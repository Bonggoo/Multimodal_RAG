import os
import google.generativeai as genai
from src.config import settings

genai.configure(api_key=settings.GOOGLE_API_KEY.get_secret_value())

try:
    print("Listing ALL available models...")
    for m in genai.list_models():
        print(f"Name: {m.name}, Methods: {m.supported_generation_methods}")
except Exception as e:
    print(f"Error: {e}")
