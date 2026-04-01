import tomllib
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("devmate.config")


def validate_config(config_data: dict):
    """
    Ensure all required fields exist in the configuration.
    Uses logger.error for reporting to comply with 'no print' rule.
    """
    required_fields = {
        "model": ["ai_base_url", "api_key", "model_name", "embedding_model_name"],
        "search": ["tavily_api_key"],
        "langsmith": ["langchain_tracing_v2", "langchain_api_key"],
        "skills": ["skills_dir"],
        "vectorstore": ["persist_directory"]
    }

    missing_keys = []
    for section, keys in required_fields.items():
        if section not in config_data:
            missing_keys.append(f"[{section}] section missing")
            continue
        
        for key in keys:
            if key not in config_data[section]:
                missing_keys.append(f"[{section}] -> {key} missing")

    if missing_keys:
        logger.error("CRITICAL CONFIGURATION ERROR: Missing required fields in config.toml")
        for m in missing_keys:
            logger.error(f" - Missing: {m}")
        
        raise RuntimeError("Application failed to start due to missing configuration. See logs above.")


def load_config(config_path: str | Path = "config.toml") -> dict:
    """Load and strictly validate the TOML configuration file."""
    path = Path(config_path)
    if not path.exists():
        logger.error("Config file not found: %s", path)
        raise FileNotFoundError(f"Missing configuration file at {path}")

    with open(path, "rb") as f:
        data = tomllib.load(f)
    
    validate_config(data)
    return data


# Global config instance for easy import
config_data = load_config()


def get_config() -> dict[str, dict]:
    """Get the loaded configuration."""
    return config_data


def set_langsmith_env_vars():
    """Set LangSmith environment variables from config."""
    import os

    ls_config = config_data.get("langsmith", {})
    if ls_config.get("langchain_tracing_v2", "false").lower() == "true":
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = ls_config.get("langchain_api_key", "")
        if "langchain_project" in ls_config:
            os.environ["LANGCHAIN_PROJECT"] = ls_config["langchain_project"]
    else:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
