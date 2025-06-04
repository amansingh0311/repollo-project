#!/usr/bin/env python3
"""
Setup and Test Script for AI Research Assistant

This script helps you quickly set up and test the research agent.
Run this after setting your OPENAI_API_KEY environment variable.
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 12):
        print("❌ Python 3.12+ is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def check_openai_key():
    """Check if OpenAI API key is set."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("\n📝 To set your API key:")
        print("Windows: $env:OPENAI_API_KEY='your-key-here'")
        print("Linux/Mac: export OPENAI_API_KEY='your-key-here'")
        print("\nGet your key from: https://platform.openai.com/api-keys")
        return False
    
    if len(api_key) < 20:
        print("❌ OPENAI_API_KEY seems invalid (too short)")
        return False
    
    print("✅ OpenAI API key is configured")
    return True


def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "fastapi>=0.115.12",
            "openai>=1.84.0", 
            "uvicorn>=0.34.3",
            "pydantic>=2.10.4",
            "pydantic-settings>=2.7.0"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {str(e)}")
        return False


async def test_agent():
    """Test the research agent functionality."""
    print("\n🧪 Testing Research Agent...")
    
    try:
        # Import here to ensure dependencies are installed
        sys.path.append(str(Path(__file__).parent / "src"))
        from src.agents import ResearchAgent, ResearchRequest
        
        agent = ResearchAgent()
        
        # Simple test query
        request = ResearchRequest(
            query="What is the current weather in London?",
            context_size="low",
            max_reasoning_steps=3
        )
        
        print("🔍 Running test query: 'What is the current weather in London?'")
        response = await agent.research(request)
        
        print(f"✅ Query processed successfully!")
        print(f"✅ Answer length: {len(response.answer)} characters")
        print(f"✅ Safety check: {response.safety_check_passed}")
        print(f"✅ Processing time: {response.processing_time:.2f}s")
        print(f"✅ Reasoning steps: {len(response.reasoning_steps)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure you're running this from the backend directory")
        return False
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


def start_server():
    """Start the FastAPI server."""
    print("\n🚀 Starting FastAPI server...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/swagger")
    print("Health Check: http://localhost:8000/research/health")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "src.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")


def show_example_usage():
    """Show example API usage."""
    print("\n💡 Example API Usage:")
    print("-" * 40)
    
    example = '''
# Test the health endpoint
curl http://localhost:8000/research/health

# Simple research query
curl -X POST "http://localhost:8000/research/query" \\
     -H "Content-Type: application/json" \\
     -d '{
       "query": "Compare Tesla Model 3 vs BMW i4",
       "context_size": "medium"
     }'

# Quick search
curl -X POST "http://localhost:8000/research/quick-search?query=Current%20Bitcoin%20price"

# Geographic search
curl -X POST "http://localhost:8000/research/query" \\
     -H "Content-Type: application/json" \\
     -d '{
       "query": "Best restaurants near Central Park",
       "user_location": {
         "type": "approximate",
         "approximate": {
           "country": "US",
           "city": "New York",
           "region": "New York"
         }
       }
     }'
'''
    print(example)


def main():
    """Main setup and test function."""
    print("🚀 AI Research Assistant Setup & Test")
    print("=" * 50)
    
    # Check requirements
    if not check_python_version():
        return
    
    if not check_openai_key():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Test the agent
    test_result = asyncio.run(test_agent())
    
    if test_result:
        print("\n🎉 Setup completed successfully!")
        print("\nWhat would you like to do next?")
        print("1. Start the FastAPI server")
        print("2. See example API usage")
        print("3. Run comprehensive tests")
        print("4. Exit")
        
        while True:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                start_server()
                break
            elif choice == "2":
                show_example_usage()
                break
            elif choice == "3":
                print("\n🧪 Running comprehensive tests...")
                os.system(f"{sys.executable} src/test_research_agent.py")
                break
            elif choice == "4":
                print("👋 Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1-4.")
    else:
        print("\n❌ Setup failed. Please check the errors above.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}") 