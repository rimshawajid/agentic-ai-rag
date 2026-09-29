# Agentic AI RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot built for the Appening AI assignment.

## Architecture

```text
Agentic AI PDF
     |
     v
PyPDFLoader
     |
     v
RecursiveCharacterTextSplitter
     |
     v
OpenAI text-embedding-3-small
     |
     v
Pinecone Vector Index
     |
     | user question
     v
LangGraph
  START -> retrieve -> generate -> END
     |
     v
FastAPI /chat
     |
     +--> answer
     +--> retrieved_chunks
     +--> confidence_score
```

## Technology

- Python 3.10+
- LangGraph
- LangChain
- OpenAI `text-embedding-3-small`
- OpenAI `gpt-4o-mini`
- Pinecone
- FastAPI
- PyPDF

## 1. Create environment

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd agentic-ai-rag
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

## 2. Install

```bash
pip install -r requirements.txt
```

## 3. Configure `.env`

Copy `.env.example` to `.env` and add your keys:

```env
OPENAI_API_KEY=your_key
PINECONE_API_KEY=your_key
PINECONE_INDEX_NAME=agentic-ai-rag
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
TOP_K=5
MIN_RELEVANCE_SCORE=0.30
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
```

Never commit `.env`.

## 4. Download the eBook

```bash
python scripts/download_pdf.py
```

The file should become:

```text
data/Ebook-Agentic-AI.pdf
```


## 5. Build Pinecone index

```bash
python -m src.ingestion
```

The ingestion pipeline loads the PDF, creates approximately 1,000-character chunks with 200-character overlap, embeds them with OpenAI, and upserts them into Pinecone.

## 6. Start FastAPI

```bash
uvicorn app:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## 7. Test

```bash
python tests/test_queries.py
```

Required benchmark questions include:

- What is Agentic AI according to the eBook?
- How do AI agents differ from traditional automation systems?
- What are the core components of an Agentic Architecture?
- What role does memory play in Agentic AI workflows?
- Who won the 2022 FIFA World Cup?
- What are the key characteristics of Agentic AI?

The FIFA question is intentionally outside the document. The expected behavior is a grounded refusal rather than an answer from general knowledge.

## Grounding

The system uses a Pinecone relevance threshold. If the strongest retrieved similarity is below `MIN_RELEVANCE_SCORE`, generation is skipped.

When relevant context exists, the LLM is instructed to use only the retrieved eBook chunks and never outside knowledge.

## Confidence score

`confidence_score` is the highest Pinecone similarity score among the retrieved chunks. It is a retrieval relevance score, not a calibrated probability that the generated answer is correct.

## Project structure

```text
agentic-ai-rag/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── data/
│   └── Ebook-Agentic-AI.pdf
├── scripts/
│   └── download_pdf.py
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── ingestion.py
│   └── graph.py
└── tests/
    └── test_queries.py
```

## Submission checklist

- [ ] RAG implementation completed
- [ ] LangGraph workflow implemented
- [ ] Pinecone index created
- [ ] PDF ingestion completed
- [ ] OpenAI embeddings configured
- [ ] Grounded generation implemented
- [ ] FastAPI `/chat` endpoint works
- [ ] Retrieved chunks returned
- [ ] Relevance/confidence score returned
- [ ] Out-of-scope query tested
- [ ] README completed
- [ ] `.env` excluded from Git
- [ ] GitHub repository made public/shared as requested
- [ ] Only the GitHub URL submitted

## Security

Do not commit API keys. Do not redistribute the assignment PDF if its sharing terms prohibit that.



## Assignment-aligned API response

The `/chat` endpoint returns the structure requested in the assignment:

```json
{
  "query": "What is Agentic AI?",
  "final_answer": "Answer grounded in the Agentic AI eBook.",
  "retrieved_context_chunks": [
    "Chunk 1 text from the PDF...",
    "Chunk 2 text from the PDF..."
  ],
  "confidence_score": 0.92
}
```

`confidence_score` is a retrieval/groundedness score, not a calibrated probability.

## LangGraph workflow

```text
START
  |
  v
Retrieve
  |
  v
Generate grounded answer
  |
  v
Groundedness check
  |
  v
END
```

The retrieval node queries Pinecone for the most relevant eBook chunks. The
generation node is explicitly restricted to the retrieved context. The
groundedness node uses the LLM as a strict verifier and replaces an unsupported
answer with the grounded refusal message.

## Example interface

After starting FastAPI, open:

```text
http://127.0.0.1:8000/docs
```

Swagger UI provides an interactive `POST /chat` endpoint.

![Representative FastAPI output](docs/representative-output.png)

### Representative successful query

**Query**

```text
What is the core definition of Agentic AI as outlined in the eBook?
```

**Response shape**

```json
{
  "query": "What is the core definition of Agentic AI as outlined in the eBook?",
  "final_answer": "...grounded answer from the Agentic AI eBook...",
  "retrieved_context_chunks": [
    "...relevant excerpt from the eBook...",
    "...supporting excerpt from the eBook..."
  ],
  "confidence_score": 0.82
}
```



### Out-of-scope groundedness test

```text
Query: What is the capital of France?
```

Expected behavior:

```text
I don't have enough information in the Agentic AI eBook to answer that question.
```

This demonstrates that the chatbot is restricted to the supplied knowledge
base rather than answering from general world knowledge.

## Assignment benchmark queries

The included `tests/test_queries.py` contains the six requested validation
queries:

1. Definition & Scope
2. Architecture & Paradigms
3. Use Cases
4. Comparison with traditional generative AI chatbots
5. Challenges & Considerations
6. Out-of-scope capital-of-France test

## Evaluator setup

1. Clone the repository.
2. Create a Python virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env`.
5. Add the evaluator's own `OPENAI_API_KEY` and `PINECONE_API_KEY`.
6. Download the Agentic AI eBook:

```bash
python scripts/download_pdf.py
```

7. Build the Pinecone vector index:

```bash
python -m src.ingestion
```

8. Start the API:

```bash
uvicorn app:app --reload
```

9. Open `http://127.0.0.1:8000/docs` and test `/chat`.

No API keys are stored in this repository. The developer environment used for
preparation did not have sufficient OpenAI API credits for a live ingestion run,
so the README labels the displayed response as representative rather than
claiming an unverified live result.
