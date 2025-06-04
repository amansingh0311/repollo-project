# Repollo

<div align="center">
  <img src="frontend/public/repollo-logo.svg" alt="Repollo Platform" width="400" />
</div>

A modern platform featuring AI-powered research and content moderation agents.

## Features

- **Research Agent**: AI-powered research assistant with web search capabilities
- **Moderation Agent**: Content analysis for safety and policy compliance
- **Modern UI**: Built with Next.js and Tailwind CSS
- **Containerized Backend**: Python FastAPI backend with Docker support

## Prerequisites

- Docker and Docker Compose
- Node.js (v18 or higher)
- pnpm package manager
- Python 3.9+

## Setup

### Backend Setup

1. Create a `.env` file in the `backend` directory with the following variables:

```env
ANTHROPIC_API_KEY=your_anthropic_key
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
```

2. Build and start the backend server using Docker:

```bash
# From the root directory
docker compose build server
docker compose up -d
```

The backend server will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
pnpm install
```

3. Start the development server:

```bash
pnpm run dev
```

The frontend will be available at `http://localhost:3000`

## Project Structure

```
repollo-project/
├── backend/           # FastAPI backend
│   ├── src/          # Source code
│   └── .env          # Backend environment variables
├── frontend/         # Next.js frontend
│   ├── src/         # Source code
│   └── public/      # Static assets
└── docker-compose.yaml
```

## API Endpoints

### Research Agent

- `POST /research/query`: Submit research queries
- `GET /research/health`: Check agent health status

### Moderation Agent

- `POST /moderation/analyze`: Analyze content
- `POST /moderation/batch-analyze`: Batch content analysis
- `GET /moderation/health`: Check agent health status

## Development

- Backend API documentation is available at `http://localhost:8000/docs`
- The frontend uses Next.js 14 with App Router
- All API routes are configured to use environment variables for backend URL

## License

MIT License
