"""Load the Agentic AI eBook, chunk it, embed it, and upsert it into Pinecone."""

from pathlib import Path
import hashlib

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec

from src.config import get_settings

PDF_PATH = Path("data/Ebook-Agentic-AI.pdf")
DIMENSION = 1536
METRIC = "cosine"

def get_index():
    settings = get_settings()
    pc = Pinecone(api_key=settings.pinecone_api_key)

    existing = [idx["name"] for idx in pc.list_indexes()]
    if settings.pinecone_index_name not in existing:
        pc.create_index(
            name=settings.pinecone_index_name,
            dimension=DIMENSION,
            metric=METRIC,
            spec=ServerlessSpec(
                cloud=settings.pinecone_cloud,
                region=settings.pinecone_region,
            ),
        )
    return pc.Index(settings.pinecone_index_name)

def main():
    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"{PDF_PATH} not found. Download the Agentic AI eBook into the data/ directory first."
        )

    settings = get_settings()
    pages = PyPDFLoader(str(PDF_PATH)).load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(pages)

    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=settings.openai_api_key,
    )

    vectors = []
    for i, doc in enumerate(chunks):
        text = doc.page_content.strip()
        if not text:
            continue

        vector = embeddings.embed_query(text)
        source = doc.metadata.get("source", str(PDF_PATH))
        page = int(doc.metadata.get("page", 0)) + 1
        digest = hashlib.sha1(
            f"{source}:{page}:{i}:{text}".encode()
        ).hexdigest()[:16]

        vectors.append({
            "id": f"chunk-{digest}",
            "values": vector,
            "metadata": {
                "text": text,
                "source": source,
                "page": page,
                "chunk_id": i,
            },
        })

    index = get_index()
    for start in range(0, len(vectors), 100):
        index.upsert(vectors=vectors[start:start + 100])

    print(f"Loaded {len(pages)} pages.")
    print(f"Created {len(vectors)} chunks.")
    print(f"Upserted vectors into Pinecone index '{settings.pinecone_index_name}'.")

if __name__ == "__main__":
    main()
