#!/usr/bin/env python3
"""
Test script for the new POST-based template creation API
"""

import requests
import json

def test_template_creation_api():
    """Test the updated template creation API with POST body"""
    
    # API base URL (adjust if your server runs on different port)
    base_url = "http://localhost:8000/api/v1"
    
    # Sample job ID (you would get this from uploading a resume)
    job_id = "your-job-id-here"  # Replace with actual job ID
    
    # Sample job description
    job_description = """
    Senior React Developer
    
    We are looking for a Senior React Developer to join our team. The ideal candidate will have:
    
    - 3+ years of experience with React and modern JavaScript
    - Experience with TypeScript and state management (Redux, Context API)
    - Knowledge of GraphQL and REST APIs
    - Experience with testing frameworks (Jest, React Testing Library)
    - Familiarity with CI/CD pipelines and deployment processes
    - Strong problem-solving skills and attention to detail
    
    Responsibilities:
    - Lead frontend development using React and TypeScript
    - Collaborate with backend developers to integrate APIs
    - Implement responsive designs and ensure cross-browser compatibility
    - Write comprehensive tests and maintain code quality
    - Mentor junior developers and conduct code reviews
    """
    
    print("🚀 Testing Template Creation API")
    print("=" * 50)
    
    # Test 1: Template creation with AI tailoring
    print("\n📋 Test 1: Creating template with AI tailoring")
    
    request_payload = {
        "template_id": 3,  # Using sidebar template
        "job_description": job_description
    }
    
    try:
        response = requests.post(
            f"{base_url}/create-template/{job_id}",
            json=request_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Template created successfully with AI tailoring!")
            print(f"📄 HTML content length: {len(response.text)} characters")
            
            # Save the HTML to a file for inspection
            with open("tailored_resume.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("💾 Saved tailored resume to 'tailored_resume.html'")
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the FastAPI server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Test 2: Template creation without AI tailoring
    print("\n📋 Test 2: Creating template without AI tailoring")
    
    request_payload_no_ai = {
        "template_id": 2,  # Using clean template
        # No job_description field
    }
    
    try:
        response = requests.post(
            f"{base_url}/create-template/{job_id}",
            json=request_payload_no_ai,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ Template created successfully without AI tailoring!")
            print(f"📄 HTML content length: {len(response.text)} characters")
            
            # Save the HTML to a file for comparison
            with open("original_resume.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("💾 Saved original resume to 'original_resume.html'")
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the FastAPI server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test 3: Show curl command examples
    print("\n🔧 Curl Command Examples:")
    print("-" * 30)
    
    print("\n1. With AI tailoring:")
    curl_with_ai = f'''curl -X POST "{base_url}/create-template/{job_id}" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(request_payload, indent=2)}'
'''
    print(curl_with_ai)
    
    print("\n2. Without AI tailoring:")
    curl_without_ai = f'''curl -X POST "{base_url}/create-template/{job_id}" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(request_payload_no_ai, indent=2)}'
'''
    print(curl_without_ai)
    
    print("\n📋 API Documentation:")
    print("- Method: POST")
    print(f"- URL: {base_url}/create-template/{{job_id}}")
    print("- Content-Type: application/json")
    print("- Body schema:")
    print("  {")
    print('    "template_id": 1-3,           // Required')
    print('    "job_description": "..."      // Optional')
    print("  }")


if __name__ == "__main__":
    test_template_creation_api()
