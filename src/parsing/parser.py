import google.generativeai as genai
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, ValidationError

from .client import get_gemini_client

# --- Pydantic Models for Validation ---
class Image(BaseModel):
    description: str
    caption: Optional[str] = None

class PageContent(BaseModel):
    text: str
    tables: List[str]
    images: List[Image]
    chapter_path: Optional[str] = None

# --- System Prompt ---
SYSTEM_PROMPT = """
You are an expert document analysis assistant. Your task is to process a single page of a PDF document and extract its content into a structured JSON format.

The JSON output should strictly follow this schema:
{
  "text": "A string containing all the running text from the page, concatenated and cleaned.",
  "tables": ["A list of strings, where each string is a table found on the page, formatted as a Markdown table."],
  "images": [
    {
      "description": "A detailed description of the image content.",
      "caption": "The caption of the image, if present. Can be null."
    }
  ],
  "chapter_path": "A string representing the chapter and section hierarchy (e.g., 'Chapter 3.1.2: Advanced Topics'). Can be null."
}

Analyze the provided PDF page carefully and return only a valid JSON object matching this schema.
"""

def parse_page_multimodal(pdf_page_bytes: bytes) -> Optional[PageContent]:
    """
    Parses a single PDF page using a multimodal Gemini model and validates the output.

    Args:
        pdf_page_bytes: The bytes of a single-page PDF.

    Returns:
        A validated PageContent object, or None if parsing or validation fails.
    """
    try:
        model = get_gemini_client()

        pdf_part = {"mime_type": "application/pdf", "data": pdf_page_bytes}

        response = model.generate_content(
            [SYSTEM_PROMPT, pdf_part],
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )

        # Parse the JSON string into a Python dict
        response_dict = json.loads(response.text)

        # Validate the dictionary with Pydantic
        validated_data = PageContent(**response_dict)
        return validated_data

    except ValidationError as e:
        print(f"Gemini response validation failed: {e}")
        return None
    except Exception as e:
        print(f"Error parsing PDF page with Gemini: {e}")
        return None
