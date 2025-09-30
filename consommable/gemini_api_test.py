import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API connection and functionality"""
    
    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    
    print("=== Gemini API Test ===")
    print(f"API Key loaded: {'✅ Yes' if api_key else '❌ No'}")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return False
    
    # Configure Gemini API
    try:
        genai.configure(api_key=api_key)
        print("✅ API configured successfully")
    except Exception as e:
        print(f"❌ Error configuring API: {e}")
        return False
    
    # Try to use gemini-2.0-flash model specifically
    model_name = 'models/gemini-2.0-flash-exp'
    print(f"\n--- Testing with {model_name} ---")
    
    # First, list available models for reference
    print("\n--- Available Models ---")
    try:
        models = list(genai.list_models())
        print(f"Total available models: {len(models)}")
        available_model_names = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                available_model_names.append(model.name)
                print(f"  - {model.name} (supports generateContent)")
        
        # Check if our preferred model is available
        if model_name not in available_model_names:
            print(f"⚠️  {model_name} not found, trying alternatives...")
            # Try other gemini-2.0 variants
            alternatives = ['models/gemini-2.0-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-1.5-flash']
            for alt in alternatives:
                if alt in available_model_names:
                    model_name = alt
                    print(f"✅ Using alternative: {model_name}")
                    break
            else:
                # Fall back to first available model
                if available_model_names:
                    model_name = available_model_names[0]
                    print(f"⚠️  Using fallback model: {model_name}")
                else:
                    print("❌ No models available for content generation")
                    return False
        else:
            print(f"✅ Found requested model: {model_name}")
        
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        # Try to proceed with the requested model anyway
        pass
    
    # Test basic API call
    print("\n--- Testing Basic API Call ---")
    try:
        model = genai.GenerativeModel(model_name)
        
        test_prompt = """
        Bonjour, tu es une IA spécialisée dans la gestion de véhicules.
        Peux-tu me répondre en français pour confirmer que tu fonctionnes correctement ?
        Dis-moi simplement "Test réussi - API Gemini fonctionnelle"
        """
        
        print("Sending test prompt...")
        response = model.generate_content(test_prompt)
        
        print("✅ API call successful!")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error with basic API call: {e}")
        return False
    
    # Test vehicle maintenance email generation
    print("\n--- Testing Vehicle Email Generation ---")
    try:
        # Sample vehicle data
        sample_vehicle_data = {
            'license_plate': 'AB-123-CD',
            'brand': 'Renault',
            'commercial_type': 'Master',
            'vehicle_type': 'Utilitaire',
            'group_number': '2',
            'body_type': 'Fourgon',
            'kilometers': '85000',
            'comments': 'Véhicule en bon état général, révision récente'
        }
        
        sample_notifications = [{
            'type': 'Contrôle Technique',
            'due_date': '2025-07-15',
            'message': 'Contrôle technique obligatoire à effectuer',
            'vehicle_data': sample_vehicle_data
        }]
        
        # Create prompt for email generation
        email_prompt = f"""
        Tu es une intelligence artificielle qui rédige des mails en français pour l'entreprise Bourgeois Travaux Publics.
        
        Génère un email de rappel pour le mécanicien José concernant le véhicule suivant :
        
        Véhicule : {sample_vehicle_data['license_plate']} - {sample_vehicle_data['brand']} {sample_vehicle_data['commercial_type']}
        Type : {sample_vehicle_data['vehicle_type']}
        Kilométrage : {sample_vehicle_data['kilometers']} km
        Commentaires : {sample_vehicle_data['comments']}
        
        Notification : Contrôle technique à effectuer avant le 15 juillet 2025
        
        Format demandé :
        OBJET: [Objet de l'email]
        
        CORPS:
        [Corps de l'email en français, professionnel mais amical]
        
        Signe : Agent artificiel chargé des véhicules Bourgeois Travaux Publics
        """
        
        print("Generating vehicle maintenance email...")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(email_prompt)
        
        print("✅ Email generation successful!")
        print("Generated content:")
        print("-" * 50)
        print(response.text)
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Error generating vehicle email: {e}")
        return False
    
    print("\n--- Complete Model Information ---")
    try:
        for model in models:
            print(f"  - {model.name}")
            print(f"    Display name: {model.display_name}")
            print(f"    Supported methods: {model.supported_generation_methods}")
            print()
        
    except Exception as e:
        print(f"❌ Error showing model details: {e}")
    
    return True

def test_custom_prompt(custom_prompt=None):
    """Test Gemini API with a custom prompt"""
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found")
        return False
    
    genai.configure(api_key=api_key)
    
    if not custom_prompt:
        custom_prompt = input("Enter your custom prompt: ")
    
    try:
        # Use the same model selection logic as main test
        model_name = 'models/gemini-2.0-flash-exp'
        
        # Get available models first
        models = list(genai.list_models())
        available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        
        # Check if our preferred model is available
        if model_name not in available_models:
            # Try alternatives
            alternatives = ['models/gemini-2.0-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-1.5-flash']
            for alt in alternatives:
                if alt in available_models:
                    model_name = alt
                    break
            else:
                # Fall back to first available model
                if available_models:
                    model_name = available_models[0]
                else:
                    print("❌ No models available for content generation")
                    return False
        
        print(f"Using model: {model_name}")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(custom_prompt)
        
        print("\n✅ Custom prompt response:")
        print("-" * 50)
        print(response.text)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error with custom prompt: {e}")
        return False

if __name__ == "__main__":
    # Run basic tests
    success = test_gemini_api()
    
    if success:
        print("\n" + "="*50)
        print("✅ All Gemini API tests passed!")
        print("The API is working correctly and ready for use.")
        
        # Ask if user wants to test custom prompt
        print("\nWould you like to test a custom prompt? (y/n)")
        user_choice = input().lower().strip()
        
        if user_choice in ['y', 'yes']:
            test_custom_prompt()
            
    else:
        print("\n" + "="*50)
        print("❌ Gemini API tests failed!")
        print("Please check your API key and connection.")
        
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
