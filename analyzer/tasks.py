from celery import shared_task
from .models import FoodAnalysis
from .ai_analyzer_agent import FoodAnalyzer
import logging

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
            analysis.delete()
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
    
    
    
    

@shared_task
def process_pending_analyses():
    """
    Process all pending food analyses in the queue
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting batch processing of pending analyses")
    
    # Get all pending analyses
    pending_analyses = FoodAnalysis.objects.filter(status='pending')
    
    if not pending_analyses.exists():
        logger.info("No pending analyses found")
        return {'processed': 0, 'failed': 0}
    
    results = {
        'processed': 0,
        'failed': 0,
        'total': pending_analyses.count()
    }
    
    # Process each pending analysis
    for analysis in pending_analyses:
        try:
            logger.info(f"Processing analysis ID: {analysis.id}")
            
            # Update status to processing
            analysis.status = 'processing'
            analysis.save()
            
            # Use the existing analyze_food_image task
            success = analyze_food_image(analysis.id)
            
            if success:
                results['processed'] += 1
                logger.info(f"Successfully processed analysis ID: {analysis.id}")
            else:
                results['failed'] += 1
                logger.warning(f"Failed to process analysis ID: {analysis.id}")
                
        except Exception as e:
            results['failed'] += 1
            logger.error(f"Error processing analysis {analysis.id}: {str(e)}")
            
            # Update analysis status
            analysis.status = 'failed'
            analysis.error_message = f"Batch processing error: {str(e)}"
            analysis.save()

    logger.info(f"Completed batch processing. Results: {results}")
    return results