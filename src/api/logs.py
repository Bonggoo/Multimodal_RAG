import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from src.config import settings
from src.services.storage import storage_manager

DATA_DIR = "data"

def ensure_session_dir(uid: str):
    """유저의 세션 폴더를 생성하고 경로를 반환합니다."""
    session_dir = os.path.join(DATA_DIR, uid, "sessions")
    if not os.path.exists(session_dir):
        os.makedirs(session_dir)
    return session_dir

def get_metadata_path(uid: str):
    """세션 메타데이터 파일 경로를 반환합니다."""
    return os.path.join(DATA_DIR, uid, "sessions.json")

def load_sessions_metadata(uid: str) -> List[Dict[str, Any]]:
    """유저의 모든 세션 메타데이터를 로드합니다."""
    path = get_metadata_path(uid)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_sessions_metadata(uid: str, metadata: List[Dict[str, Any]]):
    """세션 메타데이터를 저장하고 GCS와 동기화합니다."""
    path = get_metadata_path(uid)
    ensure_session_dir(uid) # 부모 디렉토리 보장
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    # GCS 동기화
    try:
        storage_manager.upload_file(path, f"{uid}/sessions.json")
    except Exception as e:
        print(f"Sessions metadata GCS sync failed: {e}")

def update_session_metadata(uid: str, session_id: str, title: str = None):
    """세션 정보를 업데이트하거나 새로 생성합니다."""
    sessions = load_sessions_metadata(uid)
    now = datetime.utcnow().isoformat()
    
    found = False
    for s in sessions:
        if s["session_id"] == session_id:
            s["last_message_at"] = now
            if title:
                s["title"] = title
            found = True
            break
            
    if not found:
        sessions.insert(0, {
            "session_id": session_id,
            "title": title or "새로운 채팅",
            "created_at": now,
            "last_message_at": now
        })
        
    save_sessions_metadata(uid, sessions)

def log_qa_history(uid: str, session_id: str, trace_id: str, query: str, answer: str, filters: Dict[str, Any] = None):
    """특정 세션 파일에 대화 내용을 기록합니다."""
    session_dir = ensure_session_dir(uid)
    log_file = os.path.join(session_dir, f"{session_id}.jsonl")
    
    log_entry = {
        "trace_id": str(trace_id),
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "answer": answer,
        "filters": filters
    }
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    # 세션 메타데이터 업데이트 (마지막 메시지 시간 갱신)
    update_session_metadata(uid, session_id)
    
    # GCS 동기화 (세션 파일)
    try:
        storage_manager.upload_file(log_file, f"{uid}/sessions/{session_id}.jsonl")
    except Exception as e:
        print(f"Session log GCS sync failed: {e}")

def log_feedback(uid: str, trace_id: str, score: int, comment: str = None):
    """피드백 기록은 별도의 공용 유저 로그 파일로 관리하거나 세션에 병합할 수 있습니다. 
    여기서는 관리 편의를 위해 유저별 통합 피드백 파일로 유지합니다."""
    uid_dir = os.path.join(DATA_DIR, uid)
    if not os.path.exists(uid_dir):
        os.makedirs(uid_dir)
    log_file = os.path.join(uid_dir, "feedback_logs.jsonl")
    
    log_entry = {
        "trace_id": str(trace_id),
        "timestamp": datetime.utcnow().isoformat(),
        "score": score,
        "comment": comment
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    try:
        storage_manager.upload_file(log_file, f"{uid}/logs/feedback_logs.jsonl")
    except Exception as e:
        print(f"Feedback GCS sync failed: {e}")

def get_session_history(uid: str, session_id: str) -> List[Dict[str, Any]]:
    """특정 세션의 대화 내역 전체를 파싱하여 반환합니다."""
    session_dir = ensure_session_dir(uid)
    log_file = os.path.join(session_dir, f"{session_id}.jsonl")
    
    messages = []
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    messages.append({"role": "user", "content": data["query"], "timestamp": data["timestamp"], "trace_id": data["trace_id"]})
                    messages.append({"role": "assistant", "content": data["answer"], "timestamp": data["timestamp"], "trace_id": data["trace_id"]})
                except:
                    continue
    return messages

def delete_session(uid: str, session_id: str):
    """세션 파일 및 메타데이터에서 정보를 삭제합니다."""
    # 1. 파일 삭제
    session_dir = ensure_session_dir(uid)
    log_file = os.path.join(session_dir, f"{session_id}.jsonl")
    if os.path.exists(log_file):
        os.remove(log_file)
        
    # 2. 메타데이터 업데이트
    sessions = load_sessions_metadata(uid)
    sessions = [s for s in sessions if s["session_id"] != session_id]
    save_sessions_metadata(uid, sessions)
    
    # 3. GCS에서도 삭제 (옵션: 여기서는 덮어쓰기 방식으로 처리됨)
