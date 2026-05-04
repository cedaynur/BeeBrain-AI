import streamlit as st
import time
from src.retriever import WikiRetriever
from src.generator import WikiGenerator


st.set_page_config(
    page_title="BeeBrain AI | Hive Intelligence",
    page_icon="🐝",
    layout="centered",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
.stChatMessage {
    border-radius: 12px;
    border: 1px solid rgba(128, 128, 128, 0.2);
    margin-bottom: 10px;
}

.source-tag {
    display: inline-block;
    padding: 4px 10px;
    margin-right: 5px;
    margin-top: 8px;
    border-radius: 6px;
    background-color: rgba(240, 173, 78, 0.1);
    color: #f0ad4e;
    font-size: 0.75rem;
    border: 1px solid #f0ad4e;
    font-family: 'Courier New', Courier, monospace;
}

.meta-box {
    font-size: 0.8rem;
    color: gray;
    margin-top: 6px;
}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_beebrain_engine():
    retriever = WikiRetriever()
    generator = WikiGenerator()
    return retriever, generator


retriever, generator = load_beebrain_engine()


if "messages" not in st.session_state:
    st.session_state.messages = []


with st.sidebar:
    st.title("🐝 BeeBrain")
    st.caption("Local Wikipedia RAG Assistant")
    st.markdown("---")

    st.write("**LLM:** Llama 3.2")
    st.write("**Embedding:** nomic-embed-text")
    st.write("**Vector DB:** Chroma")
    st.write("**Status:** 🟢 Operational")

    st.markdown("---")

    show_context = st.toggle("Show retrieved context", value=False)
    show_rewritten_query = st.toggle("Show rewritten query", value=True)

    st.markdown("---")

    example = st.selectbox(
        "Example questions",
        [
            "",
            "Who is Albert Einstein?",
            "When was he born?",
            "Tell me about Sultan Ahmed Mosque.",
            "Where is Hagia Sophia?",
            "Compare Nikola Tesla and Thomas Edison.",
            "Who is the president of Mars?"
        ]
    )

    if st.button("Use Example", use_container_width=True) and example:
        st.session_state.pending_input = example
        st.rerun()

    if st.button("Clear Chat Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption("ITU BLG Course Project")


st.subheader("BeeBrain Intelligence Interface")
st.caption("Context-Aware Local Wikipedia RAG System")


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant":
            if msg.get("meta"):
                meta = msg["meta"]
                st.markdown(
                    f"""
                    <div class="meta-box">
                    Category: {meta.get("category", "unknown")} |
                    Latency: {meta.get("latency", "-")}s
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            if msg.get("sources"):
                src_html = "".join(
                    [f'<span class="source-tag">{s}</span>' for s in msg["sources"]]
                )
                st.markdown(src_html, unsafe_allow_html=True)

            with st.expander("📋 Copy response text"):
                st.code(msg["content"], language=None)

            if show_context and msg.get("context"):
                with st.expander("Retrieved Context"):
                    st.write(msg["context"][:3000])


pending_input = st.session_state.pop("pending_input", None)

user_input = pending_input or st.chat_input("Ask BeeBrain...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response_container = st.empty()

        with st.status("🐝 BeeBrain is retrieving and synthesizing...", expanded=False) as status:
            start_tm = time.time()

            history_before_current = st.session_state.messages[:-1]

            standalone_query = generator.rewrite_query(
                user_input,
                history_before_current
            )

            search_data = retriever.search(standalone_query)

            raw_answer, gen_latency = generator.generate_answer(
                standalone_query,
                search_data["context"]
            )

            total_latency = round(time.time() - start_tm, 2)

            clean_sources = [
                s.replace("_", " ").title()
                for s in search_data.get("sources", [])
            ]

            status.update(
                label=f"Analysis complete in {total_latency}s",
                state="complete"
            )

        words = raw_answer.split()
        streamed_text = ""

        for word in words:
            streamed_text += word + " "
            response_container.markdown(streamed_text + "▌")
            time.sleep(0.025)

        response_container.markdown(raw_answer)

        if show_rewritten_query and standalone_query != user_input:
            st.caption(f"Rewritten query: {standalone_query}")

        st.markdown(
            f"""
            <div class="meta-box">
            Category: {search_data.get("category", "unknown")} |
            Latency: {total_latency}s
            </div>
            """,
            unsafe_allow_html=True
        )

        if clean_sources:
            src_html = "".join(
                [f'<span class="source-tag">{s}</span>' for s in clean_sources]
            )
            st.markdown(src_html, unsafe_allow_html=True)

        with st.expander("📋 Copy response text"):
            st.code(raw_answer, language=None)

        if show_context:
            with st.expander("Retrieved Context"):
                st.write(search_data["context"][:3000])

        st.session_state.messages.append({
            "role": "assistant",
            "content": raw_answer,
            "sources": clean_sources,
            "context": search_data.get("context", ""),
            "meta": {
                "category": search_data.get("category", "unknown"),
                "latency": total_latency,
                "rewritten_query": standalone_query
            }
        })