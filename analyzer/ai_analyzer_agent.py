from typing import Optional, Dict
import json
from PIL import Image
import google.generativeai as genai
from .schemas import FoodAnalysisResponse
import re

class FoodAnalyzer:
    """Food analysis AI agent using Google's Generative AI"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def _load_image(self, image_path: str) -> Image.Image:
        """Load and prepare image for Gemini"""
        return Image.open(image_path)

    def _extract_json_parts(self, text: str) -> tuple:
        """Extract JSON parts from text using regex"""
        try:
            # Remove markdown code blocks and get clean JSON strings
            json_blocks = re.findall(r'```json\s*(.*?)\s*```', text, re.DOTALL)
            if len(json_blocks) != 3:
                raise ValueError(f"Expected 3 JSON blocks, got {len(json_blocks)}")

            # Parse each JSON block
            ingredients = json.loads(json_blocks[0])
            calories = json.loads(json_blocks[1])
            nutrients = json.loads(json_blocks[2])
            
            return ingredients, calories, nutrients
                
        except Exception as e:
            print(f"Raw response: {text}")  # Debug output
            print(f"JSON blocks: {json_blocks if 'json_blocks' in locals() else 'None'}")  # Debug parts
            raise ValueError(f"Failed to parse response: {str(e)}")

    def validate_image(self, image_path: str) -> bool:
        """Check if image contains food"""
        try:
            image = self._load_image(image_path)
            prompt = "Is this an image of food? Reply with only 'true' or 'false'."
            
            response = self.model.generate_content([prompt, image])
            response.resolve()
            
            return 'true' in response.text.lower()
            
        except Exception as e:
            raise Exception(f"Image validation failed: {str(e)}")

    def analyze_food(self, image_path: str) -> FoodAnalysisResponse:
        """Analyze food image and return structured data"""
        try:
            image = self._load_image(image_path)
            prompt = """Analyze this food image and return three JSON objects, each wrapped in ```json code blocks:

            First block: List of ingredients in array
            ```json
            ["ingredient1", "ingredient2"]
            ```

            Second block: Calorie information
            ```json
            {"total": 500, "breakdown": {"item1": 200, "item2": 300}}
            ```

            Third block: Nutrients
            ```json
            {"protein": 30, "carbs": 40, "fats": 15}
            ```"""
            
            response = self.model.generate_content([prompt, image])
            response.resolve()
            
            # Extract the text content from response
            content = response.text.strip()
            
            # Use our JSON extraction method
            ingredients, calories, nutrients = self._extract_json_parts(content)
            
            return FoodAnalysisResponse(
                ingredients=ingredients,
                calories=calories,
                nutrients=nutrients,
                raw_response=content,
                confidence_score=response.candidates[0].avg_logprobs
            )
            
        except Exception as e:
            print(f"Raw response content: {response.text if 'response' in locals() else 'No response'}")
            raise Exception(f"Food analysis failed: {str(e)}")