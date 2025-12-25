# Research Agent - Design & Architecture

## Architecture Overview
The agent is built using **LangGraph**, modeling the research process as a state machine.

### Components
1.  **State**: `AgentState` manages the `topic`, `plan`, `findings`, and `messages`. It uses a reducer (`operator.add`) for messages and findings to append updates rather than overwrite.
2.  **Planner Node**: Leverages **GPT-5 Nano** to decompose the user's high-level topic into executable search steps.
3.  **Researcher Node**: The core worker. It iterates through the plan and dynamically selects tools:
    - **Web Search**: Used for general queries (DuckDuckGo).
    - **RAG (Pinecone)**: Used when the query implies retrieving specific internal documents (triggered by keywords like "retrieve", "document").
4.  **Responder Node**: Synthesizes all gathered findings into a coherent final answer with citations.

### Persistence
We rely on `SqliteSaver` to persist the graph state to `checkpoints.sqlite`.
- **Benefit**: Fault tolerance. If the script crashes or the user pauses, the state is preserved mapped to a `thread_id`.

## Design Decisions & Trade-offs

### 1. Model Selection: GPT-5 Nano
- **Decision**: Used the specific `gpt-5-nano` model as requested.
- **Trade-off**: Smaller models may be faster/cheaper but might struggle with complex planning compared to larger models. However, for a focused research task, it is efficiently sufficient.

### 2. RAG: Pinecone + OpenAI Embeddings
- **Decision**: Used a full cloud-native Vector DB (Pinecone) instead of extensive local processing.
- **Trade-off**: Requires external API keys and setup, but simulates a production environment much better than a simple in-memory retrieval.

### 3. Tool Selection Logic
- **Decision**: Simple keyword-based routing ("retrieve" -> RAG).
- **Trade-off**: This is fragile. A better approach (with more time) would be to use an LLM router to decide the tool, or let the LLM bind tools and call them autonomously.

## Improvements with More Time
1.  **Tool-Use**: Implement true Function Calling (Tool Binding) instead of manual if/else logic in the Researcher node.
2.  **Async/Parallel**: Execute research steps in parallel (map-reduce) rather than sequentially to speed up data gathering.
3.  **Evaluation**: Add an evaluator node to critique the findings and re-plan if information is missing.
