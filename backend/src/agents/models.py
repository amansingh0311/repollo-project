from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
import base64


class Citation(BaseModel):
    """Represents a citation source from web search results."""
    url: str = Field(..., description="URL of the cited source")
    title: str = Field(..., description="Title of the cited source")
    start_index: int = Field(..., description="Start index of citation in text")
    end_index: int = Field(..., description="End index of citation in text")


class ReasoningStep(BaseModel):
    """Represents a step in the agent's reasoning process."""
    step_number: int = Field(..., description="Sequential step number")
    action: str = Field(..., description="Action taken in this step")
    description: str = Field(..., description="Description of what was done")
    query: Optional[str] = Field(None, description="Search query if applicable")
    result: Optional[str] = Field(None, description="Result or findings from this step")
    timestamp: datetime = Field(default_factory=datetime.now)


class ResearchRequest(BaseModel):
    """Request model for research queries."""
    query: str = Field(..., description="User's research question or query", min_length=1, max_length=1000)
    context_size: Optional[str] = Field(
        default="medium", 
        description="Search context size (low, medium, high)",
        pattern="^(low|medium|high)$"
    )
    user_location: Optional[Dict[str, Any]] = Field(
        None, 
        description="User location for geographically relevant results"
    )
    max_reasoning_steps: Optional[int] = Field(
        default=5, 
        description="Maximum number of reasoning steps",
        ge=1,
        le=10
    )


class ResearchResponse(BaseModel):
    """Response model for research results."""
    query: str = Field(..., description="Original user query")
    answer: str = Field(..., description="Synthesized answer from research")
    citations: List[Citation] = Field(default_factory=list, description="List of cited sources")
    reasoning_steps: List[ReasoningStep] = Field(default_factory=list, description="Agent's reasoning process")
    safety_check_passed: bool = Field(..., description="Whether the response passed safety checks")
    content_moderation_flags: Optional[Dict[str, Any]] = Field(
        None, 
        description="Content moderation results if any flags were raised"
    )
    processing_time: float = Field(..., description="Time taken to process the request in seconds")
    timestamp: datetime = Field(default_factory=datetime.now)


class ModerationResult(BaseModel):
    """Model for content moderation results."""
    flagged: bool = Field(..., description="Whether content was flagged")
    categories: Dict[str, bool] = Field(..., description="Moderation categories")
    category_scores: Dict[str, float] = Field(..., description="Confidence scores for categories")


# NEW MODELS FOR CONTENT MODERATION AGENT

class ViolationCategory(BaseModel):
    """Represents a specific violation category with details."""
    category: str = Field(..., description="Name of the violation category")
    detected: bool = Field(..., description="Whether this category was detected")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)", ge=0.0, le=1.0)
    description: str = Field(..., description="Description of what was detected")
    evidence: Optional[List[str]] = Field(default_factory=list, description="Specific evidence found")


class ImageAnalysisResult(BaseModel):
    """Results from image content analysis."""
    has_nsfw: bool = Field(..., description="Whether NSFW content was detected")
    has_violence: bool = Field(..., description="Whether violent content was detected") 
    has_hate_symbols: bool = Field(..., description="Whether hate symbols were detected")
    extracted_text: Optional[str] = Field(None, description="Text extracted via OCR")
    violations: List[ViolationCategory] = Field(default_factory=list, description="Detailed violation analysis")
    confidence_scores: Dict[str, float] = Field(default_factory=dict, description="Raw confidence scores")
    processing_notes: Optional[str] = Field(None, description="Notes about image processing")


class TextAnalysisResult(BaseModel):
    """Results from text content analysis."""
    has_toxicity: bool = Field(..., description="Whether toxic content was detected")
    has_hate_speech: bool = Field(..., description="Whether hate speech was detected")
    has_harassment: bool = Field(..., description="Whether harassment was detected")
    has_pii: bool = Field(..., description="Whether PII was detected")
    violations: List[ViolationCategory] = Field(default_factory=list, description="Detailed violation analysis")
    detected_pii: List[str] = Field(default_factory=list, description="Types of PII detected")
    confidence_scores: Dict[str, float] = Field(default_factory=dict, description="Raw confidence scores")
    cleaned_text: Optional[str] = Field(None, description="Text with PII redacted")


class ModerationRequest(BaseModel):
    """Request model for content moderation."""
    text: Optional[str] = Field(None, description="Text content to moderate", max_length=10000)
    image_url: Optional[str] = Field(None, description="URL of image to analyze")
    image_base64: Optional[str] = Field(None, description="Base64 encoded image data")
    image_filename: Optional[str] = Field(None, description="Original filename of uploaded image")
    context: Optional[str] = Field(None, description="Additional context about the content")
    strict_mode: bool = Field(default=False, description="Whether to use strict moderation rules")
    check_categories: List[str] = Field(
        default_factory=lambda: ["nsfw", "violence", "hate", "toxicity", "harassment", "pii"],
        description="Categories to check for violations"
    )


class ModerationResponse(BaseModel):
    """Response model for content moderation results."""
    is_safe: bool = Field(..., description="Overall safety assessment")
    overall_risk_level: str = Field(..., description="Risk level: LOW, MEDIUM, HIGH, CRITICAL")
    summary: str = Field(..., description="Human-readable summary of findings")
    rationale: str = Field(..., description="Detailed explanation of the decision")
    
    # Detailed analysis results
    image_analysis: Optional[ImageAnalysisResult] = Field(None, description="Image analysis results")
    text_analysis: Optional[TextAnalysisResult] = Field(None, description="Text analysis results")
    
    # Combined violations
    violations_found: List[ViolationCategory] = Field(default_factory=list, description="All violations detected")
    violation_categories: List[str] = Field(default_factory=list, description="Names of violated categories")
    
    # Processing metadata
    processing_steps: List[ReasoningStep] = Field(default_factory=list, description="Analysis steps taken")
    processing_time: float = Field(..., description="Time taken to process in seconds")
    content_types_analyzed: List[str] = Field(default_factory=list, description="Types of content analyzed")
    timestamp: datetime = Field(default_factory=datetime.now)


class BatchModerationRequest(BaseModel):
    """Request for batch content moderation."""
    items: List[ModerationRequest] = Field(..., description="List of content items to moderate", max_items=20)
    strict_mode: bool = Field(default=False, description="Whether to use strict moderation for all items")
    parallel_processing: bool = Field(default=True, description="Whether to process items in parallel")


class BatchModerationResponse(BaseModel):
    """Response for batch content moderation."""
    results: List[ModerationResponse] = Field(..., description="Individual moderation results")
    summary_stats: Dict[str, int] = Field(..., description="Summary statistics")
    overall_safe_count: int = Field(..., description="Number of items deemed safe")
    overall_unsafe_count: int = Field(..., description="Number of items deemed unsafe")
    processing_time: float = Field(..., description="Total processing time")
    timestamp: datetime = Field(default_factory=datetime.now)


class PIIDetectionResult(BaseModel):
    """Results from PII detection analysis."""
    has_pii: bool = Field(..., description="Whether PII was detected")
    pii_types: List[str] = Field(default_factory=list, description="Types of PII detected")
    confidence: float = Field(..., description="Overall confidence in PII detection")
    redacted_text: str = Field(..., description="Text with PII redacted/masked")
    pii_locations: List[Dict[str, Any]] = Field(default_factory=list, description="Locations and types of PII found") 