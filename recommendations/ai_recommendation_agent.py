from typing import List, Dict
from pydantic import BaseModel, Field
from config.base_ai_agent import BaseAIAgent, AIResponse

class Dish(BaseModel):
    name: str
    description: str
    ingredients: List[str]
    instructions: List[str]
    nutritional_info: Dict[str, float]
    health_benefits: List[str]
    cultural_notes: str
    serving_size: str

class MealSummary(BaseModel):
    total_calories: int
    preparation_time: int
    cost_estimate: str
    dietary_notes: str

class RecommendationResponse(AIResponse):
    dishes: List[Dish]
    meal_summary: MealSummary

class MealRecommender(BaseAIAgent):
    """AI-powered meal recommendation agent"""
    
    def __init__(self):
        super().__init__(model_name='gemini-2.0-flash')

    def generate_recommendation(self, preferences: dict) -> RecommendationResponse:
        """Generate meal recommendations based on user preferences"""
        try:
            # Prepare prompt
            prompt = self._build_prompt(preferences)
            
            # Generate content
            content, confidence = self._generate_content(prompt)
            
            # Parse response
            data = self._extract_json_from_response(content)
            
            # Validate and return structured response
            return RecommendationResponse(
                raw_response=content,
                confidence_score=confidence,
                dishes=[Dish(**dish) for dish in data['dishes']],
                meal_summary=MealSummary(**data['meal_summary'])
            )
            
        except Exception as e:
            raise Exception(f"Recommendation generation failed: {str(e)}")

    def _build_prompt(self, preferences: dict) -> str:
        """Build AI prompt from user preferences"""
        return f"""As a nutrition expert, generate a detailed meal recommendation in JSON format.
        
        Requirements:
        - Meal type: {preferences.get('meal_type')}
        - Family size: {preferences.get('family_size')}
        - Age ranges: {preferences.get('age_ranges')}
        - Region: {preferences.get('region')}
        - Dietary restrictions: {preferences.get('dietary_restrictions')}
        - Cultural preferences: {preferences.get('cultural_preferences')}

        Respond with a single JSON object:
        ```json
        {{
            "dishes": [
                {{
                    "name": "string",
                    "description": "string",
                    "ingredients": ["string"],
                    "instructions": ["string"],
                    "nutritional_info": {{
                        "calories": float,
                        "protein": float,
                        "carbs": float,
                        "fats": float
                    }},
                    "health_benefits": ["string"],
                    "cultural_notes": "string",
                    "serving_size": "string"
                }}
            ],
            "meal_summary": {{
                "total_calories": integer,
                "preparation_time": integer,
                "cost_estimate": "string",
                "dietary_notes": "string"
            }}
        }}
        ```"""