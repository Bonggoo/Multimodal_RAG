import requests
import websocket
import time
import os
import json
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8000"
INGEST_URL = f"{BASE_URL}/ingest"
STATUS_URL = f"{BASE_URL}/ingest/status"
WS_URL = "ws://127.0.0.1:8000/ws/qa"

# As found in src/config.py
API_KEY = os.getenv("BACKEND_API_KEY", "FASTAPI_SECRET_KEY")
HEADERS = {"X-API-Key": API_KEY}

# Test file
TEST_PDF_PATH = "tests/assets/test_document.pdf"
TEST_QUERY = "What are the key capabilities of Gemini 1.5 Pro?"


def run_ingestion(file_path: str) -> str:
    """Uploads a document and waits for it to be processed."""
    print(f"--- 1. Starting Ingestion for {file_path} ---")
    
    if not os.path.exists(file_path):
        print(f"Error: Test file not found at {file_path}")
        return None

    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'application/pdf')}
        try:
            response = requests.post(INGEST_URL, headers=HEADERS, files=files)
        except requests.exceptions.ConnectionError as e:
            print(f"\n[ERROR] Connection to the server failed. Is the server running?")
            print(f"Please run 'poetry run uvicorn src.api.main:app --reload' in another terminal.")
            return None


    if response.status_code != 202:
        print(f"Error during ingestion request: {response.status_code} {response.text}")
        return None

    job_id = response.json().get("job_id")
    print(f"Ingestion started. Job ID: {job_id}")

    # Poll for status
    while True:
        try:
            status_response = requests.get(f"{STATUS_URL}/{job_id}", headers=HEADERS)
        except requests.exceptions.ConnectionError:
            print("\n[ERROR] Server connection lost during status check.")
            return None

        if status_response.status_code != 200:
            print(f"Error fetching status: {status_response.status_code} {status_response.text}")
            return None
        
        status_data = status_response.json()
        status = status_data.get("status")
        progress = status_data.get('details', {}).get('progress', 0)
        
        # Use carriage return to show progress in the same line
        print(f"\rCurrent job status: {status} (Progress: {progress}%)  ", end="", flush=True)

        if status == "completed":
            print("\nIngestion successful.")
            return job_id
        elif status == "failed":
            print(f"\nIngestion failed: {status_data.get('message')}")
            return None
        
        time.sleep(2)


def run_qa(query: str):
    """Connects to the WebSocket, sends a query, and streams the response."""
    print(f"\n--- 2. Running Q&A for query: '{query}' ---")
    
    ws = None
    try:
        ws = websocket.create_connection(WS_URL, header=HEADERS)
        
        # Send query
        ws.send(json.dumps({"query": query}))
        print("Query sent. Waiting for response...")
        print("\n--- LLM Stream Output ---")

        # Receive and print stream
        while True:
            message_str = ws.recv()
            message = json.loads(message_str)
            
            msg_type = message.get("type")
            payload = message.get("payload")

            if msg_type == "token":
                print(payload, end="", flush=True)
            elif msg_type == "metadata":
                print("\n\n--- Response Metadata ---")
                print(f"Cited Images: {payload.get('image_paths')}")
                print(f"Expanded Query: {payload.get('expanded_query')}")
                print("------------------------")
            elif msg_type == "end":
                print("\n--- Stream Ended ---")
                break
            elif msg_type == "error":
                print("\n\n--- Error Received ---")
                print(payload)
                print("----------------------")
                break
            else:
                print(f"\nUnknown message type: {message}")

    except (websocket.WebSocketException, ConnectionRefusedError) as e:
        print(f"\n[ERROR] WebSocket connection failed: {e}")
        print(f"Please ensure the server is running and the WebSocket endpoint is correct.")
    except Exception as e:
        print(f"\nAn error occurred during WebSocket communication: {e}")
    finally:
        if ws:
            ws.close()


if __name__ == "__main__":
    # Check for GOOGLE_API_KEY
    if not os.getenv("GOOGLE_API_KEY"):
        print("[ERROR] The 'GOOGLE_API_KEY' environment variable is not set.")
        print("Please create a '.env' file with 'GOOGLE_API_KEY=your_key_here' or set it as an environment variable.")
    else:
        print("Starting RAG Pipeline Benchmark...")
        # Check if server is running
        try:
            requests.get(BASE_URL)
        except requests.exceptions.ConnectionError:
            print(f"\n[ERROR] Connection to the server at {BASE_URL} failed. Is the server running?")
            print(f"Please run 'poetry run uvicorn src.api.main:app --reload' in another terminal first.")
        else:
            job_id = run_ingestion(TEST_PDF_PATH)
            
            if job_id:
                # Wait a moment for the server to be fully ready after ingestion
                time.sleep(1)
                run_qa(TEST_QUERY)
            
            print("\nBenchmark finished.")
