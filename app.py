import streamlit as st
import time
from src.retriever import WikiRetriever
from src.generator import WikiGenerator

# --- Page Configuration ---
st.set_page_config(
    page_title="BeeBrain AI | Hive Intelligence", 
    page_icon="🐝", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- Dynamic Styling (Tema Uyumlu CSS) ---
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
    /* Code block içindeki kopyalama butonunu daha belirgin yapar */
    code {
        color: #f0ad4e !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Engine Initialization ---
@st.cache_resource
def load_beebrain_engine():
    return WikiRetriever(), WikiGenerator()

retriever, generator = load_beebrain_engine()

# --- Session Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar Design ---
with st.sidebar:
    st.title("🐝 BeeBrain")
    st.caption("The Hive Intellectual Engine")
    st.markdown("---")
    st.write("**Core:** Llama 3.2 (3B)")
    st.write("**Status:** 🟢 Operational")
    st.markdown("---")
    
    if st.button("Purge Hive Memory", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.caption("ITU BLG Course Project")

# --- UI Header ---
st.subheader("BeeBrain Intelligence Interface")
st.caption("Context-Aware Neural RAG System")

# --- Chat Display Loop ---
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        # Eğer asistan mesajıysa, kopyalanabilir code block içinde göster
        if msg["role"] == "assistant":
            st.markdown(msg["content"])
            # Alternatif kopyalama: Metni seçilebilir bir kod bloğuna koyuyoruz
            with st.expander("📋 Click to copy response text"):
                st.code(msg["content"], language=None)
                
            if "sources" in msg and msg["sources"]:
                src_html = "".join([f'<span class="source-tag">{s}</span>' for s in msg["sources"]])
                st.markdown(src_html, unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# --- Active Chat Logic ---
if user_input := st.chat_input("Connect with the Hive..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response_container = st.empty()
        
        with st.status("🐝 BeeBrain is synthesizing...", expanded=False) as status:
            start_tm = time.time()
            
            # Memory-Augmented Search
            standalone_query = generator.rewrite_query(user_input, st.session_state.messages[:-1])
            search_data = retriever.search(standalone_query)
            
            # Contextual Generation
            raw_answer, _ = generator.generate_answer(standalone_query, search_data['context'])
            
            total_latency = round(time.time() - start_tm, 2)
            clean_sources = [s.replace("_", " ").title() for s in search_data['sources']]
            status.update(label=f"Analysis Complete in {total_latency}s", state="complete")

        # Simulated Streaming
        words = raw_answer.split()
        curr_text = ""
        for word in words:
            curr_text += word + " "
            response_container.markdown(curr_text + "▌")
            time.sleep(0.04)
        
        response_container.markdown(raw_answer)
        
        # Kopyalama için Expander ve Code Block ekliyoruz
        with st.expander("📋 Click to copy response text"):
            st.code(raw_answer, language=None)
        
        if clean_sources:
            src_html = "".join([f'<span class="source-tag">{s}</span>' for s in clean_sources])
            st.markdown(src_html, unsafe_allow_html=True)

        st.session_state.messages.append({
            "role": "assistant", 
            "content": raw_answer,
            "sources": clean_sources
        })