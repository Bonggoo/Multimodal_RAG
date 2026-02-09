import os
import google.generativeai as genai
from src.config import settings

genai.configure(api_key=settings.GOOGLE_API_KEY.get_secret_value())

test_models = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro",
    "text-embedding-004",
    "embedding-001"
]

print("Testing model accessibility...")
for model_name in test_models:
    try:
        # For generative models
        if "gemini" in model_name:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hi", generation_config={"max_output_tokens": 10})
            print(f"✅ [Generative] {model_name} is accessible.")
        else:
            # For embedding models
            result = genai.embed_content(model=f"models/{model_name}", content="Hello world")
            print(f"✅ [Embedding] models/{model_name} is accessible.")
    except Exception as e:
        print(f"❌ {model_name} failed: {e}")

print("\nListing ALL supported models for this key:")
try:
    for m in genai.list_models():
        print(f"- {m.name} (Methods: {m.supported_generation_methods})")
except Exception as e:
    print(f"Error listing models: {e}")
