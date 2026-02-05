from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.api.routes import router as api_router, ws_router
from src.rag_pipeline.retriever import get_retriever
from src.rag_pipeline.query_expansion import QueryExpander
from src.config import settings

app = FastAPI(
    title="Multimodal RAG API",
    description="PDF 문서를 업로드하고 내용을 질문할 수 있는 멀티모달 RAG API입니다.",
    version="1.0.0"
)

# CORS 미들웨어 추가
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 애플리케이션 시작 시 Query Expander를 로드하여 메모리에 캐싱합니다.
# 리트리버는 유저 로그인 및 요청 시점에 UID별로 동적으로 로드(lazy loading)됩니다.
print("Initializing Query Expander...")
app.state.query_expander = QueryExpander(model_name=settings.GEMINI_MODEL)
print("Query Expander initialized.")

# 유저별 리트리버 캐시 (UID: EnsembleRetriever)
app.state.retrievers = {}

# 비동기 작업 상태를 저장하기 위한 딕셔너리
app.state.job_status = {}

app.include_router(api_router)
app.include_router(ws_router)

# 정적 파일(이미지 썸네일 등) 서빙을 위한 경로 설정
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

@app.get("/")
async def root():
    return {"message": "Multimodal RAG API is running. Visit /docs for documentation."}
