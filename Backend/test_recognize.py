from app.routes.attendance import get_ai_models
try:
    get_ai_models()
    print("Models loaded successfully")
except Exception as e:
    print(f"Failed to load models: {e}")
