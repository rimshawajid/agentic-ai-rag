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

You may also download the assignment PDF manually and place it at that path.

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


## Example output / interface

The application exposes a FastAPI interface. After starting the server, open:

```text
http://127.0.0.1:8000/docs
```

The Swagger UI allows the evaluator to call `POST /chat` and inspect the returned answer, retrieved eBook chunks, and relevance/confidence score.

![Representative FastAPI output](docs/representative-output.png)

### Representative successful query

**Question**

```text
What is Agentic AI according to the eBook?
```

**Representative response shape**

```json
{
  "answer": "Agentic AI refers to AI systems that can perceive and reason about their environment, make decisions, and take actions toward goals with a degree of autonomy.",
  "retrieved_chunks": [
    {
      "text": "...relevant excerpt from the Agentic AI eBook...",
      "score": 0.82
    },
    {
      "text": "...another supporting excerpt...",
      "score": 0.76
    }
  ],
  "confidence_score": 0.82
}
```

The exact answer text and scores depend on the indexed eBook content and the evaluator's Pinecone/OpenAI run. The example above is **representative output, not a claim of a live end-to-end test**, because the development environment currently has no OpenAI API credits.

### Out-of-scope example

```text
Question: Who won the 2022 FIFA World Cup?

Expected behavior:
"I don't have enough information in the Agentic AI eBook to answer that question."
```

This demonstrates the grounding requirement: the chatbot should refuse when the answer is not supported by the retrieved eBook context.

### Important for evaluators

The repository does not contain API keys. The evaluator should create a `.env` file from `.env.example`, add their own OpenAI and Pinecone credentials, run ingestion, and then start FastAPI. No developer API credits are required from the repository author for the evaluator to run the project.
