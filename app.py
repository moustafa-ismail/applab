import streamlit as st
import chromadb

# Connect to ChromaDB
CHROMA_HOST = "http://chromadb:8000"
client = chromadb.HttpClient(host=CHROMA_HOST.replace("http://", ""))

# Create or get a collection
collection = client.get_or_create_collection(name="rag_demo")

# Streamlit UI
st.title("🔍 Simple RAG Demo with ChromaDB")

# Text input for adding data
text_input = st.text_input("Add a sentence to the database:")
if st.button("Store in ChromaDB"):
    if text_input:
        collection.add(ids=[text_input], documents=[text_input])
        st.success("Stored successfully!")

# Query input for retrieving similar texts
query = st.text_input("Enter a query to find similar sentences:")
if st.button("Search"):
    if query:
        results = collection.query(query_texts=[query], n_results=3)
        st.write("### Top Matches:")
        for doc in results["documents"][0]:
            st.write(f"- {doc}")

# Show stored data
if st.button("Show all stored data"):
    stored_data = collection.get()
    st.write("### Stored Sentences:")
    for doc in stored_data["documents"]:
        st.write(f"- {doc}")
