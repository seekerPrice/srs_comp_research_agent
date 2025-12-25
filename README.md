# Research Assistant Agent (LangGraph)

A robust research assistant built with LangGraph, featuring **intelligent LLM fallback** (OpenAI → Gemini) and **Pinecone** for Retrieval-Augmented Generation (RAG).

## Features

- **Multi-Step Research Planning**: Decomposes a topic into specific search queries.
- **Autonomous Tool Selection**: Intelligently switches between Web Search (DuckDuckGo), Wikipedia, Arxiv, and RAG (Pinecone) based on the query type.
- **LLM Fallback**: If OpenAI is unavailable, automatically falls back to Google Gemini.
- **State Persistence**: Uses SQLite to persist conversation state, allowing you to stop and resume sessions.
- **Graceful Error Handling**: Handles tool and LLM errors gracefully, informing the user instead of crashing.
- **Data Ingestion**: Scripts to index local knowledge into a serverless Pinecone vector database with auto-creation.

---

## Prerequisites

- Python 3.13
- API Keys:
  - **OpenAI API Key** (primary LLM)
  - **Google API Key** (fallback LLM - Gemini)
  - **Pinecone API Key** (for RAG)

---

## Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd research_agent
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

**Activate the environment:**

- **Windows (PowerShell)**:
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **Windows (CMD)**:
  ```cmd
  .venv\Scripts\activate.bat
  ```
- **Mac/Linux**:
  ```bash
  source .venv/bin/activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys:

```env
OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_API_KEY=your-google-api-key-here
PINECONE_API_KEY=your-pinecone-key-here
PINECONE_INDEX_NAME=research-agent
```

- `OPENAI_API_KEY`: Your OpenAI API key (get it from [platform.openai.com](https://platform.openai.com/account/api-keys))
- `GOOGLE_API_KEY`: Your Google API key for Gemini fallback (get it from [aistudio.google.com](https://aistudio.google.com/app/apikey))
- `PINECONE_API_KEY`: Your Pinecone API key
- `PINECONE_INDEX_NAME`: Name of your Pinecone index 

### 5. Ingest Knowledge Base (Optional)

Index the sample data (or your own `data/*.txt` files) into Pinecone:

```bash
python ingest.py
```

> **Note**: The script will automatically create the Pinecone index if it doesn't exist.

---

## Usage

### Start a New Research Session

```bash
python main.py
```

You will be prompted to enter a research topic.

### Start with a Specific Topic

```bash
python main.py --topic "Benefits and risks of AI in healthcare"
```


### Interactive Mode

Once running, you can:
- Type any research topic and press Enter
- Once done, you can ask new questions
- Type `quit` or `exit` to end the session

---

## Project Structure

```
research_agent/
├── main.py          # Entry point - CLI interface
├── graph.py         # LangGraph workflow definition
├── nodes.py         # Node implementations (planner, researcher, responder)
├── tools.py         # Tool definitions (web search, RAG, Wikipedia, Arxiv)
├── state.py         # Agent state schema
├── ingest.py        # Knowledge base ingestion script
├── data/            # Knowledge base files (.txt)
├── .env.example     # Environment variable template
├── requirements.txt # Python dependencies
├── writeup.md       # Architectural overview
└── README.md        # This file
```

---

## Architecture

See [writeup.md](writeup.md) for a detailed architectural overview, including:
- LangGraph workflow design
- Node responsibilities
- Tool selection logic
- Error handling strategy
- Design decisions and tradeoffs

---


