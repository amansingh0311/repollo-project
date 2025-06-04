# AI Research Assistant Backend

A sophisticated AI-powered research assistant that can answer complex queries by searching the web and synthesizing information from multiple sources. Built with FastAPI and OpenAI's latest web search capabilities.

## Features

### 🔍 **Web Search Integration**

- Uses OpenAI's `gpt-4o-search-preview` model for real-time web search
- Configurable search context size (low, medium, high)
- Geographic search customization
- Multi-source information gathering

### 🧠 **Multi-Step Reasoning**

- Step-by-step reasoning process with full transparency
- Query analysis and sub-question generation
- Information synthesis and cross-referencing
- Detailed reasoning logs for each step

### 🛡️ **Safety & Security**

- Input validation and sanitization
- Harmful content detection
- OpenAI's content moderation API integration
- Prompt injection protection
- Safe output filtering

### 📚 **Citation & Source Management**

- Automatic citation extraction from search results
- URL and title preservation
- Source credibility indicators
- Inline citation formatting

### ⚡ **Performance Optimizations**

- Async/await throughout
- Configurable reasoning depth
- Quick search option for faster responses
- Batch processing capabilities

## Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key with access to search-enabled models

### Installation

1. **Clone and setup:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install dependencies:**

```bash
uv sync
# or
pip install -e .
```

3. **Environment configuration:**

```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run the server:**

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

Create a `.env` file in the backend directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Optional: Other AI providers
ANTHROPIC_API_KEY=your-anthropic-key
GROQ_API_KEY=your-groq-key

# Application Mode
MODE=development
```

## API Documentation

Once running, visit:

- **API Docs:** http://localhost:8000/swagger
- **Health Check:** http://localhost:8000/research/health

### Core Endpoints

#### 1. Main Research Query

```bash
POST /research/query
```

**Request Body:**

```json
{
  "query": "Compare the latest electric vehicle models and their safety features",
  "context_size": "medium",
  "user_location": {
    "type": "approximate",
    "approximate": {
      "country": "US",
      "city": "San Francisco",
      "region": "California"
    }
  },
  "max_reasoning_steps": 5
}
```

**Response:**

```json
{
  "query": "Compare the latest electric vehicle models...",
  "answer": "Based on my research of current electric vehicle models...",
  "citations": [
    {
      "url": "https://example.com/ev-safety-report",
      "title": "2024 EV Safety Report",
      "start_index": 245,
      "end_index": 290
    }
  ],
  "reasoning_steps": [
    {
      "step_number": 1,
      "action": "input_validation",
      "description": "Input validation and sanitization completed",
      "result": "SAFE: Input passed safety checks"
    }
  ],
  "safety_check_passed": true,
  "processing_time": 12.45,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### 2. Quick Search

```bash
POST /research/quick-search?query=your-query&context_size=low
```

Faster endpoint with reduced reasoning steps for simple queries.

#### 3. Batch Processing

```bash
POST /research/batch-queries
```

Process multiple queries efficiently (max 10 per batch).

#### 4. Health & Status

```bash
GET /research/health
GET /research/models
```

## Usage Examples

### Basic Research Query

```python
import requests

response = requests.post(
    "http://localhost:8000/research/query",
    json={
        "query": "What are the latest developments in quantum computing?",
        "context_size": "high"
    }
)

result = response.json()
print(f"Answer: {result['answer']}")
print(f"Citations: {len(result['citations'])}")
print(f"Processing time: {result['processing_time']:.2f}s")
```

### Geographic Search

```python
requests.post(
    "http://localhost:8000/research/query",
    json={
        "query": "Best restaurants near Times Square",
        "user_location": {
            "type": "approximate",
            "approximate": {
                "country": "US",
                "city": "New York",
                "region": "New York"
            }
        }
    }
)
```

### Quick Search for Simple Queries

```python
response = requests.post(
    "http://localhost:8000/research/quick-search",
    params={
        "query": "Current weather in London",
        "context_size": "low"
    }
)
```

## Architecture

### Agent Structure

```
ResearchAgent
├── Input Validation & Sanitization
├── Query Analysis & Planning
├── Web Search Execution
├── Citation Extraction
├── Content Moderation
└── Answer Synthesis
```

### Safety Measures

1. **Input Filtering:** Harmful keyword detection
2. **Content Moderation:** OpenAI's moderation API
3. **Output Sanitization:** Safe response formatting
4. **Prompt Protection:** Injection attempt detection

### Models Used

- **Search:** `gpt-4o-search-preview` (primary web search)
- **Analysis:** `gpt-4o-mini` (query analysis & synthesis)
- **Moderation:** `omni-moderation-latest` (content safety)

## Configuration Options

### Search Context Sizes

- **Low:** Fastest, least comprehensive (~50 tokens)
- **Medium:** Balanced performance (~200 tokens)
- **High:** Most comprehensive, slower (~500 tokens)

### Reasoning Steps

- **Minimum:** 1 step (validation only)
- **Default:** 5 steps (full reasoning)
- **Maximum:** 10 steps (detailed analysis)

## Error Handling

The agent includes comprehensive error handling:

- Graceful degradation for API failures
- Detailed error logging
- User-friendly error messages
- Automatic retry mechanisms

## Rate Limits & Costs

- **Search Context:** Affects cost and latency
- **Batch Limits:** Max 10 queries per batch
- **Rate Limiting:** Built-in delays for batch processing
- **Cost Optimization:** Configurable context sizes

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
black src/
flake8 src/
mypy src/
```

### Docker

```bash
docker build -t research-agent .
docker run -p 8000:8000 research-agent
```

## Security Considerations

1. **API Keys:** Never commit API keys to version control
2. **Input Validation:** All user inputs are sanitized
3. **Content Filtering:** Automatic moderation of all outputs
4. **Rate Limiting:** Prevents abuse of external APIs
5. **Error Handling:** No sensitive information in error messages

## Troubleshooting

### Common Issues

1. **OpenAI API Key Issues:**

   - Ensure key has access to search-enabled models
   - Check API quota and billing status

2. **Search Model Unavailable:**

   - Fallback to regular models implemented
   - Check OpenAI service status

3. **Slow Response Times:**
   - Reduce context_size to 'low'
   - Limit max_reasoning_steps
   - Use quick-search endpoint

### Logs

```bash
# Check application logs
tail -f logs/research_agent.log

# Debug mode
MODE=development uvicorn src.main:app --reload --log-level debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License.
