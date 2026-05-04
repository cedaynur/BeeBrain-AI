from src.retriever import WikiRetriever
from src.generator import WikiGenerator
import time

def run_test(name, query, retriever, generator):
    print(f"\n{'='*20} TEST: {name} {'='*20}")
    print(f"Sorgu: {query}")
    
    start = time.time()
    search_res = retriever.search(query)
    answer, gen_latency = generator.generate_answer(query, search_res['context'])
    total_latency = round(time.time() - start, 2)
    
    print(f"Kategori: {search_res['category']}")
    print(f"Tespit Edilenler: {search_res.get('found_people', []) + search_res.get('found_places', [])}")
    print(f"Kaynaklar: {search_res['sources']}")
    print(f"Cevap: {answer}")
    print(f"Toplam Süre: {total_latency}s")

def main():
    retriever = WikiRetriever()
    generator = WikiGenerator()

    tests = [
        {
            "name": "Çoklu Kişi Karşılaştırma",
            "query": "Compare the contributions of Alan Turing and Ada Lovelace to computing."
        },
        {
            "name": "Spesifik Yer Bilgisi",
            "query": "What is the architectural style of the Taj Mahal and where is it?"
        },
        {
            "name": "Karma Soru (Kişi + Yer)",
            "query": "Did Leonardo da Vinci ever visit the Eiffel Tower?" 
            # Not: Kronolojik olarak imkansız, modelin 'context'e bakıp ne diyeceğini görelim.
        },
        {
            "name": "Soyisim ile Arama",
            "query": "What did Hawking discover?"
        },
        {
            "name": "Alakasız / Veritabanı Dışı Soru",
            "query": "How do I make a chocolate cake?"
        }
    ]

    for t in tests:
        run_test(t["name"], t["query"], retriever, generator)

if __name__ == "__main__":
    main()