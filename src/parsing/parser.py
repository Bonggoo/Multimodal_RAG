import os
import base64
from typing import Optional
from pydantic import ValidationError
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from .schema import PageContent

# Load environment variables
load_dotenv()

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
        # Initialize LangChain's ChatGoogleGenerativeAI model
        # using gemini-2.5-flash which has native PDF support and is cost-effective
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            convert_system_message_to_human=True,
            max_output_tokens=2048, 
        ).with_structured_output(PageContent)

        # Encode PDF bytes to base64
        pdf_base64 = base64.b64encode(pdf_page_bytes).decode("utf-8")

        # Construct the message with the system prompt and PDF part
        # LangChain handles data URIs in 'image_url' by mapping them to inline_data for Gemini
        message = HumanMessage(
            content=[
                {"type": "text", "text": SYSTEM_PROMPT},
                {
                    "type": "image_url", 
                    "image_url": {"url": f"data:application/pdf;base64,{pdf_base64}"}
                },
            ]
        )

        # Invoke the model
        validated_data: PageContent = llm.invoke([message])
        return validated_data

    except ValidationError as e:
        print(f"Gemini response validation failed: {e}")
        return None
    except Exception as e:
        print(f"Error parsing PDF page with Gemini: {e}")
        return None
