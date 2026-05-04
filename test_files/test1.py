from src.retriever import WikiRetriever
from src.generator import WikiGenerator
import time

def main():
    retriever = WikiRetriever()
    generator = WikiGenerator()

    test_scenarios = [
        {
            "name": "Kategori Ayrımı & Giriş Bilgisi",
            "query": "Where exactly is Hagia Sophia located?" # İlk paragrafta yazar
        },
        {
            "name": "Karmaşık Karşılaştırma",
            "query": "Compare the inventions and life of Nikola Tesla and Thomas Edison." # İki kişi birden
        },
        {
            "name": "Eksik Bilgi (Halüsinasyon) Kontrolü",
            "query": "What is the population of the moon colony?" # Veritabanında yok
        },
        {
            "name": "Sadece Soyisim Tespiti",
            "query": "Tell me about Turing's work." # Alan Turing'i bulmalı
        }
    ]

    for test in test_scenarios:
        print(f"\n{'='*50}\nRUNNING TEST: {test['name']}\nQuery: {test['query']}")
        
        start_time = time.time()
        # Arama
        search_res = retriever.search(test['query'])
        # Üretim
        answer, latency = generator.generate_answer(test['query'], search_res['context'])
        
        print(f"Category Detected: {search_res['category']}")
        print(f"Sources Used: {search_res['sources']}")
        print(f"Answer: {answer}")
        print(f"Latency: {latency}s")

if __name__ == "__main__":
    main()