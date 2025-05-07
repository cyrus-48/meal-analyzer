from celery import shared_task
from .models import FoodRecommendation
from .ai_recommendation_agent import MealRecommender

@shared_task
def generate_food_recommendation(recommendation_id: int) -> bool:
    """Generate food recommendation asynchronously"""
    recommendation = FoodRecommendation.objects.get(id=recommendation_id)
    
    try:
        recommender = MealRecommender()
        
        # Get preferences from recommendation object
        preferences = {
            'meal_type': recommendation.meal_type,
            'family_size': recommendation.family_size,
            'age_ranges': recommendation.age_ranges,
            'region': recommendation.region,
            'dietary_restrictions': recommendation.dietary_restrictions,
            'cultural_preferences': recommendation.cultural_preferences
        }
        
        # Generate recommendation
        result = recommender.generate_recommendation(preferences)
        
        # Update recommendation object
        recommendation.recommendations = {
            'dishes': [dish.dict() for dish in result.dishes],
            'meal_summary': result.meal_summary.dict()
        }
        recommendation.status = 'completed'
        recommendation.save()
        
        return True
        
    except Exception as e:
        recommendation.status = 'failed'
        recommendation.error_message = str(e)
        recommendation.save()
        return False