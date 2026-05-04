import chromadb
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

try:
    from src.config import PEOPLE_LIST, PLACES_LIST, DB_PATH
except ModuleNotFoundError:
    from config import PEOPLE_LIST, PLACES_LIST, DB_PATH


class WikiRetriever:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=DB_PATH)

        self.embedding_func = OllamaEmbeddingFunction(
            model_name="nomic-embed-text"
        )

        self.collection = self.client.get_collection(
            name="wiki_rag_collection",
            embedding_function=self.embedding_func
        )

        self.PEOPLE_LIST = PEOPLE_LIST
        self.PLACES_LIST = PLACES_LIST

        self.normalized_people = [
            self.normalize_name(p) for p in PEOPLE_LIST
        ]

        self.normalized_places = [
            self.normalize_name(pl) for pl in PLACES_LIST
        ]

    def normalize_name(self, name):
        return name.lower().replace(" ", "_")

    def detect_entities(self, query):
        q = query.lower()

        found_people = []
        for person in self.PEOPLE_LIST:
            full_name = person.lower()
            last_name = person.split()[-1].lower()

            if full_name in q or last_name in q:
                found_people.append(self.normalize_name(person))

        found_places = []
        for place in self.PLACES_LIST:
            full_name = place.lower()

            if full_name in q:
                found_places.append(self.normalize_name(place))

        return found_people, found_places

    def get_source_type(self, source_name):
        if source_name in self.normalized_people:
            return "person"
        if source_name in self.normalized_places:
            return "place"
        return None

    def build_enhanced_query(self, query, source_type):
        if source_type == "person":
            return f"{query} biography known for occupation overview"
        if source_type == "place":
            return f"{query} location country city overview"
        return query

    def add_unique_context(self, contexts, sources, seen_texts, documents, metadatas):
        for doc, meta in zip(documents, metadatas):
            clean_doc = doc.strip()

            if clean_doc and clean_doc not in seen_texts:
                contexts.append(clean_doc)
                sources.append(meta.get("source", "unknown"))
                seen_texts.add(clean_doc)

    def get_intro_chunk(self, source_name, source_type):
        try:
            res = self.collection.get(
                where={
                    "$and": [
                        {"type": source_type},
                        {"source": source_name},
                        {"chunk_index": 0}
                    ]
                }
            )

            documents = res.get("documents", [])
            metadatas = res.get("metadatas", [])

            return documents, metadatas

        except Exception:
            return [], []

    def search(self, query, n_results_per_source=5):
        found_people, found_places = self.detect_entities(query)

        all_found = found_people + found_places
        all_contexts = []
        all_sources = []
        seen_texts = set()

        if found_people and found_places:
            category = "both"
        elif found_people:
            category = "person"
        elif found_places:
            category = "place"
        else:
            category = "unknown"

        if all_found:
            for source_name in all_found:
                source_type = self.get_source_type(source_name)

                if source_type is None:
                    continue

                # 1. Intro chunk'ı zorla ekle
                intro_docs, intro_metas = self.get_intro_chunk(
                    source_name=source_name,
                    source_type=source_type
                )

                self.add_unique_context(
                    contexts=all_contexts,
                    sources=all_sources,
                    seen_texts=seen_texts,
                    documents=intro_docs,
                    metadatas=intro_metas
                )

                # 2. Semantic retrieval yap
                enhanced_query = self.build_enhanced_query(query, source_type)

                res = self.collection.query(
                    query_texts=[enhanced_query],
                    n_results=n_results_per_source,
                    where={
                        "$and": [
                            {"type": source_type},
                            {"source": source_name}
                        ]
                    }
                )

                documents = res["documents"][0]
                metadatas = res["metadatas"][0]

                self.add_unique_context(
                    contexts=all_contexts,
                    sources=all_sources,
                    seen_texts=seen_texts,
                    documents=documents,
                    metadatas=metadatas
                )

        else:
            # Entity bulunamazsa genel arama
            res = self.collection.query(
                query_texts=[query],
                n_results=n_results_per_source * 2
            )

            documents = res["documents"][0]
            metadatas = res["metadatas"][0]

            self.add_unique_context(
                contexts=all_contexts,
                sources=all_sources,
                seen_texts=seen_texts,
                documents=documents,
                metadatas=metadatas
            )

        return {
            "context": "\n\n".join(all_contexts),
            "sources": list(set(all_sources)),
            "category": category,
            "found_people": found_people,
            "found_places": found_places
        }