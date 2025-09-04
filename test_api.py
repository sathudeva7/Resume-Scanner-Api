#!/usr/bin/env python3
"""
Simple test script for the Resume Screening API
Run this after starting the server to verify basic functionality
"""

import requests
import json
import time
import os
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8080"
TEST_FILE_PATH = "sample_resume.txt"

def create_test_resume():
    """Create a sample resume file for testing"""
    resume_content = """
John Doe
Senior Software Engineer
Email: john.doe@email.com
LinkedIn: linkedin.com/in/johndoe
GitHub: github.com/johndoe

EXPERIENCE
Senior Software Engineer | Tech Corp | 2020 - Present
- Developed web applications using Python and FastAPI
- Implemented machine learning models for data analysis
- Led team of 5 engineers in agile environment
- Built cloud infrastructure using AWS and Docker

Software Engineer | StartupXYZ | 2018 - 2020
- Created REST APIs using Django and PostgreSQL
- Implemented CI/CD pipelines using GitHub Actions
- Worked with machine learning and data science teams

EDUCATION
Bachelor of Science in Computer Science | University of Technology | 2014 - 2018

TECHNICAL SKILLS
Programming Languages: Python, JavaScript, Java, Go
Frameworks: FastAPI, Django, React, Node.js
Tools: Docker, Kubernetes, AWS, PostgreSQL, Redis
Skills: Machine Learning, Data Analysis, System Design, API Development

ACCOMPLISHMENTS
- Published 3 research papers on machine learning applications
- Open source contributor with 500+ GitHub stars
- Led migration of legacy system serving 1M+ users
- Reduced system latency by 40% through optimization
"""
    
    with open(TEST_FILE_PATH, 'w') as f:
        f.write(resume_content.strip())
    
    print(f"✅ Created test resume file: {TEST_FILE_PATH}")
    return TEST_FILE_PATH

def test_health_check():
    """Test the health check endpoint"""
    print("\n🔍 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check passed: {health_data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running.")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_upload_resume(file_path):
    """Test resume upload"""
    print("\n📤 Testing resume upload...")
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/plain')}
            response = requests.post(f"{API_BASE_URL}/api/v1/upload-resume", files=files)
        
        if response.status_code == 200:
            upload_data = response.json()
            print(f"✅ Upload successful: Job ID {upload_data['job_id']}")
            return upload_data['job_id']
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def test_job_status(job_id):
    """Test job status check"""
    print(f"\n🔍 Testing job status for {job_id}...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/resume/{job_id}")
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ Status check successful: {status_data['status']}")
            return status_data
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return None

def wait_for_completion(job_id, max_wait=60):
    """Wait for job completion"""
    print(f"\n⏳ Waiting for job {job_id} to complete...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        status_data = test_job_status(job_id)
        if status_data:
            if status_data['status'] == 'SUCCESS':
                print("✅ Job completed successfully!")
                return True
            elif status_data['status'] == 'ERROR':
                print("❌ Job failed!")
                return False
        
        print("⏳ Still processing... waiting 5 seconds")
        time.sleep(5)
    
    print("⏱️ Timeout waiting for job completion")
    return False

def test_get_resume_data(job_id):
    """Test getting extracted resume data"""
    print(f"\n📊 Testing resume data retrieval for {job_id}...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/resume/{job_id}/data")
        if response.status_code == 200:
            resume_data = response.json()
            print("✅ Resume data retrieved successfully!")
            print(f"   Name: {resume_data.get('name', 'N/A')}")
            print(f"   Email: {resume_data.get('email', 'N/A')}")
            print(f"   Skills: {len(resume_data.get('technical_skills', {}).get('skills', []))} found")
            return resume_data
        else:
            print(f"❌ Data retrieval failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Data retrieval error: {e}")
        return None

def test_screening(job_id):
    """Test resume screening"""
    print(f"\n🎯 Testing resume screening for {job_id}...")
    
    screening_request = {
        "job_ids": [job_id],
        "criteria": {
            "required_skills": ["Python", "Machine Learning"],
            "preferred_skills": ["FastAPI", "Docker", "AWS"],
            "min_years_experience": 2,
            "keywords": ["API", "web applications"]
        },
        "include_unqualified": True
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/screen-resumes",
            json=screening_request
        )
        
        if response.status_code == 200:
            screening_data = response.json()
            print("✅ Screening completed successfully!")
            print(f"   Total resumes: {screening_data['total_resumes']}")
            print(f"   Qualified candidates: {screening_data['qualified_count']}")
            
            if screening_data['results']:
                result = screening_data['results'][0]
                print(f"   Overall score: {result['overall_score']}")
                print(f"   Skills score: {result['skills_score']}")
                print(f"   Qualified: {result['qualified']}")
            
            return screening_data
        else:
            print(f"❌ Screening failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Screening error: {e}")
        return None

def test_list_resumes():
    """Test listing resumes"""
    print("\n📋 Testing resume listing...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/resumes")
        if response.status_code == 200:
            list_data = response.json()
            print(f"✅ Resume listing successful: {list_data['total_count']} resumes found")
            return list_data
        else:
            print(f"❌ Resume listing failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Resume listing error: {e}")
        return None

def cleanup_test_file():
    """Clean up test file"""
    try:
        if os.path.exists(TEST_FILE_PATH):
            os.remove(TEST_FILE_PATH)
            print(f"🧹 Cleaned up test file: {TEST_FILE_PATH}")
    except Exception as e:
        print(f"⚠️  Could not clean up test file: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Resume Screening API Tests")
    print("=" * 50)
    
    # Create test file
    test_file = create_test_resume()
    
    try:
        # Test health check
        if not test_health_check():
            print("\n❌ Health check failed. Make sure the API is running.")
            return
        
        # Test upload
        job_id = test_upload_resume(test_file)
        if not job_id:
            print("\n❌ Upload failed. Cannot continue with other tests.")
            return
        
        # Wait for processing
        if not wait_for_completion(job_id):
            print("\n❌ Job did not complete. Cannot continue with other tests.")
            return
        
        # Test data retrieval
        resume_data = test_get_resume_data(job_id)
        if not resume_data:
            print("\n❌ Could not retrieve resume data.")
            return
        
        # Test screening
        screening_result = test_screening(job_id)
        if not screening_result:
            print("\n❌ Screening failed.")
        
        # Test listing
        list_result = test_list_resumes()
        if not list_result:
            print("\n❌ Resume listing failed.")
        
        print("\n" + "=" * 50)
        print("✅ All tests completed! API is working correctly.")
        
    finally:
        cleanup_test_file()

if __name__ == "__main__":
    main()
