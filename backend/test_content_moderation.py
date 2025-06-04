#!/usr/bin/env python3
"""
Content Moderation Agent Test Suite

This script demonstrates the multi-modal content moderation capabilities including:
- Image analysis for NSFW, violence, hate symbols
- OCR text extraction from images
- Text analysis for toxicity, hate speech, harassment
- PII detection and redaction
- Combined multi-modal analysis

Make sure to set your OPENAI_API_KEY environment variable before running.
"""

import asyncio
import os
import sys
import base64
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.absolute()
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from src.agents import ContentModerator, ModerationRequest
from src.config import get_settings


class ContentModerationTestSuite:
    """Test suite for content moderation features."""
    
    def __init__(self):
        self.moderator = ContentModerator()
        
    async def test_text_analysis(self):
        """Test text content analysis for various violations."""
        print("📝 Testing Text Content Analysis")
        print("-" * 50)
        
        test_cases = [
            # Safe content
            ("Hello, how are you today? I hope you're having a great day!", "SAFE"),
            ("I love programming and learning new technologies.", "SAFE"),
            
            # Toxic content
            ("You are so stupid and worthless!", "TOXIC"),
            ("I hate you and everyone like you", "TOXIC"),
            
            # PII content
            ("My phone number is 555-123-4567 and my email is john@example.com", "PII"),
            ("I live at 123 Main Street, New York, NY 10001", "PII"),
            
            # Hate speech
            ("All people from that country are terrorists", "HATE"),
            ("Those people don't deserve to live here", "HATE"),
            
            # Harassment
            ("I'm going to find you and make you pay", "HARASSMENT"),
            ("You better watch your back, I know where you live", "HARASSMENT"),
        ]
        
        for text, expected_category in test_cases:
            try:
                request = ModerationRequest(text=text)
                response = await self.moderator.moderate_content(request)
                
                status = "✅" if not response.is_safe else "⚠️"  # We expect unsafe for most test cases
                risk_level = response.overall_risk_level
                violations = ', '.join(response.violation_categories) if response.violation_categories else 'None'
                
                print(f"{status} '{text[:40]}...'")
                print(f"   Expected: {expected_category} | Result: {'UNSAFE' if not response.is_safe else 'SAFE'} ({risk_level})")
                print(f"   Violations: {violations}")
                print(f"   Processing time: {response.processing_time:.2f}s")
                
                # Show PII redaction if available
                if response.text_analysis and response.text_analysis.cleaned_text != text:
                    print(f"   Redacted: '{response.text_analysis.cleaned_text[:40]}...'")
                
                print()
                
            except Exception as e:
                print(f"❌ Error testing '{text[:30]}...': {str(e)}\n")
    
    async def test_image_url_analysis(self):
        """Test analysis of images via URL."""
        print("🖼️ Testing Image URL Analysis")
        print("-" * 50)
        
        # Example image URLs (you can replace with actual test images)
        test_images = [
            {
                "url": "https://via.placeholder.com/300x200/0000FF/FFFFFF?text=Safe+Image",
                "description": "Safe placeholder image",
                "expected": "SAFE"
            },
            # Add more test image URLs as needed
        ]
        
        for image_data in test_images:
            try:
                request = ModerationRequest(image_url=image_data["url"])
                response = await self.moderator.moderate_content(request)
                
                status = "✅" if response.is_safe else "🚫"
                print(f"{status} {image_data['description']}")
                print(f"   URL: {image_data['url']}")
                print(f"   Result: {'SAFE' if response.is_safe else 'UNSAFE'} ({response.overall_risk_level})")
                
                if response.image_analysis:
                    print(f"   NSFW: {response.image_analysis.has_nsfw}")
                    print(f"   Violence: {response.image_analysis.has_violence}")
                    print(f"   Hate Symbols: {response.image_analysis.has_hate_symbols}")
                    
                    if response.image_analysis.extracted_text:
                        print(f"   Extracted Text: '{response.image_analysis.extracted_text}'")
                
                print(f"   Processing time: {response.processing_time:.2f}s")
                print()
                
            except Exception as e:
                print(f"❌ Error analyzing image '{image_data['description']}': {str(e)}\n")
    
    async def test_multimodal_analysis(self):
        """Test combined image and text analysis."""
        print("🔄 Testing Multi-Modal Analysis")
        print("-" * 50)
        
        # Test with text and image URL
        test_cases = [
            {
                "text": "Check out this amazing sunset photo!",
                "image_url": "https://via.placeholder.com/400x300/FF6347/FFFFFF?text=Beautiful+Sunset",
                "description": "Safe image with safe caption"
            },
            {
                "text": "This person is an idiot and should be banned!",
                "image_url": "https://via.placeholder.com/300x300/90EE90/000000?text=Profile+Picture",
                "description": "Safe image with toxic text"
            }
        ]
        
        for case in test_cases:
            try:
                request = ModerationRequest(
                    text=case["text"],
                    image_url=case["image_url"]
                )
                response = await self.moderator.moderate_content(request)
                
                status = "✅" if response.is_safe else "🚫"
                print(f"{status} {case['description']}")
                print(f"   Text: '{case['text']}'")
                print(f"   Image: {case['image_url']}")
                print(f"   Overall Result: {'SAFE' if response.is_safe else 'UNSAFE'} ({response.overall_risk_level})")
                print(f"   Content Types: {', '.join(response.content_types_analyzed)}")
                print(f"   Violations: {', '.join(response.violation_categories) if response.violation_categories else 'None'}")
                print(f"   Summary: {response.summary}")
                print(f"   Processing time: {response.processing_time:.2f}s")
                print()
                
            except Exception as e:
                print(f"❌ Error in multimodal test '{case['description']}': {str(e)}\n")
    
    async def test_pii_detection_and_redaction(self):
        """Test PII detection and redaction capabilities."""
        print("🔒 Testing PII Detection and Redaction")
        print("-" * 50)
        
        pii_test_cases = [
            "Call me at 555-123-4567 or email john.doe@company.com",
            "My SSN is 123-45-6789 and my credit card is 4532 1234 5678 9012",
            "I live at 1234 Elm Street, Springfield, IL 62701",
            "You can reach me at (555) 987-6543 or my backup email test@gmail.com"
        ]
        
        for text in pii_test_cases:
            try:
                request = ModerationRequest(text=text, strict_mode=False)
                response = await self.moderator.moderate_content(request)
                
                has_pii = any(v.category == "pii" and v.detected for v in response.violations_found)
                status = "🔍" if has_pii else "✅"
                
                print(f"{status} Original: '{text}'")
                
                if response.text_analysis:
                    print(f"   PII Detected: {response.text_analysis.has_pii}")
                    print(f"   PII Types: {', '.join(response.text_analysis.detected_pii) if response.text_analysis.detected_pii else 'None'}")
                    print(f"   Redacted: '{response.text_analysis.cleaned_text}'")
                else:
                    print("   No text analysis results")
                
                print()
                
            except Exception as e:
                print(f"❌ Error testing PII in '{text[:30]}...': {str(e)}\n")
    
    async def test_strict_vs_normal_mode(self):
        """Test the difference between strict and normal moderation modes."""
        print("⚖️ Testing Strict vs Normal Mode")
        print("-" * 50)
        
        borderline_content = [
            "That's pretty damn annoying, but whatever",
            "This is stupid, why would anyone do this?",
            "I hate when people do things like this"
        ]
        
        for text in borderline_content:
            try:
                # Test normal mode
                normal_request = ModerationRequest(text=text, strict_mode=False)
                normal_response = await self.moderator.moderate_content(normal_request)
                
                # Test strict mode
                strict_request = ModerationRequest(text=text, strict_mode=True)
                strict_response = await self.moderator.moderate_content(strict_request)
                
                print(f"📝 Text: '{text}'")
                print(f"   Normal Mode: {'SAFE' if normal_response.is_safe else 'UNSAFE'} ({normal_response.overall_risk_level})")
                print(f"   Strict Mode: {'SAFE' if strict_response.is_safe else 'UNSAFE'} ({strict_response.overall_risk_level})")
                
                if normal_response.violation_categories != strict_response.violation_categories:
                    print(f"   Different results! Normal: {normal_response.violation_categories}, Strict: {strict_response.violation_categories}")
                
                print()
                
            except Exception as e:
                print(f"❌ Error comparing modes for '{text[:30]}...': {str(e)}\n")
    
    async def test_processing_steps_transparency(self):
        """Test the transparency of processing steps."""
        print("🔍 Testing Processing Steps Transparency")
        print("-" * 50)
        
        test_text = "This is a test message with my email test@example.com and phone 555-1234"
        
        try:
            request = ModerationRequest(text=test_text)
            response = await self.moderator.moderate_content(request)
            
            print(f"📝 Analyzed: '{test_text}'")
            print(f"Result: {'SAFE' if response.is_safe else 'UNSAFE'} ({response.overall_risk_level})")
            print()
            print("Processing Steps:")
            print("-" * 30)
            
            for step in response.processing_steps:
                print(f"{step.step_number}. {step.action.replace('_', ' ').title()}")
                print(f"   Description: {step.description}")
                print(f"   Result: {step.result[:100]}{'...' if len(step.result) > 100 else ''}")
                print()
            
        except Exception as e:
            print(f"❌ Error in transparency test: {str(e)}\n")


async def run_content_moderation_tests():
    """Run the complete content moderation test suite."""
    print("🛡️ Content Moderation Agent Test Suite")
    print("=" * 60)
    
    # Check if OpenAI API key is set
    settings = get_settings()
    if not settings.openai_api_key:
        print("❌ Error: OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key and try again.")
        return
    
    print(f"✅ OpenAI API key is configured")
    print(f"🤖 Using models:")
    print(f"   Vision: gpt-4o-mini")
    print(f"   Text: gpt-4o-mini")
    print(f"   Moderation: omni-moderation-latest")
    print()
    
    test_suite = ContentModerationTestSuite()
    
    # Run all test categories
    await test_suite.test_text_analysis()
    await test_suite.test_image_url_analysis()
    await test_suite.test_multimodal_analysis()
    await test_suite.test_pii_detection_and_redaction()
    await test_suite.test_strict_vs_normal_mode()
    await test_suite.test_processing_steps_transparency()
    
    print("🎉 Content moderation test suite completed!")
    print("\nKey Features Demonstrated:")
    print("- ✅ Text toxicity and hate speech detection")
    print("- ✅ Image content analysis (NSFW, violence, hate symbols)")
    print("- ✅ OCR text extraction from images")
    print("- ✅ PII detection and redaction")
    print("- ✅ Multi-modal content analysis")
    print("- ✅ Strict vs normal moderation modes")
    print("- ✅ Transparent processing steps")


def show_api_examples():
    """Show examples of using the content moderation API."""
    print("\n💡 Content Moderation API Examples")
    print("-" * 60)
    
    examples = '''
# Analyze text content
curl -X POST "http://localhost:8000/moderation/analyze" \\
     -H "Content-Type: application/json" \\
     -d '{
       "text": "This is some text to analyze for safety",
       "strict_mode": false
     }'

# Analyze image from URL
curl -X POST "http://localhost:8000/moderation/analyze" \\
     -H "Content-Type: application/json" \\
     -d '{
       "image_url": "https://example.com/image.jpg"
     }'

# Analyze both text and image
curl -X POST "http://localhost:8000/moderation/analyze" \\
     -H "Content-Type: application/json" \\
     -d '{
       "text": "Check out this image!",
       "image_url": "https://example.com/image.jpg",
       "strict_mode": true
     }'

# Upload and analyze image file
curl -X POST "http://localhost:8000/moderation/analyze-upload" \\
     -F "file=@image.jpg" \\
     -F "text=Optional caption text" \\
     -F "strict_mode=false"

# Quick safety check
curl -X POST "http://localhost:8000/moderation/quick-check" \\
     -H "Content-Type: application/json" \\
     -d '{
       "text": "Quick text to check",
       "strict_mode": false
     }'

# Get violation categories info
curl http://localhost:8000/moderation/categories

# Health check
curl http://localhost:8000/moderation/health
'''
    
    print(examples)


if __name__ == "__main__":
    try:
        # Run the tests
        asyncio.run(run_content_moderation_tests())
        
        # Show API examples
        show_api_examples()
        
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("Make sure you have set the OPENAI_API_KEY environment variable")
        print("and that you have an active internet connection.") 