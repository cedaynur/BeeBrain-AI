# 🐝 Product Requirements Document (PRD): BeeBrain AI

## 1. Executive Summary
**BeeBrain AI** is a specialized Retrieval-Augmented Generation (RAG) platform designed for the ITU academic community. It provides a "Hive Mind" experience where users can query a local, curated database of Wikipedia entries regarding influential people and historical places. The primary goal is to eliminate LLM hallucinations by forcing the model to rely strictly on a verified local knowledge base.

## 2. Target Audience
*   **Students & Researchers:** Looking for verified, summarized information without browsing multiple web pages.
*   **History & Tech Enthusiasts:** Users interested in the lives of scientists (like Einstein, Tesla) or architectural wonders (like Hagia Sophia).
*   **Instructors:** Evaluating the implementation of RAG architectures and hallucination control.

## 3. Core Features & Functional Requirements

### 3.1. Knowledge Management
*   **Automated Ingestion:** Fetching data directly from Wikipedia via the `ingestion.py` pipeline.
*   **Semantic Indexing:** Chunks of 1000 characters with 50-word overlaps to maintain contextual continuity.
*   **Vector Search:** Powered by ChromaDB and `nomic-embed-text` for high-precision retrieval.

### 3.2. Conversational Intelligence (The BeeBrain Logic)
*   **Query Expansion:** The system must rewrite ambiguous user queries using chat history (e.g., resolving "he" to "Albert Einstein") before performing a vector search.
*   **Grounded Generation:** Answers must be synthesized using **only** the retrieved context. If information is missing, the system must strictly output "I don't know".

### 3.3. User Interface (The Hive Interface)
*   **Streaming Responses:** Real-time character-by-character output to improve perceived latency.
*   **Source Citation:** Displaying the specific Wikipedia source files used for each generated answer.
*   **Adaptive Theme:** A UI that supports both Light and Dark modes without breaking the visual hierarchy.
*   **Session Control:** Ability to purge "Hive Memory" (chat history) at any time.

## 4. Technical Specifications
*   **Language:** Python 3.10+
*   **LLM Engine:** Ollama (Llama 3.2 - 3B)
*   **Vector Store:** ChromaDB
*   **UI Framework:** Streamlit
*   **Retrieval Depth:** $n=5$ results per source to ensure comprehensive context.

## 5. User Stories
*   **As a student**, I want to compare two historical figures so that I can understand their differing impacts on technology.
*   **As a researcher**, I want to know exactly which document a piece of information came from so that I can verify its accuracy.
*   **As a user**, I want the AI to remember who we are talking about so I don't have to repeat names in every question.

## 6. Success Metrics
*   **Zero Hallucination:** 100% of responses must be traceable to the local `data/` directory.
*   **Latency:** Average response generation should be within 5-12 seconds on standard local hardware.
*   **Reliability:** Successful entity detection for all 80+ pre-defined people and places in the `config.py` manifest.

## 7. Performance & Edge Case Handling
* **Hardware Specs:** Optimized for local execution. Recommended: 8GB+ RAM. Works on CPU (via Ollama), but Apple Silicon (M-series) or NVIDIA GPUs provide optimal latency (<5s).
* **Ambiguity Handling:** Integrated `generator.rewrite_query` logic resolves ambiguous pronouns based on the last 3 messages of chat history.
* **Cold Start:** The system checks for the existence of the `db/` directory on startup to prevent querying an empty Hive.