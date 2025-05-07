from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class NutrientInfo(BaseModel):
    protein: int = Field(..., description="Protein content in grams")
    carbs: int = Field(..., description="Carbohydrates content in grams")
    fats: int = Field(..., description="Fats content in grams")

class CalorieInfo(BaseModel):
    total: int = Field(..., description="Total calories")
    breakdown: Dict[str, int] = Field(
        ..., 
        description="Calorie breakdown per ingredient"
    )

class FoodAnalysisResponse(BaseModel):
    ingredients: List[str] = Field(
        ..., 
        description="List of identified ingredients"
    )
    calories: CalorieInfo
    nutrients: NutrientInfo
    confidence_score: Optional[float] = Field(
        default=None,
        description="AI confidence score for the analysis"
    )

class ValidationResponse(BaseModel):
    is_food: bool = Field(..., description="Whether the image contains food")
    confidence: float = Field(..., description="Confidence score of the validation")