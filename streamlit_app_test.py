import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8501"

st.title("📄 RAG Chatbot with Document Upload")

# File upload
uploaded_file = st.file_uploader("Upload a PDF document", type="pdf")

if uploaded_file and st.button("Upload"):
    files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
    response = requests.post(f"{BACKEND_URL}/upload/", files=files)
    
    if response.status_code == 200:
        st.success("File uploaded and processed!")
    else:
        st.error("Upload failed.")

# Chat input
query = st.text_input("Ask a question about the document:")

if query and st.button("Ask"):
    response = requests.post(f"{BACKEND_URL}/chat/", data={"query": query}).json()
    st.write("### 🤖 AI Response:")
    st.write(response["response"])
    st.write("### 📌 Sources:")
    for doc in response["sources"]:
        st.write(f"- {doc}")
