from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import asyncio
import logging
import base64
import io
from PIL import Image
import time

from agents import (
    ContentModerator, 
    ModerationRequest, 
    ModerationResponse, 
    BatchModerationRequest, 
    BatchModerationResponse
)
from responses import JSONResponse as CustomJSONResponse

logger = logging.getLogger(__name__)

moderation_router = APIRouter(
    prefix="/moderation",
    tags=["Content Moderation"],
    responses={404: {"description": "Not found"}},
)

# Initialize the content moderator
content_moderator = ContentModerator()


@moderation_router.post(
    "/analyze",
    response_model=ModerationResponse,
    summary="Analyze Content for Policy Violations",
    description="""
    Analyze text and/or image content for safety and policy compliance.
    
    **Capabilities:**
    - **Image Analysis**: NSFW detection, violence detection, hate symbols, OCR text extraction
    - **Text Analysis**: Toxicity, hate speech, harassment, PII detection and redaction
    - **Multi-Modal**: Combines analysis from both image and text content
    - **Detailed Reports**: Provides confidence scores, violation categories, and reasoning
    
    **Safety Categories Checked:**
    - NSFW/Adult content
    - Violence and gore
    - Hate symbols and extremist content
    - Toxicity and offensive language
    - Harassment and threats
    - Personal Identifiable Information (PII)
    
    **Response Format:**
    Returns detailed analysis with safety assessment, risk level, violations found, and rationale.
    """
)
async def analyze_content(request: ModerationRequest) -> ModerationResponse:
    """
    Main content moderation endpoint for analyzing text and/or image content.
    
    Performs comprehensive multi-modal analysis including:
    - Image content analysis using OpenAI Vision API
    - OCR text extraction from images
    - Text toxicity and hate speech detection
    - PII detection and redaction
    - Combined safety assessment with detailed reasoning
    """
    try:
        logger.info(f"Processing content moderation request...")
        
        # Log request details (without sensitive content)
        content_types = []
        if request.text:
            content_types.append(f"text({len(request.text)} chars)")
        if request.image_url:
            content_types.append("image(url)")
        if request.image_base64:
            content_types.append("image(base64)")
        
        logger.info(f"Content types: {', '.join(content_types)}")
        logger.info(f"Strict mode: {request.strict_mode}")
        
        # Perform the moderation
        response = await content_moderator.moderate_content(request)
        
        logger.info(f"Moderation completed in {response.processing_time:.2f} seconds")
        logger.info(f"Safety result: {'SAFE' if response.is_safe else 'UNSAFE'} ({response.overall_risk_level})")
        logger.info(f"Violations: {', '.join(response.violation_categories) if response.violation_categories else 'None'}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing content moderation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while analyzing content: {str(e)}"
        )


@moderation_router.post(
    "/batch-analyze",
    response_model=BatchModerationResponse,
    summary="Batch Content Analysis",
    description="Analyze multiple content items in a single request for efficiency."
)
async def batch_analyze_content(request: BatchModerationRequest) -> BatchModerationResponse:
    """
    Analyze multiple content items in batch for efficiency.
    
    Processes up to 20 items per batch. Can process in parallel or sequential mode.
    Each item gets full moderation analysis with individual results.
    """
    try:
        if not request.items:
            raise HTTPException(status_code=400, detail="No items provided for batch analysis")
        
        if len(request.items) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 items per batch")
        
        logger.info(f"Processing batch moderation: {len(request.items)} items")
        start_time = time.time()
        
        results = []
        
        if request.parallel_processing and len(request.items) <= 5:
            # Parallel processing for small batches
            tasks = [content_moderator.moderate_content(item) for item in request.items]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions in results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error in batch item {i+1}: {str(result)}")
                    # Create error response
                    results[i] = content_moderator._create_error_response(
                        f"Batch processing error: {str(result)}",
                        [],
                        0.0
                    )
        else:
            # Sequential processing for larger batches or when requested
            for i, item in enumerate(request.items):
                try:
                    logger.info(f"Processing batch item {i+1}/{len(request.items)}")
                    result = await content_moderator.moderate_content(item)
                    results.append(result)
                    
                    # Small delay between items to respect rate limits
                    if i < len(request.items) - 1:
                        await asyncio.sleep(0.1)
                        
                except Exception as e:
                    logger.error(f"Error processing batch item {i+1}: {str(e)}")
                    error_response = content_moderator._create_error_response(
                        f"Item {i+1} processing error: {str(e)}",
                        [],
                        0.0
                    )
                    results.append(error_response)
        
        # Calculate summary statistics
        safe_count = sum(1 for r in results if r.is_safe)
        unsafe_count = len(results) - safe_count
        
        # Aggregate violation categories
        all_violations = {}
        for result in results:
            for category in result.violation_categories:
                all_violations[category] = all_violations.get(category, 0) + 1
        
        processing_time = time.time() - start_time
        
        logger.info(f"Batch moderation completed: {safe_count} safe, {unsafe_count} unsafe")
        
        return BatchModerationResponse(
            results=results,
            summary_stats={
                "total_items": len(results),
                "safe_items": safe_count,
                "unsafe_items": unsafe_count,
                **all_violations
            },
            overall_safe_count=safe_count,
            overall_unsafe_count=unsafe_count,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch moderation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during batch processing: {str(e)}"
        )


@moderation_router.get(
    "/health",
    summary="Content Moderation Health Check",
    description="Check if the content moderation service is healthy and operational."
)
async def moderation_health_check() -> Dict[str, Any]:
    """Health check endpoint for the content moderation service."""
    try:
        # Check if OpenAI client is accessible
        client_status = "healthy" if content_moderator.client else "unhealthy"
        
        # Check if API key is configured
        api_key_status = "configured" if content_moderator.settings.openai_api_key else "missing"
        
        return {
            "status": "healthy",
            "service": "content_moderation",
            "client_status": client_status,
            "api_key_status": api_key_status,
            "models": {
                "vision_model": content_moderator.vision_model,
                "text_model": content_moderator.text_model,
                "moderation_model": content_moderator.moderation_model
            },
            "capabilities": {
                "image_analysis": True,
                "text_analysis": True,
                "ocr_extraction": True,
                "pii_detection": True,
                "batch_processing": True,
                "file_upload": True
            },
            "supported_formats": ["PNG", "JPEG", "WEBP", "GIF"],
            "max_file_size": "50MB",
            "max_batch_size": 20,
            "message": "Content moderation service is operational"
        }
        
    except Exception as e:
        logger.error(f"Content moderation health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Content moderation health check failed: {str(e)}"
        )


@moderation_router.get(
    "/categories",
    summary="Get Violation Categories",
    description="Get list of all violation categories that the system can detect."
)
async def get_violation_categories() -> Dict[str, Any]:
    """Get information about violation categories and detection capabilities."""
    return {
        "violation_categories": {
            "nsfw": {
                "name": "NSFW/Adult Content",
                "description": "Nudity, sexual content, suggestive poses",
                "applies_to": ["images"]
            },
            "violence": {
                "name": "Violence",
                "description": "Blood, weapons, fighting, gore, harm to people/animals",
                "applies_to": ["images"]
            },
            "hate_symbols": {
                "name": "Hate Symbols",
                "description": "Nazi symbols, confederate flags, gang signs, extremist imagery",
                "applies_to": ["images"]
            },
            "toxicity": {
                "name": "Toxicity",
                "description": "Offensive, rude, or disrespectful language",
                "applies_to": ["text"]
            },
            "hate_speech": {
                "name": "Hate Speech",
                "description": "Content targeting individuals/groups based on identity",
                "applies_to": ["text"]
            },
            "harassment": {
                "name": "Harassment",
                "description": "Threats, intimidation, stalking, bullying",
                "applies_to": ["text"]
            },
            "pii": {
                "name": "Personal Information",
                "description": "Phone numbers, emails, addresses, SSNs, credit cards",
                "applies_to": ["text"]
            }
        },
        "risk_levels": {
            "LOW": "Content is safe with minimal or no violations",
            "MEDIUM": "Content has minor violations but may be acceptable in context",
            "HIGH": "Content has significant violations and should be reviewed",
            "CRITICAL": "Content has severe violations and should be blocked"
        },
        "pii_types": [
            "phone", "email", "ssn", "credit_card", "ip_address", "address"
        ]
    }


@moderation_router.post(
    "/quick-check",
    summary="Quick Content Safety Check",
    description="Fast safety check with basic analysis for high-volume scenarios."
)
async def quick_safety_check(
    text: Optional[str] = None,
    image_url: Optional[str] = None,
    strict_mode: bool = False
) -> Dict[str, Any]:
    """
    Quick safety check for high-volume scenarios.
    
    Provides faster analysis with basic safety assessment.
    Use for preliminary filtering before full analysis.
    """
    try:
        if not text and not image_url:
            raise HTTPException(status_code=400, detail="Either text or image_url must be provided")
        
        # Create simplified request
        request = ModerationRequest(
            text=text,
            image_url=image_url,
            strict_mode=strict_mode,
            check_categories=["nsfw", "violence", "toxicity", "hate_speech"]  # Reduced set for speed
        )
        
        # Perform quick analysis
        response = await content_moderator.moderate_content(request)
        
        return {
            "is_safe": response.is_safe,
            "risk_level": response.overall_risk_level,
            "summary": response.summary,
            "violation_categories": response.violation_categories,
            "confidence": max([v.confidence for v in response.violations_found if v.detected], default=0.0),
            "processing_time": response.processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in quick safety check: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during quick safety check: {str(e)}"
        ) 