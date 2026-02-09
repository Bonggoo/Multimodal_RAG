import os
import sys
from google.cloud import storage

# src 경로 추가 (config 등을 가져오기 위해)
sys.path.append(os.getcwd())

try:
    from src.config import settings
    print(f"Checking bucket: {settings.GCS_BUCKET_NAME}")
    
    client = storage.Client()
    bucket = client.bucket(settings.GCS_BUCKET_NAME)
    
    if bucket.exists():
        print(f"SUCCESS: Bucket '{settings.GCS_BUCKET_NAME}' exists.")
        # 테스트 파일 업로드 시도
        blob = bucket.blob("test_connection.txt")
        blob.upload_from_string("Connection test successful.")
        print("SUCCESS: Upload test passed.")
    else:
        print(f"ERROR: Bucket '{settings.GCS_BUCKET_NAME}' DOES NOT exist.")
        print("Please create the bucket in your GCP console.")
except Exception as e:
    print(f"ERROR: GCS Connection failed.")
    print(f"Detail: {e}")
    print("\nTip: Have you run 'gcloud auth application-default login'?")
