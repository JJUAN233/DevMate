from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from .config import get_config
from .logger import get_logger

logger = get_logger(__name__)
config = get_config()
model_cfg = config.get("model", {})
vector_dir = config.get("vectorstore", {}).get("persist_directory", "./chroma_db")


def _get_collection():
    """Retrieve or create the ChromaDB collection for local docs."""
    client = chromadb.PersistentClient(path=vector_dir)
    
    # Force use of SiliconFlow Embedding API
    embedding_fn = OpenAIEmbeddingFunction(
        api_key=model_cfg.get("api_key", ""),
        api_base=model_cfg.get("ai_base_url", "https://api.siliconflow.cn/v1"),
        model_name=model_cfg.get("embedding_model_name", "BAAI/bge-large-zh-v1.5")
    )
    
    return client.get_or_create_collection(
        name="docs", embedding_function=embedding_fn
    )


def ingest_docs(docs_dir: str = "docs"):
    """Parse and index local markdown or text documents from the docs dir."""
    path = Path(docs_dir)
    if not path.exists() or not path.is_dir():
        logger.warning(f"Docs directory '{docs_dir}' not found. Skipping ingestion.")
        return

    collection = _get_collection()
    documents = []
    ids = []
    metadatas = []

    for filepath in path.glob("**/*.*"):
        if filepath.suffix not in (".md", ".txt"):
            continue

        logger.info("Ingesting document: %s", filepath)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Simple chunking by paragraph
            chunks = [c.strip() for c in content.split("\\n\\n") if len(c.strip()) > 10]
            for i, chunk in enumerate(chunks):
                doc_id = f"{filepath.name}_{i}"
                documents.append(chunk)
                ids.append(doc_id)
                metadatas.append({"source": str(filepath), "chunk_index": i})

        except Exception as e:
            logger.error("Failed to ingest %s: %s", filepath, e)

    if documents:
        # Upsert allows avoiding duplicates if same doc is ingested again
        collection.upsert(documents=documents, ids=ids, metadatas=metadatas)
        logger.info("Successfully ingested %d chunks.", len(documents))
    else:
        logger.info("No valid text documents found to ingest.")


def search_knowledge_base(query: str, n_results: int = 3) -> str:
    """Search local documentation vector database."""
    logger.info("Searching local docs for: %s", query)
    try:
        collection = _get_collection()
        if collection.count() == 0:
            return "The vector database is currently empty. No internal docs available."

        results = collection.query(query_texts=[query], n_results=n_results)

        formatted = []
        if results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            for doc, meta in zip(docs, metas):
                source = meta.get("source", "Unknown")
                formatted.append(f"[Source: {source}]:\\n{doc}")

        if not formatted:
            return "No relevant local documentation found."

        return "\\n\\n".join(formatted)
    except Exception as e:
        logger.error("Error during knowledge base search: %s", e)
        return f"Error occurred during search: {e}"
