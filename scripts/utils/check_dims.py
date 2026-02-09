import google.generativeai as genai
import os
from src.config import settings

genai.configure(api_key=settings.GOOGLE_API_KEY.get_secret_value())

print("--- Embedding Models Discovery ---")
try:
    for m in genai.list_models():
        if 'embedContent' in m.supported_generation_methods:
            print(f"Model: {m.name}")
            print(f"  Input Token Limit: {m.input_token_limit}")
            # We can't directly get dimension from list_models, so we test it
            try:
                embedding = genai.embed_content(model=m.name, content="test")
                dim = len(embedding['embedding'])
                print(f"  Detected Dimension: {dim}")
            except Exception as e:
                print(f"  Dimension test failed: {e}")
            print("-" * 20)
except Exception as e:
    print(f"Error: {e}")
