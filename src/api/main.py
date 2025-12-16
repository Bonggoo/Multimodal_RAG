from fastapi import FastAPI
from src.api.routes import router as api_router

app = FastAPI(
    title="Multimodal RAG API",
    description="PDF 문서를 업로드하고 내용을 질문할 수 있는 멀티모달 RAG API입니다.",
    version="1.0.0"
)

app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Multimodal RAG API is running. Visit /docs for documentation."}
