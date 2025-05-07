from typing import Optional, Any
import json
import re
from pydantic import BaseModel
import google.generativeai as genai

class AIResponse(BaseModel):
    raw_response: str
    confidence_score: float

class BaseAIAgent:
    """Base class for AI agents"""
    
    def __init__(self, model_name: str = 'gemini-2.0-flash'):
        self.model = genai.GenerativeModel(model_name)
    
    def _extract_json_from_response(self, text: str) -> dict:
        """Extract JSON from markdown text"""
        try:
            # Try direct JSON parsing first
            return json.loads(text)
        except json.JSONDecodeError:
            # Try extracting from markdown blocks
            json_blocks = re.findall(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
            if json_blocks:
                return json.loads(json_blocks[0])
            # Try one last time with the raw text
            return json.loads(text.strip())
    
    def _generate_content(self, prompt: str, **kwargs) -> tuple[str, float]:
        """Generate content from AI model"""
        response = self.model.generate_content(prompt, **kwargs)
        response.resolve()
        
        return (
            response.text.strip(),
            response.candidates[0].avg_logprobs if hasattr(response, 'candidates') else 0.0
        )