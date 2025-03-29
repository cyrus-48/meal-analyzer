from celery import shared_task
from .models import FoodAnalysis
from .ai_analyzer_agent import FoodAnalyzer

@shared_task
def analyze_food_image(analysis_id):
    """
    Asynchronously analyze food image using AI
    """
    analysis = FoodAnalysis.objects.get(id=analysis_id)
    try:
        # Initialize the analyzer
        analyzer = FoodAnalyzer()
        
        # Validate if image contains food
        is_food = analyzer.validate_image(analysis.image.path)
        
        if not is_food:
            analysis.status = 'failed'
            analysis.error_message = "The uploaded image does not contain food."
            analysis.save()
            return False

        # If it is food, proceed with the analysis
        result = analyzer.analyze_food(analysis.image.path)
        
        if result:
            # Update analysis object with results
            analysis.ingredients = result.ingredients
            analysis.calories = {
                "total": result.calories.total,
                "breakdown": result.calories.breakdown
            }
            analysis.nutrients = {
                "protein": result.nutrients.protein,
                "carbs": result.nutrients.carbs,
                "fats": result.nutrients.fats
            }
            analysis.status = 'completed'
            analysis.confidence_score = result.confidence_score
            analysis.save()
            return True
        
        analysis.status = 'failed'
        analysis.error_message = "Failed to analyze the image."
        analysis.save()
        return False
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        analysis.status = 'failed'
        analysis.error_message = str(e)
        analysis.save()
        return False