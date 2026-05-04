import os
import shutil
import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

try:
    from src.config import DB_PATH
except ModuleNotFoundError:
    from config import DB_PATH

# Sabitler
DATA_PATH = "data"
MAX_CHUNK_SIZE = 1000 
OVERLAP_WORDS = 50     

def smart_split(text, max_size=MAX_CHUNK_SIZE, overlap_n=OVERLAP_WORDS):
    """Metni anlamlı parçalara böler ve overlap ekler."""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    for p in paragraphs:
        if len(p) > max_size:
            words = p.split()
            start = 0
            while start < len(words):
                end = start + 180 
                sub_text = " ".join(words[start:end])
                chunks.append(sub_text)
                start += (180 - overlap_n)
            continue
        if len(current_chunk) + len(p) < max_size:
            current_chunk += p + "\n\n"
        else:
            if current_chunk: chunks.append(current_chunk.strip())
            prev_words = current_chunk.split()[-overlap_n:] if current_chunk else []
            current_chunk = " ".join(prev_words) + " " + p + "\n\n"
    if current_chunk: chunks.append(current_chunk.strip())
    return chunks

def process_documents():
    # 1. Fiziksel Temizlik
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)
        print(f"Old database removed: {DB_PATH}")

    client = chromadb.PersistentClient(path=DB_PATH)
    embedding_func = OllamaEmbeddingFunction(model_name="nomic-embed-text")
    collection = client.get_or_create_collection(name="wiki_rag_collection", embedding_function=embedding_func)

    categories = {"people": "person", "places": "place"}
    total_chunks = 0

    for folder_name, label in categories.items():
        folder_path = os.path.join(DATA_PATH, folder_name)
        if not os.path.exists(folder_path): continue

        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
                    content = f.read()
                
                chunks = smart_split(content)
                name_clean = filename.replace('.txt', '')
                
                for i, chunk in enumerate(chunks):
                    # Benzersiz ID ve chunk_index eklemesi
                    u_id = f"{label}_{name_clean}_{i}"
                    collection.add(
                        documents=[chunk],
                        metadatas=[{
                            "type": label, 
                            "source": name_clean,
                            "chunk_index": i # Yeni retriever için kritik
                        }],
                        ids=[u_id]
                    )
                    total_chunks += 1
                print(f"Processed: {filename} ({len(chunks)} chunks)")

    print(f"\nProcessing Complete! Total {total_chunks} chunks saved.")

if __name__ == "__main__":
    process_documents()