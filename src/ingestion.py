import wikipedia
import os

try:
    from src.config import PEOPLE_LIST, PLACES_LIST, DB_PATH
except ModuleNotFoundError:
    from config import PEOPLE_LIST, PLACES_LIST, DB_PATH

# Klasörü oluştur
os.makedirs('data/people', exist_ok=True)
os.makedirs('data/places', exist_ok=True)


def fetch_and_save(entities, category):
    for entity in entities:
        try:
            print(f"Çekiliyor: {entity}...")
            # Wikipedia'dan özet yerine tüm içeriği çekiyoruz (Chunking için veri lazım)
            page = wikipedia.page(entity, auto_suggest=False)
            content = page.content
            
            # Dosya adını temizle ve kaydet
            filename = entity.replace(" ", "_").lower() + ".txt"
            filepath = os.path.join(f'data/{category}', filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Hata oluştu ({entity}): {e}")

if __name__ == "__main__":
    fetch_and_save(PEOPLE_LIST, "people")
    fetch_and_save(PLACES_LIST, "places")