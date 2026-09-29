from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.graph import graph

app = FastAPI(
    title="Agentic AI RAG Chatbot",
    description="Grounded question answering over the Agentic AI eBook.",
    version="1.0.0",
)

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)

class ChatResponse(BaseModel):
    answer: str
    retrieved_chunks: list
    confidence_score: float

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = graph.invoke({"question": request.query})
        return ChatResponse(
            answer=result.get("answer", ""),
            retrieved_chunks=result.get("context", []),
            confidence_score=float(result.get("score", 0.0)),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
