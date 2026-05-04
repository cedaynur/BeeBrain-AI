# src/config.py

PEOPLE_LIST = [
    "Albert Einstein", "Marie Curie", "Leonardo da Vinci", "William Shakespeare",
    "Ada Lovelace", "Nikola Tesla", "Lionel Messi", "Cristiano Ronaldo",
    "Taylor Swift", "Frida Kahlo", # Zorunlu
    "Thomas Edison", "Isaac Newton", "Stephen Hawking", "Charles Darwin", 
    "Alan Turing", "Steve Jobs", "Serena Williams", "Pele", "Beyonce", "Diego Rivera" # Bonus
]

PLACES_LIST = [
    "Eiffel Tower", "Great Wall of China", "Taj Mahal", "Grand Canyon",
    "Machu Picchu", "Colosseum", "Hagia Sophia", "Statue of Liberty",
    "Pyramids of Giza", "Mount Everest", # Zorunlu
    "Parthenon", "Sultan Ahmed Mosque", "Petra", "Stonehenge", 
    "Louvre", "Burj Khalifa", "Niagara Falls", "Cappadocia", "Amazon rainforest", "Mount Fuji" # Bonus
]

# Diğer ortak ayarlar
DB_PATH = "db/chroma_db"
MODEL_NAME = "llama3.2"
EMBEDDING_MODEL = "nomic-embed-text"