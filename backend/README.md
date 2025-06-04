# Multi-Agent AI System Backend

A comprehensive AI agent system featuring two sophisticated agents: an AI Research Assistant with web search capabilities and a Multi-Modal Content Moderator for safety and policy compliance. Built with FastAPI and OpenAI's latest models.

## 🤖 **AI Agents Overview**

### 1. 🔍 **AI Research Assistant**

Advanced research agent with LLM-based validation and web search capabilities.

**Key Features:**

- **Web Search Integration:** Real-time web search using OpenAI's `gpt-4o-search-preview`
- **Advanced LLM Validation:** Sophisticated prompt injection and harmful content detection
- **Multi-Step Reasoning:** Transparent step-by-step research process
- **Citation Management:** Automatic source extraction and referencing
- **Geographic Search:** Location-aware search results
- **Safety & Security:** Input sanitization, content moderation, and output filtering

### 2. 🛡️ **Multi-Modal Content Moderator**

Comprehensive content safety analyzer for both images and text.

**Key Features:**

- **Image Analysis:** NSFW detection, violence detection, hate symbols identification
- **OCR Text Extraction:** Extract and analyze text from images
- **Text Analysis:** Toxicity, hate speech, harassment, and PII detection
- **Multi-Modal Processing:** Combined analysis of images and text
- **PII Detection & Redaction:** Automatic detection and masking of personal information
- **Batch Processing:** Efficient analysis of multiple content items
- **File Upload Support:** Direct image file upload and analysis

## 🚀 **Quick Start**

### Prerequisites

- Python 3.12+
- OpenAI API key with access to:
  - `gpt-4o-search-preview` (for research)
  - `gpt-4o-mini` (for analysis and moderation)
  - `omni-moderation-latest` (for content moderation)

### Installation

1. **Setup Environment:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Install Dependencies:**

```bash
uv sync
# or
pip install -e .
```

3. **Configure API Key:**

```bash
# Windows PowerShell
$env:OPENAI_API_KEY = "your-openai-api-key-here"

# Linux/Mac
export OPENAI_API_KEY="your-openai-api-key-here"
```

4. **Test the System:**

```bash
python test_simple.py
```

5. **Start the Server:**

```bash
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 📖 **API Documentation**

Once running:

- **Interactive Docs:** http://localhost:8000/swagger
- **Research Health:** http://localhost:8000/research/health
- **Moderation Health:** http://localhost:8000/moderation/health

## 🔍 **Research Agent API**

### Core Endpoints

**Advanced Research Query:**

```bash
POST /research/query
```

**Example Request:**

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

**Quick Search:**

```bash
POST /research/quick-search?query=your-query&context_size=low
```

**Query Validation:**

```bash
POST /research/validate-query
```

**Batch Processing:**

```bash
POST /research/batch-queries
```

### Security Features

The research agent includes advanced security measures:

- **LLM-Based Input Validation:** Detects prompt injections, harmful requests, and manipulation attempts
- **Contextual Content Moderation:** Evaluates search results for safety and appropriateness
- **Query Sanitization:** Automatically cleans malicious input while preserving intent
- **Multi-Layer Security:** Combines keyword detection, pattern matching, and AI analysis

## 🛡️ **Content Moderation API**

### Core Endpoints

**Content Analysis:**

```bash
POST /moderation/analyze
```

**Example Request:**

```json
{
  "text": "This is some text to analyze for safety",
  "image_url": "https://example.com/image.jpg",
  "strict_mode": false,
  "check_categories": [
    "nsfw",
    "violence",
    "hate",
    "toxicity",
    "harassment",
    "pii"
  ]
}
```

**File Upload Analysis:**

```bash
POST /moderation/analyze-upload
```

**Batch Analysis:**

```bash
POST /moderation/batch-analyze
```

**Quick Safety Check:**

```bash
POST /moderation/quick-check
```

### Violation Categories

| Category         | Description                              | Applies To |
| ---------------- | ---------------------------------------- | ---------- |
| **NSFW**         | Nudity, sexual content, suggestive poses | Images     |
| **Violence**     | Blood, weapons, fighting, gore           | Images     |
| **Hate Symbols** | Nazi symbols, extremist imagery          | Images     |
| **Toxicity**     | Offensive, rude language                 | Text       |
| **Hate Speech**  | Identity-based targeting                 | Text       |
| **Harassment**   | Threats, intimidation, bullying          | Text       |
| **PII**          | Phone numbers, emails, addresses, SSNs   | Text       |

### Risk Levels

- **LOW:** Content is safe with minimal violations
- **MEDIUM:** Minor violations, context-dependent
- **HIGH:** Significant violations, should be reviewed
- **CRITICAL:** Severe violations, should be blocked

## 🧪 **Testing & Examples**

### Comprehensive Test Suites

**Research Agent Tests:**

```bash
python src/test_llm_validation.py
```

**Content Moderation Tests:**

```bash
python test_content_moderation.py
```

**Simple System Test:**

```bash
python test_simple.py
```

### Example API Calls

**Research Example:**

```bash
curl -X POST "http://localhost:8000/research/query" \
     -H "Content-Type: application/json" \
     -d '{
       "query": "What are the latest developments in quantum computing?",
       "context_size": "high"
     }'
```

**Content Moderation Example:**

```bash
curl -X POST "http://localhost:8000/moderation/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Check out this image!",
       "image_url": "https://example.com/image.jpg"
     }'
```

**File Upload Example:**

```bash
curl -X POST "http://localhost:8000/moderation/analyze-upload" \
     -F "file=@image.jpg" \
     -F "text=Optional caption text" \
     -F "strict_mode=false"
```

## 🏗️ **Architecture**

### System Components

```
AI Agent System
├── Research Agent
│   ├── LLM Input Validation
│   ├── Query Analysis & Planning
│   ├── Web Search Execution
│   ├── Citation Extraction
│   ├── Content Moderation
│   └── Answer Synthesis
├── Content Moderation Agent
│   ├── Input Validation
│   ├── Image Analysis (Vision API)
│   ├── OCR Text Extraction
│   ├── Text Analysis
│   ├── OpenAI Moderation
│   └── Result Aggregation
└── Shared Infrastructure
    ├── FastAPI Server
    ├── Pydantic Models
    ├── Error Handling
    └── Logging
```

### Models Used

| Purpose                | Model                    | Usage                            |
| ---------------------- | ------------------------ | -------------------------------- |
| **Web Search**         | `gpt-4o-search-preview`  | Real-time web search             |
| **Vision Analysis**    | `gpt-4o-mini`            | Image content analysis           |
| **Text Analysis**      | `gpt-4o-mini`            | Validation, reasoning, synthesis |
| **Content Moderation** | `omni-moderation-latest` | Safety validation                |

## ⚙️ **Configuration**

### Environment Variables

```env
# Required
OPENAI_API_KEY=your-openai-api-key-here

# Optional
ANTHROPIC_API_KEY=your-anthropic-key
GROQ_API_KEY=your-groq-key
MODE=development
```

### Search Context Sizes

- **Low:** Fastest, ~50 tokens context
- **Medium:** Balanced, ~200 tokens context
- **High:** Comprehensive, ~500 tokens context

### Processing Limits

- **Research Agent:** Max 10 reasoning steps, 1000 char queries
- **Content Moderation:** Max 20 batch items, 50MB images
- **API Rate Limits:** Automatic delays and throttling

## 🔒 **Security Features**

### Research Agent Security

1. **Advanced Input Validation:** LLM-powered detection of:

   - Prompt injection attempts
   - System manipulation requests
   - Harmful content requests
   - Social engineering attempts

2. **Content Safety:** Multi-layer moderation of:

   - Search results
   - Generated responses
   - Citation content
   - User inputs

3. **Query Sanitization:** Automatic cleaning while preserving intent

### Content Moderation Security

1. **Robust Detection:** Multi-modal analysis for:

   - Visual content violations
   - Text-based violations
   - Hidden text in images
   - PII exposure

2. **Evasion Protection:** Defense against:
   - Obfuscated harmful content
   - Blurred or modified images
   - Text manipulation techniques
   - Multi-modal attack vectors

## 📊 **Performance & Monitoring**

### Performance Metrics

- **Research Agent:** ~8-15 seconds for comprehensive analysis
- **Content Moderation:** ~3-8 seconds for multi-modal analysis
- **Batch Processing:** Optimized for throughput vs. latency
- **Memory Usage:** Efficient processing with minimal memory footprint

### Monitoring Features

- Detailed processing step logs
- Performance timing metrics
- Error rate tracking
- Safety decision transparency
- Resource usage monitoring

## 🚀 **Production Deployment**

### Docker Support

```bash
docker build -t ai-agent-system .
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key ai-agent-system
```

### Scaling Considerations

- **Horizontal Scaling:** Stateless design supports multiple instances
- **Rate Limiting:** Built-in protection against API abuse
- **Caching:** Response caching for frequently requested content
- **Load Balancing:** Compatible with standard load balancers

## 🛠️ **Development**

### Code Quality

```bash
# Code formatting
black src/
flake8 src/
mypy src/

# Testing
pytest tests/
python test_simple.py
```

### Development Server

```bash
uvicorn src.main:app --reload --log-level debug
```

## 📝 **API Response Examples**

### Research Agent Response

```json
{
  "query": "Latest developments in AI",
  "answer": "Based on recent research...",
  "citations": [
    {
      "url": "https://example.com/ai-report",
      "title": "2024 AI Report",
      "start_index": 150,
      "end_index": 200
    }
  ],
  "reasoning_steps": [
    {
      "step_number": 1,
      "action": "llm_input_validation",
      "description": "Advanced input validation completed",
      "result": "SAFE: Query analyzed for legitimate research intent"
    }
  ],
  "safety_check_passed": true,
  "processing_time": 12.45
}
```

### Content Moderation Response

```json
{
  "is_safe": false,
  "overall_risk_level": "HIGH",
  "summary": "🚫 Content is NOT SAFE: Detected violations in toxicity, pii",
  "rationale": "Content contains offensive language and personal information",
  "image_analysis": {
    "has_nsfw": false,
    "has_violence": false,
    "has_hate_symbols": false,
    "extracted_text": "Contact me at john@example.com"
  },
  "text_analysis": {
    "has_toxicity": true,
    "has_pii": true,
    "cleaned_text": "Contact me at [EMAIL_REDACTED]"
  },
  "violations_found": [
    {
      "category": "toxicity",
      "detected": true,
      "confidence": 0.85,
      "description": "Offensive language detected"
    }
  ],
  "processing_time": 5.23
}
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Ensure all tests pass
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License.

---

## 🎯 **Key Advantages**

✅ **Dual-Agent Architecture:** Specialized agents for different use cases  
✅ **Advanced Security:** Multi-layer protection and validation  
✅ **Multi-Modal Capabilities:** Handle text, images, and combined content  
✅ **Transparent Processing:** Full visibility into decision-making  
✅ **Production Ready:** Comprehensive error handling and monitoring  
✅ **Scalable Design:** Stateless architecture for easy scaling  
✅ **Extensive Testing:** Comprehensive test suites for reliability

Perfect for applications requiring both intelligent research capabilities and robust content safety measures!
