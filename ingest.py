import os
import time
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

def ingest_data():
    """Ingests data/knowledge.txt into Pinecone."""
    file_path = "data/knowledge.txt"
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    print("Loading documents...")
    loader = TextLoader(file_path)
    docs = loader.load()

    print("Splitting text...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    print(f"Created {len(splits)} chunks.")

    print("Indexing to Pinecone...")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    if not index_name:
        print("Error: PINECONE_INDEX_NAME not set.")
        return
        
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Initialize Pinecone store (assumes index already exists)
    PineconeVectorStore.from_documents(
        documents=splits,
        embedding=embeddings,
        index_name=index_name
    )
    
    print("Ingestion complete.")

if __name__ == "__main__":
    ingest_data()
