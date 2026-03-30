from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
import uvicorn
from contextlib import asynccontextmanager

from .config import get_config
from .logger import get_logger

from tavily import AsyncTavilyClient

logger = get_logger(__name__)

config = get_config()
tavily_api_key = config.get("search", {}).get("tavily_api_key", "")

# Initialize FastMCP Server natively. Host 0.0.0.0 needed for Docker.
mcp = FastMCP("TavilySearchServer", host="0.0.0.0", port=8000, streamable_http_path="/mcp")

@mcp.tool()
async def search_web(query: str) -> str:
    """Search the web using Tavily Search API. Provide a concise search query."""
    logger.info("Triggered search tool with query: %s", query)
    try:
        client = AsyncTavilyClient(api_key=tavily_api_key)
        response = await client.search(query=query)
        results = response.get("results", [])
        formatted_results = "\n".join([f"- {r.get('title', '')}: {r.get('content', '')}" for r in results])
        return formatted_results if formatted_results else "No results found."
    except Exception as e:
        logger.error("Web search failed: %s", e)
        return f"Error during web search: {e}"

def run_server(port: int = 8000):
    logger.info("Starting FastMCP Streamable HTTP server on port %s", port)
    # FastMCP encapsulates the task group and uvicorn running
    mcp.run("streamable-http")

if __name__ == "__main__":
    run_server()
