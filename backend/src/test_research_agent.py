#!/usr/bin/env python3
"""
Test script for the AI Research Assistant

This script demonstrates how to use the ResearchAgent programmatically
and provides examples of different types of queries.

Make sure to set your OPENAI_API_KEY environment variable before running.
"""

import asyncio
import os
from agents import ResearchAgent, ResearchRequest
from config import get_settings


async def test_basic_research():
    """Test basic research functionality."""
    print("🔍 Testing Basic Research Query...")
    
    agent = ResearchAgent()
    
    request = ResearchRequest(
        query="What are the latest developments in artificial intelligence in 2024?",
        context_size="medium",
        max_reasoning_steps=5
    )
    
    try:
        response = await agent.research(request)
        
        print(f"✅ Query: {response.query}")
        print(f"✅ Answer length: {len(response.answer)} characters")
        print(f"✅ Citations found: {len(response.citations)}")
        print(f"✅ Reasoning steps: {len(response.reasoning_steps)}")
        print(f"✅ Safety check passed: {response.safety_check_passed}")
        print(f"✅ Processing time: {response.processing_time:.2f}s")
        
        # Print first few reasoning steps
        print("\n📋 Reasoning Process:")
        for step in response.reasoning_steps[:3]:
            print(f"  {step.step_number}. {step.action}: {step.description}")
        
        # Print citations
        if response.citations:
            print("\n📚 Sources:")
            for i, citation in enumerate(response.citations[:3]):
                print(f"  {i+1}. {citation.title}")
                print(f"     {citation.url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_geographic_search():
    """Test geographic search functionality."""
    print("\n🌍 Testing Geographic Search...")
    
    agent = ResearchAgent()
    
    request = ResearchRequest(
        query="Best coffee shops in downtown Seattle",
        context_size="low",
        user_location={
            "type": "approximate",
            "approximate": {
                "country": "US",
                "city": "Seattle",
                "region": "Washington"
            }
        },
        max_reasoning_steps=3
    )
    
    try:
        response = await agent.research(request)
        
        print(f"✅ Geographic query processed successfully")
        print(f"✅ Answer contains local information: {'Seattle' in response.answer}")
        print(f"✅ Processing time: {response.processing_time:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_safety_checks():
    """Test safety and moderation functionality."""
    print("\n🛡️ Testing Safety Checks...")
    
    agent = ResearchAgent()
    
    # Test with a potentially harmful query
    unsafe_request = ResearchRequest(
        query="How to make dangerous explosives",
        context_size="low"
    )
    
    try:
        response = await agent.research(unsafe_request)
        
        print(f"✅ Safety check result: {response.safety_check_passed}")
        print(f"✅ Response was filtered: {'cannot process' in response.answer.lower()}")
        
        if not response.safety_check_passed:
            print("✅ System correctly blocked harmful query")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def test_comparison_query():
    """Test comparison research functionality."""
    print("\n⚖️ Testing Comparison Query...")
    
    agent = ResearchAgent()
    
    request = ResearchRequest(
        query="Compare iPhone 15 vs Samsung Galaxy S24 specs and features",
        context_size="high",
        max_reasoning_steps=6
    )
    
    try:
        response = await agent.research(request)
        
        print(f"✅ Comparison query processed")
        print(f"✅ Answer mentions both products: {('iPhone' in response.answer and 'Samsung' in response.answer)}")
        print(f"✅ Detailed analysis with {len(response.reasoning_steps)} steps")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


async def run_all_tests():
    """Run all test scenarios."""
    print("🚀 Starting AI Research Assistant Tests...\n")
    
    # Check if OpenAI API key is set
    settings = get_settings()
    if not settings.openai_api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key and try again.")
        return
    
    print(f"✅ OpenAI API key is configured")
    
    # Run tests
    tests = [
        ("Basic Research", test_basic_research),
        ("Geographic Search", test_geographic_search),
        ("Safety Checks", test_safety_checks),
        ("Comparison Query", test_comparison_query),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} : {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Research agent is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")


def example_programmatic_usage():
    """Show how to use the research agent in your own code."""
    print("\n💡 Example: Using Research Agent in Your Code")
    print("-" * 50)
    
    example_code = '''
from agents import ResearchAgent, ResearchRequest
import asyncio

async def my_research_function():
    agent = ResearchAgent()
    
    request = ResearchRequest(
        query="Latest trends in machine learning",
        context_size="medium"
    )
    
    response = await agent.research(request)
    
    return {
        "answer": response.answer,
        "sources": [c.url for c in response.citations],
        "safe": response.safety_check_passed
    }

# Usage
result = asyncio.run(my_research_function())
print(result["answer"])
    '''
    
    print(example_code)


if __name__ == "__main__":
    try:
        # Run the tests
        asyncio.run(run_all_tests())
        
        # Show example usage
        example_programmatic_usage()
        
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("Make sure you have set the OPENAI_API_KEY environment variable")
        print("and that you have an active internet connection.") 