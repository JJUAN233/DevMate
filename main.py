import asyncio
import sys
from devmate.agent import DevMateAgent
from devmate.rag import ingest_docs
from devmate.logger import get_logger

logger = get_logger(__name__)


async def run_cli():
    logger.info("Starting DevMate CLI...")

    # 1. Ingest local docs for RAG
    ingest_docs("docs")

    agent = DevMateAgent()
    try:
        # Assuming MCP Server is running locally via compose or separate process
        # Wait, inside docker-compose it will be named "mcp_server", but localhost works for manual test.
        import os

        mcp_host = os.environ.get("MCP_SERVER_HOST", "localhost")
        mcp_url = f"http://{mcp_host}:8000/mcp"

        await agent.initialize(mcp_server_url=mcp_url)
        logger.info("Agent ready. Type your request.")
        logger.info("To exit, type 'exit' or 'quit'.")

        while True:
            # We use logger to prompt, to avoid any print() calls.
            # Using asyncio.to_thread for stdin so we do not block event loop
            try:
                user_input = await asyncio.to_thread(sys.stdin.readline)
            except EOFError:
                break

            user_input = user_input.strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                break

            response = await agent.chat(user_input)
            logger.info("Agent Response:")
            logger.info(response)
            logger.info("--- End of Response ---")

    except Exception as e:
        logger.error("CLI encountered an error: %s", e)
    finally:
        await agent.shutdown()
        logger.info("DevMate shut down.")


if __name__ == "__main__":
    asyncio.run(run_cli())
