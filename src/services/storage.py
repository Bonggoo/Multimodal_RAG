import os
from google.cloud import storage
from google.oauth2 import service_account
from src.config import settings

class StorageManager:
    """
    Google Cloud Storage 연동을 관리하는 클래스입니다.
    사용자 UID별 데이터 격리 및 업로드/다운로드 기능을 제공합니다.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StorageManager, cls).__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        """GCS 클라이언트를 초기화합니다. (Application Default Credentials 활용)"""
        try:
            self.client = storage.Client()
            self.bucket = self.client.bucket(settings.GCS_BUCKET_NAME)
        except Exception as e:
            print(f"GCS 클라이언트 초기화 에러: {e}")
            self.client = None
            self.bucket = None

    def upload_file(self, local_path: str, remote_path: str) -> str:
        """로컬 파일을 GCS로 업로드합니다."""
        if not self.bucket:
            return ""
        
        blob = self.bucket.blob(remote_path)
        blob.upload_from_filename(local_path)
        return f"gs://{settings.GCS_BUCKET_NAME}/{remote_path}"

    def download_file(self, remote_path: str, local_path: str):
        """GCS 파일을 로컬로 다운로드합니다."""
        if not self.bucket:
            return
        
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        blob = self.bucket.blob(remote_path)
        blob.download_to_filename(local_path)

    def upload_directory(self, local_dir: str, remote_prefix: str):
        """로컬 디렉토리 전체를 GCS로 업로드합니다. (ChromaDB 동기화용)"""
        if not self.bucket or not os.path.exists(local_dir):
            return

        for root, _, files in os.walk(local_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, local_dir)
                remote_path = os.path.join(remote_prefix, relative_path)
                self.upload_file(local_path, remote_path)

    def download_directory(self, remote_prefix: str, local_dir: str):
        """GCS 디렉토리를 로컬로 다운로드합니다. (ChromaDB 워커 로드용)"""
        if not self.bucket:
            return

        blobs = self.client.list_blobs(settings.GCS_BUCKET_NAME, prefix=remote_prefix)
        for blob in blobs:
            if blob.name.endswith('/'):
                continue
            # remote_prefix 이후의 상대 경로 추출
            relative_path = os.path.relpath(blob.name, remote_prefix)
            local_path = os.path.join(local_dir, relative_path)
            self.download_file(blob.name, local_path)

    def delete_directory(self, remote_prefix: str):
        """GCS 디렉토리(prefix) 하위의 모든 객체를 삭제합니다."""
        if not self.bucket:
            return

        blobs = self.client.list_blobs(settings.GCS_BUCKET_NAME, prefix=remote_prefix)
        for blob in blobs:
            blob.delete()
        print(f"GCS path '{remote_prefix}' and its contents deleted.")

    def sync_db_to_gcs(self, uid: str):
        """유저의 로컬 ChromaDB를 GCS로 업로드합니다."""
        local_db_path = os.path.join(settings.CHROMA_DB_DIR, uid)
        remote_prefix = f"{uid}/vector_db"
        self.upload_directory(local_db_path, remote_prefix)

    def sync_db_from_gcs(self, uid: str):
        """유저의 GCS에서 로컬로 ChromaDB를 다운로드합니다."""
        local_db_path = os.path.join(settings.CHROMA_DB_DIR, uid)
        remote_prefix = f"{uid}/vector_db"
        self.download_directory(remote_prefix, local_db_path)

# 싱글톤 인스턴스 노출
storage_manager = StorageManager()
