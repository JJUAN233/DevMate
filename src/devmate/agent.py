import os
from contextlib import AsyncExitStack

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from langchain_mcp_adapters.tools import load_mcp_tools

from langchain_core.tools import tool

from .config import get_config, set_langsmith_env_vars
from .logger import get_logger
from .rag import search_knowledge_base
from .skills import list_skills, read_skill, save_skill

logger = get_logger(__name__)


@tool
def create_file(file_path: str, content: str) -> str:
    """Create a new file or overwrite an existing file at the specified file_path with the given content.
    Can be used to generate scripts, project files etc."""
    logger.info("Creating file: %s", file_path)
    try:
        dir_name = os.path.dirname(file_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File {file_path} created successfully."
    except Exception as e:
        logger.error("Failed to create file %s: %s", file_path, e)
        return f"Failed to create file: {e}"


@tool
def read_file(file_path: str) -> str:
    """Read local file content."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"File reading failed: {e}"


@tool
def search_local_docs(query: str) -> str:
    """Search the local documentation vector database (RAG).
    Use this for internal company guidelines, local templates, etc."""
    return search_knowledge_base(query)


class DevMateAgent:
    def __init__(self):
        set_langsmith_env_vars()
        self.config = get_config()
        self._exit_stack = AsyncExitStack()
        self.agent_executor = None
        self.llm = self._setup_llm()

    def _setup_llm(self):
        model_config = self.config.get("model", {})
        base_url = model_config.get("ai_base_url")
        api_key = model_config.get("api_key")
        model_name = model_config.get("model_name", "gpt-4o")

        logger.info("Initializing LLM %s via ChatOpenAI", model_name)
        # We allow None values to be handled by ChatOpenAI default env vars if config is empty
        kwargs = {"model": model_name}
        if api_key:
            kwargs["api_key"] = api_key
        if base_url:
            kwargs["base_url"] = base_url

        return ChatOpenAI(**kwargs)

    async def initialize(self, mcp_server_url: str = "http://localhost:8000/mcp"):
        logger.info(
            "Initializing Agent and connecting to MCP Streamable HTTP: %s",
            mcp_server_url,
        )
        try:
            # MUST use Streamable HTTP per constraints
            client_ctx = streamable_http_client(url=mcp_server_url)
            transport = await self._exit_stack.enter_async_context(client_ctx)

            # Start mcp session
            # transport from streamable_http_client provides a tuple of (read_stream, write_stream, _ )
            self.session = await self._exit_stack.enter_async_context(
                ClientSession(transport[0], transport[1])
            )
            await self.session.initialize()

            # Load remote MCP tools via adapter
            mcp_tools = await load_mcp_tools(self.session)

            # Combine all tools
            my_tools = [
                create_file,
                read_file,
                search_local_docs,
                list_skills,
                read_skill,
                save_skill,
            ] + mcp_tools

            prompt = (
                "You are DevMate, an AI orchestrator and assistant. "
                "You have access to web search via Tavily (provided by MCP Streamable HTTP Server), "
                "local documents via RAG, local file management tools, and an Agent Skills library. "
                "Whenever user asks you to build or do something:\\n"
                "1. Check if an existing skill fits.\\n"
                "2. Check local docs (via search_local_docs) for internal guidelines.\\n"
                "3. Search the web for latest practices if necessary.\\n"
                "4. Generate cleanly structured code and save using create_file.\\n"
                "5. Save the procedure as a skill if it's a new useful pattern."
            )
            self.agent_executor = create_react_agent(self.llm, my_tools, prompt=prompt)
            logger.info("Agent initialized with %d tools", len(my_tools))
        except Exception as e:
            logger.error("Failed to initialize Agent: %s", e)
            raise e

    async def chat(self, user_input: str) -> str:
        if not self.agent_executor:
            raise ValueError("Agent not initialized")
        logger.info("Processing user request: %s", user_input)

        inputs = {"messages": [("user", user_input)]}
        final_msg = ""
        async for s in self.agent_executor.astream(inputs, stream_mode="values"):
            message = s["messages"][-1]
            if isinstance(message, AIMessage) and message.content:
                final_msg = message.content

        logger.info("Agent execution completed.")
        return final_msg

    async def shutdown(self):
        await self._exit_stack.aclose()
        logger.info("Agent resources cleaned up")
