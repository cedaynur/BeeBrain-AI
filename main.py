import time
from src.retriever import WikiRetriever
from src.generator import WikiGenerator

# Set to True if you want to see the retrieved text chunks
SHOW_CONTEXT = False

def main():
    # Initialize the core engines
    retriever = WikiRetriever()
    generator = WikiGenerator()
    
    # This list will store the conversation flow for context-aware queries
    chat_history = []
    
    print("\n=== 🐝 BeeBrain AI: Neural Hive CLI initialized ===")
    print("The system is now context-aware. Type 'exit' to quit.\n")

    while True:
        user_input = input("Enter your query: ")

        # Exit condition
        if user_input.lower() == 'exit':
            print("Shutting down the Hive...")
            break

        # Empty input check
        if not user_input.strip():
            print("Please enter a valid query.\n")
            continue

        print("\n🔎 BeeBrain is thinking...")
        
        start_time = time.time()

        # --- PHASE 1: Query Contextualization ---
        # Rewrites queries like "Who is he?" based on previous chat turns
        standalone_query = generator.rewrite_query(user_input, chat_history)
        
        if standalone_query != user_input:
            print(f"🔄 Internal Search Query: {standalone_query}")

        # --- PHASE 2: Retrieval ---
        # Search the vector database using the clarified query
        search_res = retriever.search(standalone_query)
        
        # --- PHASE 3: Generation ---
        # Generate answer using the standalone query and retrieved context
        answer, gen_latency = generator.generate_answer(standalone_query, search_res['context'])

        total_latency = round(time.time() - start_time, 2)

        # --- PHASE 4: Memory Update ---
        # Store the exchange in history for the next turn
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": answer})
        
        # Keep history concise (last 4 turns) to avoid prompt bloat
        if len(chat_history) > 8:
            chat_history = chat_history[-8:]

        # --- PHASE 5: Display Results ---
        formatted_sources = [s.replace("_", " ").title() for s in search_res['sources']]

        print(f"\n[Category]: {search_res['category'].upper()}")

        if search_res.get("found_people"):
            print(f"[Entities Found]: {', '.join(search_res['found_people'])}")

        print(f"[Sources Used]: {', '.join(formatted_sources)}")

        if SHOW_CONTEXT:
            print("\n[Context Preview]:")
            print(search_res['context'][:500] + "...")

        print(f"\n[BeeBrain]: {answer}")
        print(f"\n[Performance]: {total_latency} seconds")
        print("-" * 60)

if __name__ == "__main__":
    main()