"""
AI Adapter Service for tailoring candidate data based on job descriptions
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OpenAI = None
    OPENAI_AVAILABLE = False


class AiAdapterService:
    """Service for tailoring candidate data using AI based on job descriptions"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = settings.OPENAI_API_KEY
        self.model = 'gpt-4o-mini'
        self.client = None
        
        if self.api_key and OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            if not self.api_key:
                logger.info("No OpenAI API key provided - AI adaptation will be skipped")
            if not OPENAI_AVAILABLE:
                logger.info("OpenAI library not available - AI adaptation will be skipped")

    def tailor_candidate(
        self,
        candidate_data: Dict[str, Any],
        job_description: str,
    ) -> Dict[str, Any]:
        """
        Returns a modified candidate_data aligned to the job_description.
        
        Args:
            candidate_data: Original candidate information dictionary
            job_description: Job description text to tailor the resume against
            
        Returns:
            Modified candidate_data with job-specific optimizations
            
        Features:
        - Preserves structure: name/email/links/experience/education/technical_skills/key_accomplishments
        - Converts experience descriptions into strong bullet points
        - Emphasizes relevant keywords and achievements
        - Prioritizes skills relevant to the job
        """
        if not job_description or not job_description.strip():
            logger.info("No job description provided - returning original candidate data")
            return candidate_data
            
        if not self.client:
            logger.info("AI client not available - returning original candidate data")
            return candidate_data

        system_prompt = """You are a professional resume optimization assistant. Given a candidate profile JSON and a job description, you will strategically align the candidate data to the job by:

1. **Experience Optimization**:
   - Convert experience descriptions into impactful bullet points (2-4 bullets per role)
   - For each experience entry, the "description" field should be a LIST of strings, where each string is one bullet point
   - Each bullet point should highlight achievements with quantifiable metrics when possible
   - Emphasize responsibilities and technologies that match the job requirements
   - Use action verbs and industry-relevant keywords from the job description
   - Example format: "description": ["Led development of microservices architecture", "Implemented CI/CD pipelines reducing deployment time by 60%", "Mentored 5 junior developers"]

2. **Skills Prioritization**:
   - Reorder technical skills to prioritize those mentioned in the job description
   - Keep all existing skills but put relevant ones first
   - Ensure no skills are removed, only reordered

3. **Key Accomplishments Enhancement**:
   - Refine the summary to highlight experiences most relevant to the target role
   - Include keywords from the job description naturally
   - Keep it concise but impactful (2-3 sentences)

4. **Structure Preservation**:
   - Maintain the exact same JSON structure and keys
   - Do not add new root-level keys or remove existing ones
   - Preserve all personal information (name, email, links) exactly as provided
   - IMPORTANT: Convert experience "description" from string to array of strings for bullet points

Return ONLY the updated JSON without any additional commentary or explanation."""

        user_prompt = f"""Job Description:
{job_description}

Candidate Profile JSON:
{json.dumps(candidate_data, ensure_ascii=False, indent=2)}

Please optimize this candidate profile for the given job description."""

        try:
            logger.info("Sending request to OpenAI for candidate data tailoring")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Remove potential markdown code blocks
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            updated_data = json.loads(content)
            
            # Defensive programming: ensure all required keys exist
            self._ensure_required_keys(updated_data, candidate_data)
            
            logger.info("Successfully tailored candidate data using AI")
            return updated_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            return candidate_data
        except Exception as e:
            logger.error(f"AI adaptation failed: {e}")
            return candidate_data

    def _ensure_required_keys(self, updated_data: Dict[str, Any], original_data: Dict[str, Any]):
        """Ensure all required keys exist in the updated data, using original as fallback"""
        required_keys = [
            "name", "email", "links", "experience", "education", 
            "technical_skills", "key_accomplishments"
        ]
        
        for key in required_keys:
            if key not in updated_data:
                updated_data[key] = original_data.get(key, self._get_default_value(key))
        
        # Ensure technical_skills has the right structure
        if "technical_skills" in updated_data:
            tech_skills = updated_data["technical_skills"]
            if not isinstance(tech_skills, dict):
                updated_data["technical_skills"] = original_data.get("technical_skills", {})
            else:
                tech_skills.setdefault("programming_languages", [])
                tech_skills.setdefault("frameworks", [])
                tech_skills.setdefault("skills", [])

    def _get_default_value(self, key: str) -> Any:
        """Get default value for missing keys"""
        defaults = {
            "name": "Candidate Name",
            "email": "candidate@email.com",
            "links": [],
            "experience": [],
            "education": [],
            "technical_skills": {"programming_languages": [], "frameworks": [], "skills": []},
            "key_accomplishments": "",
            "title": "Professional",
            "location": "City, Country",
            "phone": "+00 0000 000000",
            "portfolio_url": "#",
            "github_url": "#",
            "languages": []
        }
        return defaults.get(key, "")

    def is_available(self) -> bool:
        """Check if AI adaptation is available"""
        return self.client is not None

    def get_status(self) -> Dict[str, Any]:
        """Get service status information"""
        return {
            "openai_available": OPENAI_AVAILABLE,
            "client_initialized": self.client is not None,
            "api_key_configured": bool(self.api_key),
            "model": self.model
        }


# Global service instance
_ai_adapter_singleton: Optional[AiAdapterService] = None


def get_ai_adapter_service() -> AiAdapterService:
    """Get AI adapter service instance (singleton pattern)"""
    global _ai_adapter_singleton
    if _ai_adapter_singleton is None:
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        _ai_adapter_singleton = AiAdapterService(api_key=api_key, model=model)
    return _ai_adapter_singleton
