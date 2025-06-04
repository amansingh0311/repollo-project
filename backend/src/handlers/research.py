from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import asyncio
import logging

from agents import ResearchAgent, ResearchRequest, ResearchResponse
from responses import JSONResponse as CustomJSONResponse

logger = logging.getLogger(__name__)

research_router = APIRouter(
    prefix="/research",
    tags=["AI Research Assistant"],
    responses={404: {"description": "Not found"}},
)

# Initialize the research agent
research_agent = ResearchAgent()


@research_router.post(
    "/query",
    response_model=ResearchResponse,
    summary="Advanced Research Query",
    description="""
    Submit a research query to the AI Research Assistant with advanced safety and validation features.
    
    **Enhanced Features:**
    - Advanced LLM-based input validation and prompt injection detection
    - Contextual content moderation and safety analysis
    - Multi-step reasoning with full transparency
    - Automatic query sanitization when possible
    - Comprehensive citation extraction
    
    **Safety Measures:**
    - Sophisticated harmful content detection
    - Prompt injection protection
    - Personal information request filtering
    - Misinformation attempt detection
    - System manipulation prevention
    
    The agent will provide detailed reasoning steps showing how it processed your query.
    """
)
async def research_query(request: ResearchRequest) -> ResearchResponse:
    """
    Main research endpoint with advanced LLM-based safety and validation.
    
    The agent performs the following steps:
    1. **Advanced LLM Input Validation**: Analyzes query for safety, prompt injections, and harmful intent
    2. **Query Analysis**: Understands research requirements and breaks down complex queries
    3. **Web Search**: Performs comprehensive search using OpenAI's latest search models
    4. **Citation Extraction**: Automatically extracts and formats source citations
    5. **Contextual Content Moderation**: Evaluates results for safety and appropriateness
    6. **Answer Synthesis**: Creates a polished, comprehensive response
    
    Returns detailed research response with citations, reasoning steps, and safety assessments.
    """
    try:
        logger.info(f"Processing advanced research query: {request.query[:100]}...")
        
        # Perform the research with enhanced validation
        response = await research_agent.research(request)
        
        logger.info(f"Research completed in {response.processing_time:.2f} seconds")
        logger.info(f"Safety check passed: {response.safety_check_passed}")
        logger.info(f"Reasoning steps: {len(response.reasoning_steps)}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing research query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your research query: {str(e)}"
        )


@research_router.get(
    "/health",
    summary="Health Check",
    description="Check if the research agent is healthy and operational with all advanced features."
)
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for the research agent."""
    try:
        # Verify OpenAI client and models are accessible
        agent_status = "healthy" if research_agent.client else "unhealthy"
        
        # Check if API key is configured
        api_key_status = "configured" if research_agent.settings.openai_api_key else "missing"
        
        return {
            "status": "healthy",
            "agent_status": agent_status,
            "api_key_status": api_key_status,
            "search_model": research_agent.search_model,
            "moderation_model": research_agent.moderation_model,
            "validation_model": research_agent.validation_model,
            "features": {
                "llm_input_validation": True,
                "prompt_injection_detection": True,
                "contextual_moderation": True,
                "advanced_sanitization": True,
                "multi_step_reasoning": True,
                "automatic_citation": True
            },
            "message": "Advanced AI Research Assistant is operational"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Research agent health check failed: {str(e)}"
        )


@research_router.post(
    "/quick-search",
    response_model=Dict[str, Any],
    summary="Quick Search with Basic Validation",
    description="Perform a quick web search with basic safety checks for faster results."
)
async def quick_search(query: str, context_size: str = "low") -> Dict[str, Any]:
    """
    Quick search endpoint for faster, simpler queries with basic validation.
    
    This endpoint uses basic validation instead of full LLM analysis for speed,
    but still provides web search capabilities and essential safety checks.
    """
    try:
        if not query or len(query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        if len(query) > 500:
            raise HTTPException(status_code=400, detail="Query too long (max 500 characters)")
        
        logger.info(f"Processing quick search: {query[:100]}...")
        
        # Create a simplified request
        request = ResearchRequest(
            query=query.strip(),
            context_size=context_size,
            max_reasoning_steps=3
        )
        
        # Perform basic validation using fallback method
        validation_step = await research_agent._basic_validate_and_sanitize_input(query)
        
        if "REJECTED" in validation_step.result:
            return {
                "query": query,
                "answer": "I cannot process this request as it may involve harmful or inappropriate content.",
                "safe": False,
                "reasoning": validation_step.result,
                "validation_method": "basic"
            }
        
        # Perform web search
        search_step = await research_agent._perform_web_search(request)
        
        if "error" in search_step.result.lower():
            raise HTTPException(status_code=503, detail="Web search service temporarily unavailable")
        
        # Basic content moderation using OpenAI API only
        try:
            moderation_response = research_agent.client.moderations.create(
                model=research_agent.moderation_model,
                input=search_step.result
            )
            safe = not moderation_response.results[0].flagged
        except:
            safe = True  # Default to safe if moderation fails
        
        if not safe:
            return {
                "query": query,
                "answer": "I apologize, but I cannot provide a response to this query due to safety concerns.",
                "safe": False,
                "reasoning": "Content failed basic safety moderation",
                "validation_method": "basic"
            }
        
        return {
            "query": query,
            "answer": search_step.result,
            "safe": safe,
            "context_size": context_size,
            "reasoning": "Quick search completed successfully",
            "validation_method": "basic"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in quick search: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during quick search: {str(e)}"
        )


@research_router.get(
    "/models",
    summary="Available Models & Features",
    description="Get information about the AI models and advanced features used by the research agent."
)
async def get_models() -> Dict[str, Any]:
    """Get information about the models and features used by the research agent."""
    return {
        "models": {
            "search_model": research_agent.search_model,
            "moderation_model": research_agent.moderation_model,
            "validation_model": research_agent.validation_model
        },
        "advanced_features": {
            "llm_input_validation": {
                "enabled": True,
                "description": "Uses LLM to analyze queries for safety and prompt injection attempts",
                "categories": list(research_agent.safety_categories.keys())
            },
            "contextual_moderation": {
                "enabled": True,
                "description": "Evaluates content safety in context of original query"
            },
            "query_sanitization": {
                "enabled": True,
                "description": "Automatically cleans and improves queries when possible"
            },
            "multi_step_reasoning": {
                "enabled": True,
                "description": "Transparent step-by-step reasoning process"
            },
            "citation_extraction": {
                "enabled": True,
                "description": "Automatic extraction and formatting of source citations"
            }
        },
        "safety_categories": research_agent.safety_categories,
        "supported_context_sizes": ["low", "medium", "high"],
        "limits": {
            "max_query_length": 1000,
            "max_reasoning_steps": 10,
            "batch_size": 10
        }
    }


@research_router.post(
    "/validate-query",
    summary="Validate Query Safety",
    description="Test query validation without performing research - useful for checking if a query would be accepted."
)
async def validate_query(query: str, validation_type: str = "advanced") -> Dict[str, Any]:
    """
    Validate a query for safety without performing the actual research.
    
    Useful for:
    - Testing if queries will be accepted
    - Understanding validation logic
    - Debugging query issues
    - Pre-validation in applications
    """
    try:
        if validation_type == "advanced":
            validation_step = await research_agent._advanced_validate_and_sanitize_input(query)
        else:
            validation_step = await research_agent._basic_validate_and_sanitize_input(query)
        
        is_safe = "SAFE" in validation_step.result
        
        # Extract sanitized query if available
        sanitized_query = None
        if is_safe:
            sanitized_query = research_agent._extract_sanitized_query(validation_step.result)
        
        return {
            "original_query": query,
            "validation_result": validation_step.result,
            "is_safe": is_safe,
            "sanitized_query": sanitized_query or query,
            "validation_method": validation_type,
            "action": validation_step.action,
            "description": validation_step.description
        }
        
    except Exception as e:
        logger.error(f"Error validating query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while validating the query: {str(e)}"
        )


@research_router.post(
    "/batch-queries",
    response_model=List[ResearchResponse],
    summary="Batch Research Queries",
    description="Process multiple research queries in batch with advanced validation for each."
)
async def batch_research_queries(queries: List[str], context_size: str = "medium") -> List[ResearchResponse]:
    """
    Process multiple research queries in batch with full advanced validation.
    
    Each query gets the complete treatment:
    - Advanced LLM validation
    - Full reasoning process
    - Safety checks
    - Citation extraction
    
    Note: Processed sequentially to respect rate limits and ensure quality.
    """
    if not queries:
        raise HTTPException(status_code=400, detail="No queries provided")
    
    if len(queries) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 queries per batch")
    
    results = []
    
    for i, query in enumerate(queries):
        try:
            logger.info(f"Processing batch query {i+1}/{len(queries)}: {query[:50]}...")
            
            request = ResearchRequest(
                query=query,
                context_size=context_size,
                max_reasoning_steps=4  # Slightly reduced for batch processing
            )
            
            response = await research_agent.research(request)
            results.append(response)
            
            # Small delay to respect rate limits
            if i < len(queries) - 1:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error processing batch query {i+1}: {str(e)}")
            # Create error response
            error_response = ResearchResponse(
                query=query,
                answer=f"Error processing query: {str(e)}",
                reasoning_steps=[],
                safety_check_passed=False,
                processing_time=0.0
            )
            results.append(error_response)
    
    return results 