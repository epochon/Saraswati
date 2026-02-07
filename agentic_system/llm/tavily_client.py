from tavily import TavilyClient
import os

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def tavily_search(query):
    return client.search(query=query, max_results=5)
