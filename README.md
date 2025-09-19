## WallGraph

### What is WallGraph?
WallGraph turns messy, unstructured financial text into an actionable knowledge graph for research, risk monitoring, and strategy. It extracts signals from filings, news, transcripts, and market data, structures them with AI, and connects entities and events into a queryable graph.

At its core, WallGraph aims to:
- **Extract**: Ingest raw, unstructured financial data (SEC filings, news, earnings call transcripts, market reports, etc.).
- **Structure**: Use AI and Neo4j graph databases to map relationships between companies, suppliers, risks, and events.
- **Connect**: Build a knowledge graph of entities (tickers, companies, suppliers, executives, products) and their relationships.
- **Query & Reason**: Support natural language questions such as:
  - "Which of NVIDIA’s suppliers might be impacted by today’s earthquake in Taiwan?"
  - "What companies mentioned AI regulation risk in their 10-K this quarter?"
  - "Show me all supplier relationships for Apple over the past 5 years."
- **Enable Decisions**: Help analysts, traders, and businesses see risks and opportunities earlier by connecting scattered information into one picture.


## Project architecture

### High-level flow
- **Ingestion**: Sources (filings, news feeds, transcripts) are ingested into the backend.
- **Processing**: NLP/LLM pipelines extract entities, events, and relationships; facts are normalized.
- **Graph storage**: Entities and relationships are persisted.
- **API**: FastAPI provides endpoints for querying the graph and orchestrating workflows.
- **Frontend**: A lightweight static UI to run natural language queries.

### Repository layout
```
wallgraph/
├─ backend/
│  ├─ requirements.txt
│  └─ src/
│     └─ adapters/
│        └─ inbound/api/main.py     # FastAPI app entry: backend.src.adapters.inbound.api.main:app
├─ frontend/
│  ├─ index.html                    # Static UI shell
│  ├─ css/
│  └─ js/
├─ Dockerfile                       # Image for backend + static frontend assets
└─ docker-compose-dev.yml           # Dev composition to run locally
```

### Key components
- **Backend (FastAPI + Uvicorn)**
  - Entrypoint: `backend.src.adapters.inbound.api.main:app`
  - Exposes HTTP API (default on port `8327`) and OpenAPI docs at `/docs`
- **Frontend (static)**
  - Static assets in `frontend/` (HTML/CSS/JS)
  - Can be served by the backend or a static file server in front.
- **Graph DB / AI services**
  - Neo4j
  - LLM/NLP services for extraction and reasoning (configure via environment variables)


## Run locally with Docker Compose

### Prerequisites
- Docker and Docker Compose installed
- `.env` file at the project root for configuration consumed by the backend


### Build and start
From the repository root:
```bash
docker compose -f docker-compose-dev.yml up --build
```

This will:
- Build the Docker image defined in `Dockerfile`
- Start the backend on `http://localhost:8327`
- Mount `./backend` and `./frontend` into the container for live development

### Access
- **API**: `http://localhost:8327`
- **Frontend**: Static files are available under `frontend/`. Depending on how the backend serves static content, you can:
  - Access via the backend if static serving is wired (e.g., `http://localhost:8327/` or a configured path), or
  - Run a local static server from `frontend/` during development.




## Development notes
- The Docker image uses Python 3.11. Backend dependencies are defined in `backend/requirements.txt`.
- The container runs with `uvicorn` and `--reload` for fast iteration.
- Frontend assets are bind-mounted; changes reflect immediately.
- Ensure any required credentials are present in `.env` before starting.