import ollama
import time
import re


class WikiGenerator:
    def __init__(self, model_name="llama3.2"):
        self.model_name = model_name

        self.known_entities = [
            "Albert Einstein", "Marie Curie", "Leonardo da Vinci", "William Shakespeare",
            "Ada Lovelace", "Nikola Tesla", "Lionel Messi", "Cristiano Ronaldo",
            "Taylor Swift", "Frida Kahlo", "Thomas Edison", "Isaac Newton",
            "Stephen Hawking", "Charles Darwin", "Alan Turing", "Steve Jobs",
            "Serena Williams", "Pele", "Beyonce", "Diego Rivera",
            "Eiffel Tower", "Great Wall of China", "Taj Mahal", "Grand Canyon",
            "Machu Picchu", "Colosseum", "Hagia Sophia", "Statue of Liberty",
            "Pyramids of Giza", "Mount Everest", "Parthenon", "Sultan Ahmed Mosque",
            "Petra", "Stonehenge", "Louvre", "Burj Khalifa", "Niagara Falls",
            "Cappadocia", "Amazon rainforest", "Mount Fuji"
        ]

        self.aliases = {
            "einstein": "Albert Einstein",
            "tesla": "Nikola Tesla",
            "nicola tesla": "Nikola Tesla",
            "edison": "Thomas Edison",
            "hawking": "Stephen Hawking",
            "turing": "Alan Turing",
            "lovelace": "Ada Lovelace",
            "sultan ahmed": "Sultan Ahmed Mosque",
            "blue mosque": "Sultan Ahmed Mosque",
            "hagia sophia": "Hagia Sophia",
            "taj mahal": "Taj Mahal",
            "eiffel tower": "Eiffel Tower"
        }

    def _contains_pronoun(self, query):
        return bool(re.search(r"\b(he|him|his|she|her|it|there|they|them|their)\b", query, re.I))

    def _find_entity(self, text):
        text_l = text.lower()

        for alias, canonical in self.aliases.items():
            if alias in text_l:
                return canonical

        for entity in self.known_entities:
            if entity.lower() in text_l:
                return entity

        return None

    def _last_entity_from_user_history(self, chat_history):
        user_messages = [
            m.get("content", "")
            for m in chat_history
            if m.get("role") == "user"
        ]

        last_entity = None

        for msg in user_messages:
            entity = self._find_entity(msg)
            if entity:
                last_entity = entity

        return last_entity

    def rewrite_query(self, query, chat_history):
        """
        Safe query rewriting:
        - If query has explicit entity, return it unchanged.
        - If query has pronoun, replace with last user-mentioned entity.
        - Otherwise return original query.
        """

        if not chat_history:
            return query

        # 1. Yeni sorguda açık entity varsa history kullanma
        explicit_entity = self._find_entity(query)
        if explicit_entity:
            return query

        # 2. Pronoun yoksa rewrite yapma
        if not self._contains_pronoun(query):
            return query

        # 3. Pronoun varsa son user entity'sini kullan
        last_entity = self._last_entity_from_user_history(chat_history)
        if not last_entity:
            return query

        rewritten = query

        rewritten = re.sub(r"\b(he|him|his|she|her|they|them|their)\b", last_entity, rewritten, flags=re.I)
        rewritten = re.sub(r"\b(it|there)\b", last_entity, rewritten, flags=re.I)

        return rewritten

    def generate_answer(self, query, context):
        if not context or not context.strip():
            return "I don't know.", 0

        context = context[:10000]

        system_msg = """
You are BeeBrain, a helpful local Wikipedia RAG assistant.

Answer using ONLY the provided context.

Rules:
- Do not use outside knowledge.
- Do not give one-word answers.
- For "Who is" or "What is" questions, write a 3-5 sentence summary.
- For comparison questions, compare using only facts from the context.
- If the context contains partial relevant information, answer with that partial information.
- Say exactly "I don't know." only if there is no relevant information.
"""

        user_msg = f"""
Context:
{context}

Question:
{query}

Answer in complete sentences:
"""

        start_tm = time.time()

        try:
            response = ollama.generate(
                model=self.model_name,
                system=system_msg,
                prompt=user_msg,
                options={
                    "temperature": 0.2,
                    "num_predict": 400
                }
            )

            latency = round(time.time() - start_tm, 2)
            answer = response.get("response", "").strip()

            if not answer:
                return "I don't know.", latency

            if len(answer.split()) < 5 and "I don't know" not in answer:
                retry_prompt = f"""
The previous answer was too short: "{answer}"

Using ONLY the context below, write a 3-5 sentence answer.

Context:
{context[:3000]}

Question:
{query}

Answer:
"""
                retry_res = ollama.generate(
                    model=self.model_name,
                    system=system_msg,
                    prompt=retry_prompt,
                    options={
                        "temperature": 0.2,
                        "num_predict": 300
                    }
                )

                answer = retry_res.get("response", "").strip() or answer

            return answer, latency

        except Exception as e:
            return f"An error occurred in the generation engine: {str(e)}", 0