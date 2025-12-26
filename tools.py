import os
from dotenv import load_dotenv
load_dotenv()

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

# Web Search Tool
web_search_tool = DuckDuckGoSearchRun()

def search_web(query: str) -> str:
    """Performs a web search for the given query."""
    try:
        return web_search_tool.invoke(query)
    except Exception as e:
        return f"Graceful Error: Unable to perform web search. Details: {str(e)}"

# RAG Retrieval Tool (This is just mock data, currently it can only answers one question: "Who is your creator?")
def retrieve_documents(query: str) -> str:
    """Retrieves relevant documents from Pinecone. Currently, it only contains the creator’s content; other documents are not included here."""
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        index_name = os.getenv("PINECONE_INDEX_NAME")
        
        if not index_name:
             return "Error: PINECONE_INDEX_NAME not set."

        vectorstore = PineconeVectorStore(
            index_name=index_name,
            embedding=embeddings
        )
        
        results = vectorstore.similarity_search(query, k=3)
        return "\n\n".join([doc.page_content for doc in results])
    except Exception as e:
        return f"Error executing document retrieval: {str(e)}"

# Wikipedia Tool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
wikipedia_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

def search_wikipedia(query: str) -> str:
    """Searches Wikipedia for the query."""
    try:
        return wikipedia_tool.invoke(query)
    except Exception as e:
        return f"Error executing Wikipedia search: {str(e)}"

# Arxiv Tool
from langchain_community.tools import ArxivQueryRun
from langchain_community.utilities import ArxivAPIWrapper
arxiv_tool = ArxivQueryRun(api_wrapper=ArxivAPIWrapper())

def search_arxiv(query: str) -> str:
    """Searches Arxiv for academic papers."""
    try:
        return arxiv_tool.invoke(query)
    except Exception as e:
        return f"Error executing Arxiv search: {str(e)}"

# Export tools list
tools = [search_web, retrieve_documents, search_wikipedia, search_arxiv]
