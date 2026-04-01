import asyncio
import os
import socket
import sys
from multiprocessing import Process
from devmate.agent import DevMateAgent
from devmate.rag import ingest_docs
from devmate.search_server import run_server
from devmate.logger import get_logger

logger = get_logger(__name__)

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            return s.connect_ex(("localhost", port)) == 0
        except socket.error:
            return False

async def run_cli():
    logger.info("Starting DevMate CLI Orchestrator...")
    
    # 1. 索引文档
    ingest_docs("docs")

    # 2. 自动管理后台搜索服务器 (MCP)
    server_process = None
    if not is_port_in_use(8000):
        logger.info("Search server (MCP) not detected on port 8000. Launching in background...")
        server_process = Process(target=run_server, daemon=True)
        server_process.start()
        
        # 等待就绪
        for _ in range(15):
            if is_port_in_use(8000):
                logger.info("Search server is now ready.")
                break
            await asyncio.sleep(1)

    # 3. 启动 Agent
    agent = DevMateAgent()
    try:
        mcp_host = os.environ.get("MCP_SERVER_HOST", "localhost")
        await agent.initialize(f"http://{mcp_host}:8000/mcp")
        
        logger.info("Agent ready. Type your request.")
        logger.info("To exit, type 'exit', 'quit', or 'q'.")

        while True:
            try:
                user_input = await asyncio.to_thread(sys.stdin.readline)
                if not user_input:
                    break
                
                query = user_input.strip()
                if query.lower() in ["exit", "quit", "q"]:
                    break
                if not query:
                    continue

                response = await agent.chat(query)
                logger.info(f"Agent Response: {response}")
            except EOFError:
                break
    finally:
        await agent.shutdown()
        if server_process and server_process.is_alive():
            server_process.terminate()
        logger.info("DevMate shut down.")

if __name__ == "__main__":
    asyncio.run(run_cli())
