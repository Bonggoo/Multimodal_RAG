import os
import shutil
from src.services.storage import storage_manager
from src.config import settings

def reset_all_data(uid: str = "default"):
    print(f"--- Full Data Reset for UID: {uid} ---")
    
    # 1. Local Reset
    local_db_path = os.path.join(settings.CHROMA_DB_DIR, uid)
    if os.path.exists(local_db_path):
        shutil.rmtree(local_db_path)
        print(f"Local DB deleted: {local_db_path}")
        
    local_assets_path = os.path.join("assets/images", uid)
    if os.path.exists(local_assets_path):
        shutil.rmtree(local_assets_path)
        print(f"Local assets deleted: {local_assets_path}")

    # 2. Remote (GCS) Reset
    print("Clearing GCS Data...")
    storage_manager.delete_directory(f"{uid}/vector_db")
    storage_manager.delete_directory(f"{uid}/thumbnails")
    
    # 3. Re-create necessary local structure
    os.makedirs("assets/images", exist_ok=True)
    os.makedirs("data/parsed", exist_ok=True)
    
    print("\n✅ Reset Complete! Now restart the server and upload documents.")

if __name__ == "__main__":
    # UID 확인 (환경 변수 등이 없다면 기본값 사용)
    # 현재 로그상 유저의 UID는 117079310173772043360 임을 확인
    target_uid = "117079310173772043360"
    reset_all_data(target_uid)
