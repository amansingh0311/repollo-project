#!/usr/bin/env python3
"""
Server startup script for the AI Agent System

This script starts the FastAPI server with both the Research Agent and Content Moderation Agent.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.absolute()
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))


def main():
    """Start the AI Agent System server."""
    print("🚀 Starting AI Agent System Server")
    print("=" * 50)
    print("Available agents:")
    print("  🔍 Research Agent - AI Research Assistant with web search")
    print("  🛡️ Content Moderation Agent - Multi-modal content safety analyzer")
    print()
    print("Server will be available at:")
    print("  🌐 API: http://localhost:8000")
    print("  📖 Docs: http://localhost:8000/swagger")
    print("  🔬 Research: http://localhost:8000/research/health")
    print("  🛡️ Moderation: http://localhost:8000/moderation/health")
    print()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ Warning: OPENAI_API_KEY environment variable not set!")
        print("   Please set it before using the agents:")
        print("   Windows: $env:OPENAI_API_KEY = 'your-key-here'")
        print("   Linux/Mac: export OPENAI_API_KEY='your-key-here'")
        print()
    
    print("Starting server... Press Ctrl+C to stop")
    print("-" * 50)
    
    # Start the server
    try:
        uvicorn.run(
            "src.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {str(e)}")


if __name__ == "__main__":
    main() 