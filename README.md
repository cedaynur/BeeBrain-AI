# 🐝 BeeBrain AI: Neural Hive Intelligence
### Advanced RAG System for ITU BLG Course Project

BeeBrain AI is a sophisticated **Retrieval-Augmented Generation (RAG)** system designed to provide context-aware, factual, and hallucination-free information about notable figures and historical places. By leveraging a local "Neural Hive" architecture, it ensures data privacy and high-performance semantic search without relying on external cloud APIs.

---

## 🛠️ System Architecture

The system operates on a multi-stage RAG pipeline:
1.  **Data Ingestion:** Fetches curated content from Wikipedia.
2.  **Neural Processing:** Chunks data with semantic overlap to preserve context.
3.  **Vector Storage:** Uses **ChromaDB** with **nomic-embed-text** for high-dimensional vector mapping.
4.  **Contextual Retrieval:** Performs entity detection and pulls relevant "knowledge chunks" ($n=5$).
5.  **Neural Generation:** Utilizes **Llama 3.2** to rewrite ambiguous queries and synthesize final answers.

---

## 📁 Project Structure

```text
.
├── app.py              # BeeBrain Intelligence Interface (Streamlit UI)
├── main.py             # CLI-based Hive Interaction Controller
├── requirements.txt    # Project Dependency Manifest
├── data/               # Knowledge Base (Categorized Text Files)
│   ├── people/         # Wikipedia content for individuals
│   └── places/         # Wikipedia content for locations
├── db/                 # Persistent ChromaDB Vector Store
├── src/                # Core Neural Engine Modules
│   ├── config.py       # Global Parameters & Entity Manifests
│   ├── ingestion.py    # Wikipedia Data Acquisition Pipeline
│   ├── processor.py    # Semantic Chunking & DB Ingestion Logic
│   ├── retriever.py    # Entity Detection & Vector Search Engine
│   └── generator.py    # Query Rewriter & LLM Synthesis Engine
```

---

## ⚙️ Installation & Setup

Please follow these steps in order to run the project locally.

### 1. Install Dependencies
First, ensure you have Python 3.10+ installed. Then, install the required Python libraries:
```bash
pip install -r requirements.txt
```

### 2. Run the Local Model
BeeBrain requires **Ollama** to be running on your machine. Install Ollama and pull the necessary models:
```bash
ollama pull llama3.2
ollama pull nomic-embed-text
```
*Note: Ensure the Ollama server is active before starting the application.*

### 3. Ingest Data
Before querying, you must populate the local database. This is a two-step process:
1.  **Fetch Raw Data:** Download text from Wikipedia.
    ```bash
    python3 src/ingestion.py
    ```
2.  **Process & Index:** Chunk the text and store it in the vector database.
    ```bash
    python3 src/processor.py
    ```

### 4. Start the Application
You can interact with BeeBrain via the web interface:
```bash
streamlit run app.py
```

---

## 🔍 Example Queries

You can test the system's performance and memory capabilities with these queries:

*   **Fact Finding:** "Where exactly is Hagia Sophia located?"
*   **Comparison:** "Compare the inventions of Nikola Tesla and Thomas Edison."
*   **Contextual Memory:** 
    *   Query 1: "Tell me about Albert Einstein."
    *   Query 2: "When was **he** born?" (BeeBrain will identify "he" as Einstein).
*   **Hallucination Check:** "What is the population of the moon colony?" (System should answer: "I don't know.")

---

## 🛡️ Technical Specifications

| Component | Technology |
| :--- | :--- |
| **LLM** | Llama 3.2 (3B Parameters) |
| **Embeddings** | Nomic-Embed-Text-v1 |
| **Vector DB** | ChromaDB (Persistent) |
| **Framework** | Streamlit |
| **Retrieval Depth** | 5 chunks per source |

## 🛠️ Troubleshooting & Validation

Before reaching out for support, please verify the following:

1. **Ollama Status:** Run `ollama list` in your terminal. You should see `llama3.2` and `nomic-embed-text` listed.
2. **Database Check:** Ensure the `db/chroma_db/` directory is not empty after running `processor.py`.
3. **Common Issue (Model Not Found):** If the app hangs, ensure the Ollama server is running in the background (`ollama serve`).
4. **UI Theme:** The interface is natively adaptive. If the text is hard to read, switch your Streamlit theme (Settings -> Theme) between "Light" and "Dark".

