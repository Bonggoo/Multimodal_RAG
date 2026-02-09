import json
import re

def parse_models():
    with open("all_models.json", "r") as f:
        content = f.read()
    
    # Remove the split markers from my script
    parts = content.split("--- Testing v1/models ---")
    
    embedding_models = []
    
    for part in parts:
        try:
            # Extract the JSON part (might have curl progress or other text around it)
            json_match = re.search(r'\{.*\}', part, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                for model in data.get('models', []):
                    if 'embedContent' in model.get('supportedGenerationMethods', []):
                        embedding_models.append(model['name'])
        except Exception:
            continue
            
    print("Found Embedding Models:")
    for m in set(embedding_models):
        print(f"- {m}")

parse_models()
