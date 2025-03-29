import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from .ai_analyzer_agent import FoodAnalyzer

def test_food_analyzer():
    """Test the FoodAnalyzer class functionality"""
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment variables")
        sys.exit(1)
    
    # Configure Google Generative AI
    genai.configure(api_key=api_key)
    
    # Initialize analyzer
    analyzer = FoodAnalyzer()
    
    # Test image path - update to your image
    image_path = Path(__file__).parent.parent / "media/food_images/food1.jpeg"
    
    if not image_path.exists():
        print(f"❌ Error: Image not found at {image_path}")
        sys.exit(1)
        
    print("\n" + "="*50)
    print("🔍 Food Analysis Test")
    print("="*50)
    print(f"📁 Image: {image_path}")
    
    try:
        # First validate if it's a food image
        print("\n1️⃣ Validating image...")
        is_food = analyzer.validate_image(str(image_path))
        print(f"🍽️ Is food image?: {'✅ Yes' if is_food else '❌ No'}")
        
        if not is_food:
            print("\n❌ Validation failed - not a food image")
            return
        
        # Then analyze the food
        print("\n2️⃣ Analyzing food...")
        result = analyzer.analyze_food(str(image_path))
        
        print("📊 Analysis result:"
              )
        print(result)
        
        print("✅ Analysis successful")
        
    except Exception as e:
        print("\n❌ Test failed")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Error details: ", end="")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_food_analyzer()