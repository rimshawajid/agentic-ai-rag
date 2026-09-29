"""LangGraph RAG workflow: question -> retrieve -> grounded generation."""

from typing import TypedDict, List, Dict, Any

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from pinecone import Pinecone

from src.config import get_settings

class AgentState(TypedDict, total=False):
    question: str
    context: List[Dict[str, Any]]
    answer: str
    score: float

def _index():
    settings = get_settings()
    pc = Pinecone(api_key=settings.pinecone_api_key)
    return pc.Index(settings.pinecone_index_name)

def retrieve(state: AgentState) -> AgentState:
    settings = get_settings()
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )

    result = _index().query(
        vector=embeddings.embed_query(state["question"]),
        top_k=settings.top_k,
        include_metadata=True,
    )

    matches = result.get("matches", [])
    context = []
    scores = []

    for match in matches:
        score = float(match.get("score", 0.0))
        metadata = match.get("metadata", {}) or {}
        context.append({
            "id": match.get("id"),
            "score": round(score, 4),
            "text": metadata.get("text", ""),
            "page": metadata.get("page"),
            "source": metadata.get("source"),
        })
        scores.append(score)

    return {
        "context": context,
        "score": round(max(scores) if scores else 0.0, 4),
    }

def generate(state: AgentState) -> AgentState:
    settings = get_settings()

    if not state.get("context") or state.get("score", 0.0) < settings.min_relevance_score:
        return {
            "answer": (
                "I don't have enough information in the Agentic AI eBook "
                "to answer that question."
            )
        }

    context_text = "\n\n".join(
        f"[Source {i + 1} | Page {item.get('page')}]\n{item.get('text', '')}"
        for i, item in enumerate(state["context"])
    )

    system_prompt = """You are a document-grounded RAG assistant.

You MUST answer using only the supplied context from the Agentic AI eBook.
Do not use outside knowledge, memory, assumptions, or general world knowledge.
If the context does not contain enough information to answer the question,
say exactly: "I don't have enough information in the Agentic AI eBook to answer that question."

Rules:
1. Do not invent facts.
2. Do not answer from pretrained knowledge.
3. Keep the answer concise and directly supported by the context.
4. When useful, mention the relevant page number.
"""

    llm = ChatOpenAI(
        model=settings.llm_model,
        temperature=0,
        api_key=settings.openai_api_key,
    )

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=f"QUESTION:\n{state['question']}\n\nCONTEXT:\n{context_text}"
        ),
    ])

    return {"answer": response.content}

def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate)
    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)
    return workflow.compile()

graph = build_graph()
