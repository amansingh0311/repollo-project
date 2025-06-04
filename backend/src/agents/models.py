from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


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