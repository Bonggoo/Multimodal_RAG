import os
import asyncio
import base64
import time
from typing import Optional
from pydantic import ValidationError

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from .schema import PageContent
from src.config import settings

# --- System Prompt ---
SYSTEM_PROMPT = """
You are a highly precise technical manual digitizer. Your goal is to convert the provided PDF page into a structured JSON format, preserving all semantic and visual information.

### CRITICAL INSTRUCTION: Visual Indicators
Manuals often use checkboxes, circles, or symbols to show which options apply to an alarm or setting. 
- You MUST explicitly mark the status of all selectable items.
- If an item is SELECTED/CHECKED: Prefix it with `[V] ` or `[Selected] `.
- If an item is NOT SELECTED: You may omit it or prefix it with `[ ] `. 
- Example: If 'RESET' is checked and 'POWER ON/OFF' is not, output: `[V] RESET, [ ] POWER ON/OFF`.

### Guidelines:
1. Text Extraction: Extract cleaned text, incorporating the [V] markers for all selected options in alarm reset, classification, etc.
2. Tables: Convert into clean Markdown tables.
3. Metadata Extraction:
   - keywords: Technical terms, error codes, and symptoms.
   - summary: Brief overview of the page's purpose.
   - document_title: Full document title (found on cover or header).

Output Schema:
{
  "text": "Cleaned text with visual selection markers [V].",
  "tables": ["Markdown tables"],
  "images": [{"description": "Description.", "caption": "Caption or null"}],
  "chapter_path": "Hierarchy",
  "keywords": ["terms"],
  "summary": "Summary",
  "document_title": "Title"
}

Accuracy in reflecting marked (checked) vs unmarked items is non-negotiable for technical safety.
"""

def parse_page_multimodal(pdf_page_bytes: bytes, max_retries: int = 3) -> Optional[PageContent]:
    """
    Parses a single PDF page using a multimodal Gemini model and validates the output.
    Includes a retry mechanism with exponential backoff for robustness.

    Args:
        pdf_page_bytes: The bytes of a single-page PDF.
        max_retries: Maximum number of retries for parsing failures.

    Returns:
        A validated PageContent object, or None if parsing or validation fails after retries.
    """
    # Initialize LangChain's ChatGoogleGenerativeAI model
    # using settings.GEMINI_MODEL (e.g. gemini-1.5-pro or gemini-2.5-flash)
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        temperature=0,
        google_api_key=settings.GOOGLE_API_KEY.get_secret_value(),
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

    for attempt in range(max_retries + 1):
        try:
            # Invoke the model
            validated_data: PageContent = llm.invoke([message])
            return validated_data

        except ValidationError as e:
            print(f"[Attempt {attempt+1}/{max_retries+1}] Gemini response validation failed: {e}")
        except Exception as e:
            print(f"[Attempt {attempt+1}/{max_retries+1}] Error parsing PDF page with Gemini: {e}")
        
        if attempt < max_retries:
            wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s...
            print(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)

    print("Failed to parse page after multiple attempts.")
    return None

async def parse_page_multimodal_async(
    pdf_page_bytes: bytes, 
    semaphore: asyncio.Semaphore,
    max_retries: int = 3
) -> Optional[PageContent]:
    """
    Parses a single PDF page using a multimodal Gemini model asynchronously.
    Uses asyncio.to_thread to run the synchronous parser in a thread, bypassing potential async DNS issues.
    """
    async with semaphore:
        # Use existing sync function in a separate thread
        return await asyncio.to_thread(parse_page_multimodal, pdf_page_bytes, max_retries)
