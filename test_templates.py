#!/usr/bin/env python3
"""
Test script to verify template generation works correctly
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.template_manager import TemplateManager

def test_templates():
    """Test both templates with sample data"""

    # Sample candidate data
    sample_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "title": "Senior Software Engineer",
        "location": "San Francisco, CA",
        "phone": "+1 555-0123",
        "portfolio_url": "https://johndoe.dev",
        "github_url": "https://github.com/johndoe",
        "summary": "Experienced software engineer with 8+ years of expertise in full-stack development, cloud architecture, and team leadership. Proven track record of delivering scalable solutions and mentoring junior developers.",
        "links": [
            "https://github.com/johndoe",
            "https://linkedin.com/in/johndoe",
            "https://johndoe.dev"
        ],
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "dates": "Jan 2020 - Present",
                "description": "Led development of microservices architecture serving 1M+ users. Implemented CI/CD pipelines reducing deployment time by 60%. Mentored 5 junior developers and conducted technical interviews.",
                "start_date": "Jan 2020",
                "end_date": None
            },
            {
                "title": "Software Engineer",
                "company": "Startup Inc",
                "dates": "Mar 2017 - Dec 2019",
                "description": "Developed and maintained React-based web applications. Collaborated with design team to implement pixel-perfect UIs. Optimized database queries improving response time by 40%.",
                "start_date": "Mar 2017",
                "end_date": "Dec 2019"
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University of California",
                "dates": "2013 - 2017",
                "gpa": "GPA: 3.8"
            }
        ],
        "technical_skills": {
            "programming_languages": ["Python", "JavaScript", "TypeScript", "Java"],
            "frameworks": ["React", "Node.js", "Django", "FastAPI", "AWS"],
            "skills": ["Docker", "Kubernetes", "PostgreSQL", "MongoDB", "Git"]
        },
        "key_accomplishments": "Successfully led the migration of legacy systems to cloud infrastructure, resulting in 50% cost reduction and improved system reliability. Published 3 technical articles on medium reaching 10k+ views.",
        "projects": [
            {
                "name": "E-commerce Platform",
                "tech": "React, Node.js, PostgreSQL",
                "description": "Built a full-featured e-commerce platform with payment integration, inventory management, and admin dashboard. Served 5000+ users with 99.9% uptime."
            }
        ]
    }

    # Initialize template manager
    manager = TemplateManager()

    print("Testing Template System")
    print("=" * 50)

    # Test Template 1
    print("\n1. Testing Template 1 (Modern Gradient Template)")
    try:
        html1 = manager.get_template(1, sample_data)
        print(f"✓ Template 1 generated successfully ({len(html1)} characters)")
        # Check if key elements are present
        assert "John Doe" in html1
        assert "Senior Software Engineer" in html1
        assert "john.doe@example.com" in html1
        print("✓ Template 1 contains expected candidate data")
    except Exception as e:
        print(f"✗ Template 1 failed: {e}")
        return False

    # Test Template 2
    print("\n2. Testing Template 2 (Clean Tailwind Template)")
    try:
        html2 = manager.get_template(2, sample_data)
        print(f"✓ Template 2 generated successfully ({len(html2)} characters)")
        # Check if key elements are present
        assert "John Doe" in html2
        assert "Senior Software Engineer" in html2
        assert "john.doe@example.com" in html2
        assert "Print / Save PDF" in html2  # Check for the print button
        print("✓ Template 2 contains expected candidate data")
    except Exception as e:
        print(f"✗ Template 2 failed: {e}")
        return False

    # Test Template 3
    print("\n3. Testing Template 3 (Modern CV with Sidebar)")
    try:
        html3 = manager.get_template(3, sample_data)
        print(f"✓ Template 3 generated successfully ({len(html3)} characters)")
        # Check if key elements are present
        assert "John Doe" in html3
        assert "Senior Software Engineer" in html3
        assert "john.doe@example.com" in html3
        assert "CONTACT" in html3  # Check for sidebar sections
        assert "SKILLS" in html3
        assert "EXPERIENCE" in html3
        assert "Modern CV" in html3  # Check for template title
        print("✓ Template 3 contains expected candidate data and layout")
    except Exception as e:
        print(f"✗ Template 3 failed: {e}")
        return False

    # Test available templates
    print("\n4. Testing Available Templates")
    try:
        templates = manager.get_available_templates()
        print(f"✓ Available templates: {templates}")
        assert 1 in templates
        assert 2 in templates
        assert 3 in templates
        print("✓ All three templates are registered")
    except Exception as e:
        print(f"✗ Available templates failed: {e}")
        return False

    # Test invalid template ID
    print("\n5. Testing Invalid Template ID")
    try:
        manager.get_template(999, sample_data)
        print("✗ Should have raised ValueError for invalid template ID")
        return False
    except ValueError as e:
        print(f"✓ Correctly raised ValueError: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

    print("\n" + "=" * 50)
    print("✅ All tests passed! Template system is working correctly.")
    return True

if __name__ == "__main__":
    success = test_templates()
    sys.exit(0 if success else 1)
