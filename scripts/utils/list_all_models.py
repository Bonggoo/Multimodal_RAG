import google.generativeai as genai
import os
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class SimpleSettings(BaseSettings):
    GOOGLE_API_KEY: str
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

try:
    s = SimpleSettings()
    genai.configure(api_key=s.GOOGLE_API_KEY)
    
    print("--- Listing All Available Models ---")
    for m in genai.list_models():
        print(f"Name: {m.name}")
        print(f"  Display Name: {m.display_name}")
        print(f"  Supported Methods: {m.supported_generation_methods}")
        print("-" * 20)
except Exception as e:
    print(f"Error occurred: {e}")
