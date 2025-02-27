from flask import Flask, request, jsonify
import os
import shutil
import chromadb
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_mistralai import MistralAIEmbeddings
from langchain_mistralai import ChatMistralAI
from langchain_core.output_parsers import StrOutputParser
# from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import RunnableParallel
# from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from dotenv import load_dotenv
import chromadb.utils.embedding_functions as embedding_functions
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain



load_dotenv()

app = Flask(__name__)

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Connect to ChromaDB
CHROMA_HOST = "http://chromadb:8000"
chroma_client = chromadb.HttpClient(host="chromahost", port="8000")

class CustomMistralAIEmbeddings(MistralAIEmbeddings):

    def __init__(self, api_key, *args, **kwargs):
        super().__init__(api_key=api_key, *args, **kwargs)
        
    def _embed_documents(self, texts):
        return super().embed_documents(texts)  # <--- use OpenAIEmbedding's embedding function

    def __call__(self, input):
        return self._embed_documents(input)    # <--- get the embeddings
    
# Initialize LLM & embeddings
embeddings = MistralAIEmbeddings(model="mistral-embed")


mistral_ef = embedding_functions.chroma_langchain_embedding_function.create_langchain_embedding(embeddings)
collection = chroma_client.get_or_create_collection(name="rag_docs",
                                                    embedding_function=mistral_ef
                                                    )

# Ensure the collection is empty
# Retrieve all document IDs
all_docs = collection.get()
all_ids = all_docs["ids"]  # Extract IDs

if all_ids:
    collection.delete(ids=all_ids)
    print("✅ All documents deleted successfully!")
else:
    print("⚠️ No documents found in the collection.")

    
llm = ChatMistralAI(model="open-mistral-7b")
vectorstore = Chroma(
    client = chroma_client,
    collection_name = "rag_docs",
    embedding_function = embeddings
)

retriever = vectorstore.as_retriever(search_kwargs={'k': 3})

@app.route("/upload/", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files["file"]
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    file.save(file_path)

    # Extract text from PDF
    if file.filename.endswith(".pdf"):
        with open(file_path, "rb") as f:
            pdf_reader = PdfReader(f)
            text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    
        # Split text into chunks and store in ChromaDB
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = text_splitter.split_text(text)

        collection.add(ids=[f"{file.filename}_{i}" for i in range(len(chunks))], documents=chunks)
        
        return jsonify({"message": "File uploaded and processed!", "chunks": len(chunks)})

    return jsonify({"message": "File uploaded but not processed (Unsupported format)"}), 400

@app.route("/chat/", methods=["POST"])
def chat():
    data = request.json
    query = data.get("query", "")
    use_document = data.get("use_document", True)

    # query = request.form.get("query")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Prompt
    prompt = PromptTemplate.from_template(
        
        """
        Answer the question based only on the following context from 
        an uploaded document by the user:
        {context}
        Question: {question}
        
        """
        
    )
    # Post-processing
    def format_docs(result):
        return "\n\n".join(doc.page_content for doc in result)

    # Chain
    rag_chain = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | prompt
        | llm
        | StrOutputParser()
    )

    rag_chain_with_source = RunnableParallel(
    {"context": retriever, "question": RunnablePassthrough()}
    ).assign(answer=rag_chain)
    
    chain_response = rag_chain_with_source.invoke(query)

    documents = chain_response["context"]
    serializable_documents = [
        {
            "page_content": doc.page_content,
            "metadata": doc.metadata  # Ensure metadata is also serializable
        }
        for doc in documents
    ]

    if documents:
        response = chain_response["answer"]
    
        print(documents)
        return jsonify(
            {
                "query": query,
                "response": response,
                "sources": serializable_documents
            }
        )
    
    
    return jsonify({"query": query, "response": response, "source": "No relevant sources from the document"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8501)