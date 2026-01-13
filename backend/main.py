from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_engine import RAGEngine
import uvicorn

# FastAPI uygulaması
app = FastAPI(
    title="BozokBot RAG API",
    description="Bozok Üniversitesi Öğrenci Yönergeleri Chatbot Backend",
    version="1.0.0"
)

# CORS ayarları (C# MVC'den erişim için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Prod'da bunu https://localhost:5001 gibi spesifik yap
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RAG Engine (singleton pattern)
rag_engine = None

class QueryRequest(BaseModel):
    question: str
    top_k: int = 10

class QueryResponse(BaseModel):
    success: bool
    answer: str
    sources: list = []
    error: str = None

@app.on_event("startup")
async def startup_event():
    """Uygulama başlarken RAG engine'i yükle"""
    global rag_engine
    print("🚀 BozokBot başlatılıyor...")
    
    rag_engine = RAGEngine()
    rag_engine.initialize_or_load_collection()
    rag_engine.load_pdfs_from_directory("./pdfs")
    
    print("✅ BozokBot hazır!")

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "message": "BozokBot API çalışıyor",
        "collection_size": rag_engine.collection.count() if rag_engine else 0
    }

@app.get("/health")
async def health():
    """Sistem sağlık durumu"""
    if not rag_engine or not rag_engine.collection:
        raise HTTPException(status_code=503, detail="RAG engine henüz yüklenmedi")
    
    return {
        "status": "healthy",
        "collection_name": rag_engine.collection_name,
        "total_chunks": rag_engine.collection.count(),
        "embedding_model": rag_engine.embedding_model
    }

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Soru sor endpoint'i"""
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine hazır değil")
    
    if not request.question or len(request.question.strip()) == 0:
        raise HTTPException(status_code=400, detail="Soru boş olamaz")
    
    # RAG ile cevap üret
    result = rag_engine.generate_answer(request.question, request.top_k)
    
    return QueryResponse(**result)

@app.get("/stats")
async def get_stats():
    """İstatistikler"""
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine hazır değil")
    
    return {
        "total_documents": rag_engine.collection.count(),
        "collection_name": rag_engine.collection_name,
        "embedding_model": rag_engine.embedding_model,
        "gemini_model": rag_engine.gemini_model
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Geliştirme için, production'da False yap
        log_level="info"
    )