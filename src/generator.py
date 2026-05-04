import ollama
import time


class WikiGenerator:
    def __init__(self, model_name="llama3.2"):
        self.model_name = model_name

    def rewrite_query(self, query, chat_history):
        """
        Chat geçmişini kullanarak zamirli / eksik soruları bağımsız sorguya çevirir.
        Örn:
        "when was he born" -> "When was Albert Einstein born?"
        """

        if not chat_history:
            return query

        history_context = "\n".join(
            [f"{m['role']}: {m['content']}" for m in chat_history[-4:]]
        )

        rewrite_prompt = f"""
Rewrite the last question as a standalone search query using the chat history.

Rules:
- Do NOT answer the question.
- Return ONLY the rewritten query.
- Replace pronouns like he, she, him, her, it, there with the correct entity name.
- Fix obvious spelling mistakes in famous names, for example Nicola Tesla -> Nikola Tesla.
- If the question is already standalone, return it unchanged.

Chat history:
{history_context}

Last question:
{query}

Standalone query:
"""

        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=rewrite_prompt,
                options={
                    "temperature": 0,
                    "num_predict": 60
                }
            )

            rewritten = response.get("response", "").strip()

            if not rewritten:
                return query

            # Model bazen açıklama eklerse ilk satırı al
            rewritten = rewritten.split("\n")[0].strip()

            # Tırnakları temizle
            rewritten = rewritten.strip('"').strip("'")

            return rewritten if rewritten else query

        except Exception:
            return query

    def generate_answer(self, query, context):
        """
        Retrieved context'e dayanarak cevap üretir.
        Context dışı bilgi kullanmaz.
        """

        if not context or not context.strip():
            return "I don't know.", 0

        context = context[:9000]

        system_msg = """
You are BeeBrain, a local Wikipedia RAG assistant.

You must answer using ONLY the provided context.

Rules:
- Do not use outside knowledge.
- Do not give one-word answers.
- If the question asks "who is", "what is", or asks for an overview, write a concise 2-4 sentence summary.
- If the question asks "when", "where", or "what did", answer directly and add one short supporting sentence if useful.
- If the question asks to compare, compare the entities using only facts from the context.
- If the context contains partial relevant information, answer with that partial information.
- Only say exactly "I don't know." when the context has no relevant information at all.
"""

        user_msg = f"""
Context:
{context}

Question:
{query}

Write a helpful answer in complete sentences:
"""

        start_time = time.time()

        response = ollama.generate(
            model=self.model_name,
            system=system_msg,
            prompt=user_msg,
            options={
                "temperature": 0.2,
                "num_predict": 350
            }
        )

        latency = round(time.time() - start_time, 2)
        answer = response.get("response", "").strip()

        if not answer:
            return "I don't know.", latency

        # Çok kısa cevapları engelle
        if len(answer.split()) <= 3 and answer.lower() != "i don't know.":
            retry_prompt = f"""
The previous answer was too short: "{answer}"

Using ONLY the context below, write a 2-4 sentence answer.
If there is no relevant information, say exactly: I don't know.

Context:
{context}

Question:
{query}

Answer:
"""

            retry_response = ollama.generate(
                model=self.model_name,
                system=system_msg,
                prompt=retry_prompt,
                options={
                    "temperature": 0.2,
                    "num_predict": 350
                }
            )

            answer = retry_response.get("response", "").strip() or answer

        return answer, latency