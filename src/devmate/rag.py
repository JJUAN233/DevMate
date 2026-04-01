from pathlib import Path
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from .config import get_config
from .logger import get_logger

logger = get_logger(__name__)
config = get_config()

# 核心配置区域
model_cfg = config.get("model", {})
vector_dir = config.get("vectorstore", {}).get("persist_directory", "./chroma_db")


def _get_collection():
    """Retrieve or create the ChromaDB collection based on config.toml."""
    client = chromadb.PersistentClient(path=vector_dir)
    
    api_key = model_cfg.get("api_key")
    api_base = model_cfg.get("ai_base_url")
    model_name = model_cfg.get("embedding_model_name")

    if not all([api_key, api_base, model_name]):
        logger.error("Embedding configuration missing in config.toml (api_key, ai_base_url, or embedding_model_name).")
        raise ValueError("Incomplete Embedding configuration.")

    embedding_fn = OpenAIEmbeddingFunction(
        api_key=api_key,
        api_base=api_base,
        model_name=model_name
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

            # Improved chunking: split by paragraphs, then sub-split if too long
            raw_chunks = [c.strip() for c in content.split("\n\n") if len(c.strip()) > 10]
            
            for i, raw_chunk in enumerate(raw_chunks):
                # If a single paragraph is too long (> 800 chars), further split it
                # to avoid API limit (approx 512 tokens)
                MAX_CHUNK_LEN = 800 
                sub_chunks = [raw_chunk[k:k+MAX_CHUNK_LEN] for k in range(0, len(raw_chunk), MAX_CHUNK_LEN)]
                
                for j, sub_chunk in enumerate(sub_chunks):
                    doc_id = f"{filepath.name}_{i}_{j}"
                    documents.append(sub_chunk)
                    ids.append(doc_id)
                    metadatas.append({
                        "source": str(filepath), 
                        "chunk_index": i,
                        "sub_chunk_index": j
                    })

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
                formatted.append(f"[Source: {source}]:\n{doc}")

        if not formatted:
            return "No relevant local documentation found."

        return "\n\n".join(formatted)
    except Exception as e:
        logger.error("Error during knowledge base search: %s", e)
        return f"Error occurred during search: {e}"
