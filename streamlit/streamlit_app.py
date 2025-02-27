import streamlit as st
import requests

API_URL = "http://backend:8501"


st.set_page_config(page_title="RAG Chatbot", layout="wide")


# Sidebar - File Upload & Options
st.sidebar.title("📂 Upload Documents")
uploaded_file = st.sidebar.file_uploader("Upload a document", type=["pdf", "txt", "docx"])

if uploaded_file and "file_uploaded" not in st.session_state:
    files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
    response = requests.post(f"{API_URL}/upload/", files=files)
    
    if response.status_code == 200:
        st.sidebar.success("File uploaded and processed!")
        st.session_state.file_uploaded = True  # Prevent duplicate uploads
    else:
        st.sidebar.error("Upload failed.")

use_document = st.sidebar.checkbox("Use uploaded document for answers", value=True)

st.title("💬 RAG Chatbot")

# Session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])



# User input
if user_input := st.chat_input("Ask a question..."):
    # Store user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)
        
    # Send request to backend
    payload = {"query": user_input, "use_document": use_document}
    response = requests.post(f"{API_URL}/chat/", json=payload)
    data = response.json()

    # Extract bot response and sources
    bot_response = data.get("response", "I couldn't find an answer.")
    sources = data.get("sources", [])

    # Format sources neatly
    sources_markdown = "\n".join(
        [f"- **[{src['metadata'].get('source', 'Unknown')}]**: {src['page_content']}" for src in sources]
    )

    # Full chatbot response
    final_response = f"**Response:**\n{bot_response}\n\n---\n**📜 Sources:**\n{sources_markdown}"

    # Add bot response
    with st.chat_message("assistant"):
        st.markdown(bot_response)

        # Collapsible sources section
        if sources:
            with st.expander("📜 Sources (Click to expand)"):
                for src in sources:
                    st.markdown(sources_markdown)

    # Store in session history
    st.session_state.messages.append({"role": "assistant", "content": final_response})