#!/usr/bin/env python3
"""
Test script for AI Adapter Service
Run this to test the AI tailoring functionality
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from services.ai_adapter import AiAdapterService


def test_ai_adapter():
    """Test the AI adapter service with sample data"""
    
    # Sample candidate data
    candidate_data = {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "links": ["https://github.com/johndoe", "https://linkedin.com/in/johndoe"],
        "experience": [
            {
                "company": "Tech Corp",
                "title": "Software Developer",
                "description": "Worked on various web applications using JavaScript and Python. Built APIs and managed databases.",
                "start_date": "2020",
                "end_date": "2023",
                "dates": "2020 - 2023"
            },
            {
                "company": "Startup Inc",
                "title": "Junior Developer",
                "description": "Developed frontend components and helped with testing. Used React and Node.js.",
                "start_date": "2018",
                "end_date": "2020",
                "dates": "2018 - 2020"
            }
        ],
        "education": [
            {
                "institution": "University of Technology",
                "degree": "Bachelor of Computer Science",
                "start_date": "2014",
                "end_date": "2018",
                "dates": "2014 - 2018",
                "gpa": "Major: Computer Science"
            }
        ],
        "technical_skills": {
            "programming_languages": ["Python", "JavaScript", "Java"],
            "frameworks": ["React", "Node.js", "Django"],
            "skills": ["Git", "Docker", "AWS", "MySQL"]
        },
        "key_accomplishments": "Experienced full-stack developer with 5 years of experience building web applications.",
        "title": "Full-Stack Developer",
        "location": "San Francisco, CA",
        "phone": "+1 555-0123",
        "portfolio_url": "https://johndoe.dev",
        "github_url": "https://github.com/johndoe",
        "languages": [
            {"name": "English", "level": "Native"},
            {"name": "Spanish", "level": "Conversational"}
        ]
    }
    
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
    
    # Initialize AI adapter
    ai_adapter = AiAdapterService()
    
    print("🤖 AI Adapter Test")
    print("=" * 50)
    
    # Check status
    status = ai_adapter.get_status()
    print(f"OpenAI Available: {status['openai_available']}")
    print(f"Client Initialized: {status['client_initialized']}")
    print(f"API Key Configured: {status['api_key_configured']}")
    print(f"Model: {status['model']}")
    print(f"Service Available: {ai_adapter.is_available()}")
    print()
    
    if not ai_adapter.is_available():
        print("❌ AI adapter not available. Please check:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Install openai package: pip install openai>=1.40.0")
        return
    
    print("✅ AI adapter is available!")
    print("\n📄 Original candidate data:")
    print(f"Name: {candidate_data['name']}")
    print(f"Experience descriptions:")
    for exp in candidate_data['experience']:
        print(f"  - {exp['title']} at {exp['company']}: {exp['description']}")
    print(f"Key accomplishments: {candidate_data['key_accomplishments']}")
    
    print(f"\n🎯 Job description (first 200 chars): {job_description[:200]}...")
    
    print("\n🔄 Applying AI tailoring...")
    
    try:
        tailored_data = ai_adapter.tailor_candidate(candidate_data, job_description)
        
        print("\n✨ Tailored candidate data:")
        print(f"Name: {tailored_data['name']}")
        print(f"Tailored experience descriptions:")
        for exp in tailored_data['experience']:
            description = exp['description']
            if isinstance(description, list):
                print(f"  - {exp['title']} at {exp['company']}:")
                for bullet in description:
                    print(f"    • {bullet}")
            else:
                print(f"  - {exp['title']} at {exp['company']}: {description}")
        print(f"Tailored key accomplishments: {tailored_data['key_accomplishments']}")
        
        # Check if skills were reordered
        original_skills = candidate_data['technical_skills']['programming_languages']
        tailored_skills = tailored_data['technical_skills']['programming_languages']
        
        print(f"\nSkills reordering:")
        print(f"  Original: {original_skills}")
        print(f"  Tailored: {tailored_skills}")
        
        if original_skills != tailored_skills:
            print("  ✅ Skills were reordered to match job requirements")
        else:
            print("  ℹ️ Skills order remained the same")
            
        print("\n🎉 AI tailoring completed successfully!")
        
    except Exception as e:
        print(f"\n❌ AI tailoring failed: {e}")


if __name__ == "__main__":
    test_ai_adapter()
