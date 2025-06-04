import time
import re
import base64
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from openai import OpenAI
import asyncio

from .models import (
    ModerationRequest,
    ModerationResponse,
    ImageAnalysisResult,
    TextAnalysisResult,
    ViolationCategory,
    ReasoningStep,
    PIIDetectionResult,
    BatchModerationRequest,
    BatchModerationResponse
)
from config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentModerator:
    """
    Multi-Modal Content Moderator Agent
    
    Analyzes images and text for safety and policy compliance including:
    - NSFW/Adult content detection
    - Violence and hate symbol detection  
    - OCR text extraction from images
    - Toxicity and hate speech detection
    - PII detection and redaction
    - Harassment and threat detection
    """
    
    def __init__(self):
        """Initialize the content moderator with OpenAI client and detection patterns."""
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self.vision_model = "gpt-4o-mini"  # For image analysis
        self.text_model = "gpt-4o-mini"   # For text analysis
        self.moderation_model = "omni-moderation-latest"  # For OpenAI moderation
        
        # Risk levels and thresholds
        self.risk_thresholds = {
            "CRITICAL": 0.9,
            "HIGH": 0.7,
            "MEDIUM": 0.4,
            "LOW": 0.0
        }
        
        # PII patterns for detection
        self.pii_patterns = {
            "phone": r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "ssn": r'\b\d{3}-?\d{2}-?\d{4}\b',
            "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            "ip_address": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            "address": r'\b\d+\s+[A-Za-z0-9\s,]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b'
        }
        
        # Toxicity keywords (basic set - in production would use more sophisticated detection)
        self.toxicity_keywords = [
            # Hate speech indicators
            "hate", "nazi", "fascist", "terrorist", "kill", "murder", "die", "death",
            # Harassment indicators  
            "stalk", "harass", "threaten", "intimidate", "bully", "abuse",
            # Profanity (selective list)
            "fuck", "shit", "damn", "bitch", "asshole", "bastard",
            # Discriminatory terms
            "retard", "retarded", "gay" # (when used pejoratively)
        ]
    
    async def moderate_content(self, request: ModerationRequest) -> ModerationResponse:
        """
        Main content moderation method that analyzes both images and text.
        
        Args:
            request: Moderation request with text and/or image content
            
        Returns:
            ModerationResponse with detailed analysis and safety assessment
        """
        start_time = time.time()
        processing_steps = []
        content_types_analyzed = []
        
        # Initialize results
        image_analysis = None
        text_analysis = None
        all_violations = []
        
        try:
            # Step 1: Validate input
            step1 = self._validate_input(request)
            processing_steps.append(step1)
            
            if "error" in step1.result.lower():
                return self._create_error_response(step1.result, processing_steps, time.time() - start_time)
            
            # Step 2: Analyze image if provided
            if request.image_url or request.image_base64:
                content_types_analyzed.append("image")
                step2 = await self._analyze_image(request)
                processing_steps.append(step2)
                
                if step2.result and "error" not in step2.result.lower():
                    image_analysis = self._parse_image_analysis(step2.result)
                    all_violations.extend(image_analysis.violations)
            
            # Step 3: Analyze text (either provided directly or extracted from image)
            text_to_analyze = request.text
            
            # If we extracted text from image, include it
            if image_analysis and image_analysis.extracted_text:
                if text_to_analyze:
                    text_to_analyze += "\n\n" + image_analysis.extracted_text
                else:
                    text_to_analyze = image_analysis.extracted_text
            
            if text_to_analyze:
                content_types_analyzed.append("text")
                step3 = await self._analyze_text(text_to_analyze, request.strict_mode)
                processing_steps.append(step3)
                
                if step3.result and "error" not in step3.result.lower():
                    text_analysis = self._parse_text_analysis(step3.result, text_to_analyze)
                    all_violations.extend(text_analysis.violations)
            
            # Step 4: Apply OpenAI moderation API for additional validation
            if text_to_analyze:
                step4 = await self._apply_openai_moderation(text_to_analyze)
                processing_steps.append(step4)
                
                # Add OpenAI moderation results to violations if flagged
                if "flagged" in step4.result.lower():
                    openai_violations = self._parse_openai_moderation(step4.result)
                    all_violations.extend(openai_violations)
            
            # Step 5: Aggregate results and make final decision
            step5 = self._aggregate_results(all_violations, request.strict_mode)
            processing_steps.append(step5)
            
            # Calculate overall risk and safety
            is_safe, risk_level = self._calculate_risk_level(all_violations)
            summary, rationale = self._generate_summary_and_rationale(
                is_safe, all_violations, image_analysis, text_analysis
            )
            
            processing_time = time.time() - start_time
            
            return ModerationResponse(
                is_safe=is_safe,
                overall_risk_level=risk_level,
                summary=summary,
                rationale=rationale,
                image_analysis=image_analysis,
                text_analysis=text_analysis,
                violations_found=all_violations,
                violation_categories=[v.category for v in all_violations if v.detected],
                processing_steps=processing_steps,
                processing_time=processing_time,
                content_types_analyzed=content_types_analyzed
            )
            
        except Exception as e:
            logger.error(f"Error in content moderation: {str(e)}")
            error_step = ReasoningStep(
                step_number=len(processing_steps) + 1,
                action="error_handling",
                description="An error occurred during content moderation",
                result=f"Error: {str(e)}"
            )
            processing_steps.append(error_step)
            
            return self._create_error_response(
                f"Content moderation failed: {str(e)}", 
                processing_steps, 
                time.time() - start_time
            )
    
    def _validate_input(self, request: ModerationRequest) -> ReasoningStep:
        """Validate the moderation request input."""
        if not request.text and not request.image_url and not request.image_base64:
            return ReasoningStep(
                step_number=1,
                action="input_validation",
                description="Input validation failed",
                result="Error: No content provided for moderation"
            )
        
        # Validate image data if provided
        if request.image_base64:
            try:
                # Basic validation of base64 data
                base64.b64decode(request.image_base64)
            except Exception:
                return ReasoningStep(
                    step_number=1,
                    action="input_validation", 
                    description="Image validation failed",
                    result="Error: Invalid base64 image data"
                )
        
        return ReasoningStep(
            step_number=1,
            action="input_validation",
            description="Input validation completed successfully",
            result="Valid content provided for moderation"
        )
    
    async def _analyze_image(self, request: ModerationRequest) -> ReasoningStep:
        """Analyze image content for NSFW, violence, hate symbols, and extract text."""
        try:
            # Prepare image for OpenAI Vision API
            if request.image_base64:
                # Check if base64 string already includes data URI format
                if request.image_base64.startswith('data:image/'):
                    image_url = request.image_base64
                else:
                    image_url = f"data:image/jpeg;base64,{request.image_base64}"
            else:
                image_url = request.image_url
            
            analysis_prompt = """
            Analyze this image thoroughly for content policy violations. Check for:

            1. **NSFW/Adult Content**: Nudity, sexual content, suggestive poses
            2. **Violence**: Blood, weapons, fighting, gore, harm to people/animals  
            3. **Hate Symbols**: Nazi symbols, confederate flags, gang signs, extremist imagery
            4. **Text Content**: Extract ALL visible text using OCR capabilities
            5. **Other Violations**: Drugs, self-harm, disturbing content

            Provide your analysis in this exact format:

            NSFW_DETECTED: [YES/NO]
            NSFW_CONFIDENCE: [0.0-1.0]
            NSFW_DETAILS: [specific description]

            VIOLENCE_DETECTED: [YES/NO] 
            VIOLENCE_CONFIDENCE: [0.0-1.0]
            VIOLENCE_DETAILS: [specific description]

            HATE_SYMBOLS_DETECTED: [YES/NO]
            HATE_CONFIDENCE: [0.0-1.0] 
            HATE_DETAILS: [specific description]

            EXTRACTED_TEXT: [all visible text, or "NONE" if no text]

            OVERALL_SAFETY: [SAFE/UNSAFE]
            REASONING: [detailed explanation of findings]
            """
            
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": analysis_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url}
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            analysis_result = response.choices[0].message.content
            
            return ReasoningStep(
                step_number=2,
                action="image_analysis",
                description="Analyzed image for NSFW, violence, hate symbols, and extracted text",
                result=analysis_result
            )
            
        except Exception as e:
            logger.error(f"Image analysis error: {str(e)}")
            return ReasoningStep(
                step_number=2,
                action="image_analysis",
                description="Image analysis failed",
                result=f"Error analyzing image: {str(e)}"
            )
    
    async def _analyze_text(self, text: str, strict_mode: bool = False) -> ReasoningStep:
        """Analyze text for toxicity, hate speech, harassment, and PII."""
        try:
            strictness = "very strict" if strict_mode else "balanced"
            
            analysis_prompt = f"""
            Analyze this text content for policy violations using {strictness} standards:

            Text: "{text}"

            Check for:
            1. **Toxicity**: Offensive, rude, or disrespectful language
            2. **Hate Speech**: Content targeting individuals/groups based on identity
            3. **Harassment**: Threats, intimidation, stalking, bullying
            4. **PII**: Personal information like phone numbers, emails, addresses, SSNs
            5. **Other Violations**: Spam, misinformation, illegal content

            Provide analysis in this format:

            TOXICITY_DETECTED: [YES/NO]
            TOXICITY_CONFIDENCE: [0.0-1.0]
            TOXICITY_DETAILS: [specific examples]

            HATE_SPEECH_DETECTED: [YES/NO]
            HATE_CONFIDENCE: [0.0-1.0]
            HATE_DETAILS: [specific examples]

            HARASSMENT_DETECTED: [YES/NO]
            HARASSMENT_CONFIDENCE: [0.0-1.0]
            HARASSMENT_DETAILS: [specific examples]

            PII_DETECTED: [YES/NO]
            PII_TYPES: [list types found: phone, email, ssn, address, etc.]
            PII_DETAILS: [what was found]

            OVERALL_SAFETY: [SAFE/UNSAFE]
            REASONING: [detailed explanation]
            """
            
            response = self.client.chat.completions.create(
                model=self.text_model,
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=400,
                temperature=0.1  # Low temperature for consistent analysis
            )
            
            analysis_result = response.choices[0].message.content
            
            return ReasoningStep(
                step_number=3,
                action="text_analysis",
                description=f"Analyzed text content for violations using {strictness} standards",
                result=analysis_result
            )
            
        except Exception as e:
            logger.error(f"Text analysis error: {str(e)}")
            return ReasoningStep(
                step_number=3,
                action="text_analysis",
                description="Text analysis failed",
                result=f"Error analyzing text: {str(e)}"
            )
    
    async def _apply_openai_moderation(self, text: str) -> ReasoningStep:
        """Apply OpenAI's moderation API for additional validation."""
        try:
            response = self.client.moderations.create(
                model=self.moderation_model,
                input=text
            )
            
            result = response.results[0]
            
            if result.flagged:
                flagged_categories = [cat for cat, flagged in result.categories.model_dump().items() if flagged]
                return ReasoningStep(
                    step_number=4,
                    action="openai_moderation",
                    description="Applied OpenAI moderation API",
                    result=f"Content flagged for: {', '.join(flagged_categories)}"
                )
            else:
                return ReasoningStep(
                    step_number=4,
                    action="openai_moderation",
                    description="Applied OpenAI moderation API",
                    result="No violations detected by OpenAI moderation"
                )
                
        except Exception as e:
            logger.error(f"OpenAI moderation error: {str(e)}")
            return ReasoningStep(
                step_number=4,
                action="openai_moderation",
                description="OpenAI moderation failed",
                result=f"Error in OpenAI moderation: {str(e)}"
            )
    
    def _parse_image_analysis(self, analysis_text: str) -> ImageAnalysisResult:
        """Parse the image analysis results into structured format."""
        has_nsfw = "NSFW_DETECTED: YES" in analysis_text
        has_violence = "VIOLENCE_DETECTED: YES" in analysis_text
        has_hate_symbols = "HATE_SYMBOLS_DETECTED: YES" in analysis_text
        
        # Extract confidence scores
        nsfw_conf = self._extract_confidence(analysis_text, "NSFW_CONFIDENCE")
        violence_conf = self._extract_confidence(analysis_text, "VIOLENCE_CONFIDENCE")
        hate_conf = self._extract_confidence(analysis_text, "HATE_CONFIDENCE")
        
        # Extract text
        text_match = re.search(r'EXTRACTED_TEXT:\s*(.*?)(?:\n|$)', analysis_text, re.DOTALL)
        extracted_text = text_match.group(1).strip() if text_match else None
        if extracted_text == "NONE":
            extracted_text = None
        
        # Create violation categories
        violations = []
        if has_nsfw:
            details = self._extract_details(analysis_text, "NSFW_DETAILS")
            violations.append(ViolationCategory(
                category="nsfw",
                detected=True,
                confidence=nsfw_conf,
                description=details,
                evidence=["Visual content analysis"]
            ))
        
        if has_violence:
            details = self._extract_details(analysis_text, "VIOLENCE_DETAILS")
            violations.append(ViolationCategory(
                category="violence",
                detected=True,
                confidence=violence_conf,
                description=details,
                evidence=["Visual content analysis"]
            ))
        
        if has_hate_symbols:
            details = self._extract_details(analysis_text, "HATE_DETAILS")
            violations.append(ViolationCategory(
                category="hate_symbols",
                detected=True,
                confidence=hate_conf,
                description=details,
                evidence=["Visual content analysis"]
            ))
        
        return ImageAnalysisResult(
            has_nsfw=has_nsfw,
            has_violence=has_violence,
            has_hate_symbols=has_hate_symbols,
            extracted_text=extracted_text,
            violations=violations,
            confidence_scores={
                "nsfw": nsfw_conf,
                "violence": violence_conf,
                "hate_symbols": hate_conf
            },
            processing_notes="Analyzed using OpenAI Vision API"
        )
    
    def _parse_text_analysis(self, analysis_text: str, original_text: str) -> TextAnalysisResult:
        """Parse the text analysis results into structured format."""
        has_toxicity = "TOXICITY_DETECTED: YES" in analysis_text
        has_hate_speech = "HATE_SPEECH_DETECTED: YES" in analysis_text
        has_harassment = "HARASSMENT_DETECTED: YES" in analysis_text
        has_pii = "PII_DETECTED: YES" in analysis_text
        
        # Extract confidence scores
        toxicity_conf = self._extract_confidence(analysis_text, "TOXICITY_CONFIDENCE")
        hate_conf = self._extract_confidence(analysis_text, "HATE_CONFIDENCE")
        harassment_conf = self._extract_confidence(analysis_text, "HARASSMENT_CONFIDENCE")
        
        # Extract PII types
        pii_types = []
        pii_match = re.search(r'PII_TYPES:\s*\[(.*?)\]', analysis_text)
        if pii_match:
            pii_types = [t.strip() for t in pii_match.group(1).split(',') if t.strip()]
        
        # Create violation categories
        violations = []
        
        if has_toxicity:
            details = self._extract_details(analysis_text, "TOXICITY_DETAILS")
            violations.append(ViolationCategory(
                category="toxicity",
                detected=True,
                confidence=toxicity_conf,
                description=details,
                evidence=["Text content analysis"]
            ))
        
        if has_hate_speech:
            details = self._extract_details(analysis_text, "HATE_DETAILS")
            violations.append(ViolationCategory(
                category="hate_speech",
                detected=True,
                confidence=hate_conf,
                description=details,
                evidence=["Text content analysis"]
            ))
        
        if has_harassment:
            details = self._extract_details(analysis_text, "HARASSMENT_DETAILS")
            violations.append(ViolationCategory(
                category="harassment",
                detected=True,
                confidence=harassment_conf,
                description=details,
                evidence=["Text content analysis"]
            ))
        
        if has_pii:
            pii_details = self._extract_details(analysis_text, "PII_DETAILS")
            violations.append(ViolationCategory(
                category="pii",
                detected=True,
                confidence=0.8,  # Default for PII
                description=pii_details,
                evidence=pii_types
            ))
        
        # Redact PII from text
        cleaned_text = self._redact_pii(original_text)
        
        return TextAnalysisResult(
            has_toxicity=has_toxicity,
            has_hate_speech=has_hate_speech,
            has_harassment=has_harassment,
            has_pii=has_pii,
            violations=violations,
            detected_pii=pii_types,
            confidence_scores={
                "toxicity": toxicity_conf,
                "hate_speech": hate_conf,
                "harassment": harassment_conf
            },
            cleaned_text=cleaned_text
        )
    
    def _extract_confidence(self, text: str, field: str) -> float:
        """Extract confidence score from analysis text."""
        pattern = f"{field}:\\s*([0-9.]+)"
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return 0.0
    
    def _extract_details(self, text: str, field: str) -> str:
        """Extract details from analysis text."""
        pattern = f"{field}:\\s*(.*?)(?:\\n[A-Z_]+:|$)"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return "No details provided"
    
    def _parse_openai_moderation(self, result_text: str) -> List[ViolationCategory]:
        """Parse OpenAI moderation results into violation categories."""
        violations = []
        
        if "flagged" in result_text.lower():
            # Extract categories from the result text
            categories = re.findall(r'(\w+)', result_text)
            for category in categories:
                if category.lower() in ['harassment', 'hate', 'self-harm', 'sexual', 'violence']:
                    violations.append(ViolationCategory(
                        category=f"openai_{category.lower()}",
                        detected=True,
                        confidence=0.8,  # Default confidence for OpenAI flagged content
                        description=f"Flagged by OpenAI moderation for {category}",
                        evidence=["OpenAI Moderation API"]
                    ))
        
        return violations
    
    def _redact_pii(self, text: str) -> str:
        """Redact PII from text using regex patterns."""
        redacted_text = text
        
        for pii_type, pattern in self.pii_patterns.items():
            if pii_type == "phone":
                redacted_text = re.sub(pattern, "[PHONE_REDACTED]", redacted_text)
            elif pii_type == "email":
                redacted_text = re.sub(pattern, "[EMAIL_REDACTED]", redacted_text)
            elif pii_type == "ssn":
                redacted_text = re.sub(pattern, "[SSN_REDACTED]", redacted_text)
            elif pii_type == "credit_card":
                redacted_text = re.sub(pattern, "[CARD_REDACTED]", redacted_text)
            elif pii_type == "address":
                redacted_text = re.sub(pattern, "[ADDRESS_REDACTED]", redacted_text)
        
        return redacted_text
    
    def _aggregate_results(self, violations: List[ViolationCategory], strict_mode: bool) -> ReasoningStep:
        """Aggregate all violation results and apply decision logic."""
        violation_count = sum(1 for v in violations if v.detected)
        max_confidence = max([v.confidence for v in violations if v.detected], default=0.0)
        
        decision_logic = f"Found {violation_count} violations. Max confidence: {max_confidence:.2f}"
        if strict_mode:
            decision_logic += " (Strict mode enabled)"
        
        return ReasoningStep(
            step_number=5,
            action="result_aggregation",
            description="Aggregated all analysis results and applied decision logic",
            result=decision_logic
        )
    
    def _calculate_risk_level(self, violations: List[ViolationCategory]) -> Tuple[bool, str]:
        """Calculate overall risk level and safety assessment."""
        if not violations or not any(v.detected for v in violations):
            return True, "LOW"
        
        max_confidence = max([v.confidence for v in violations if v.detected], default=0.0)
        critical_categories = ["nsfw", "violence", "hate_speech", "harassment"]
        
        has_critical = any(v.detected and v.category in critical_categories for v in violations)
        
        if max_confidence >= self.risk_thresholds["CRITICAL"] or has_critical:
            return False, "CRITICAL"
        elif max_confidence >= self.risk_thresholds["HIGH"]:
            return False, "HIGH"
        elif max_confidence >= self.risk_thresholds["MEDIUM"]:
            return False, "MEDIUM"
        else:
            return True, "LOW"
    
    def _generate_summary_and_rationale(
        self, 
        is_safe: bool, 
        violations: List[ViolationCategory],
        image_analysis: Optional[ImageAnalysisResult],
        text_analysis: Optional[TextAnalysisResult]
    ) -> Tuple[str, str]:
        """Generate human-readable summary and detailed rationale."""
        
        if is_safe:
            summary = "✅ Content is SAFE: No significant policy violations detected."
            rationale = "The content analysis found no violations that exceed our safety thresholds. "
            
            if image_analysis:
                rationale += "Image analysis found no NSFW, violent, or hate-related content. "
            if text_analysis:
                rationale += "Text analysis found no toxicity, hate speech, or harassment. "
                
        else:
            detected_categories = [v.category for v in violations if v.detected]
            summary = f"🚫 Content is NOT SAFE: Detected violations in {', '.join(detected_categories)}"
            
            rationale = "The content analysis detected the following violations: "
            
            for violation in violations:
                if violation.detected:
                    rationale += f"\n- {violation.category.title()}: {violation.description} (confidence: {violation.confidence:.2f})"
        
        return summary, rationale
    
    def _create_error_response(
        self, 
        error_message: str, 
        processing_steps: List[ReasoningStep], 
        processing_time: float
    ) -> ModerationResponse:
        """Create an error response for failed moderation."""
        return ModerationResponse(
            is_safe=False,  # Default to unsafe on error
            overall_risk_level="HIGH",
            summary="⚠️ Content moderation failed due to processing error",
            rationale=f"Unable to complete content analysis: {error_message}",
            violations_found=[],
            violation_categories=[],
            processing_steps=processing_steps,
            processing_time=processing_time,
            content_types_analyzed=[]
        ) 