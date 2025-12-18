from fastapi import FastAPI
from src.api.routes import router as api_router
from src.rag_pipeline.retriever import get_retriever
from src.rag_pipeline.query_expansion import QueryExpander
from src.config import settings

app = FastAPI(
    title="Multimodal RAG API",
    description="PDF 문서를 업로드하고 내용을 질문할 수 있는 멀티모달 RAG API입니다.",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """
    애플리케이션 시작 시 RAG 리트리버와 Query Expander를 로드하여 메모리에 캐싱합니다.
    """
    print("Application startup: Loading RAG retriever...")
    app.state.retriever = get_retriever()
    print("RAG retriever loaded successfully.")

    print("Application startup: Initializing Query Expander...")
    app.state.query_expander = QueryExpander(model_name=settings.GEMINI_MODEL)
    print("Query Expander initialized.")

# 비동기 작업 상태를 저장하기 위한 딕셔너리
# 실제 프로덕션 환경에서는 Redis, DB 등을 사용하는 것이 좋습니다.
app.state.job_status = {}

app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Multimodal RAG API is running. Visit /docs for documentation."}
