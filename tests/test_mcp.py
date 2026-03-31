import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from devmate.logger import get_logger

logger = get_logger(__name__)

async def test_conn():
    try:
        url = 'http://localhost:8000/mcp'
        async with streamable_http_client(url=url) as transport:
            async with ClientSession(transport[0], transport[1]) as session:
                await session.initialize()
                logger.info("Successfully connected and initialized MCP session via Official SDK!")
    except Exception as e:
        logger.error(f"Failed to reach MCP server: {e}")

if __name__ == "__main__":
    asyncio.run(test_conn())
