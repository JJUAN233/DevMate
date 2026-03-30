import tomllib
from pathlib import Path


def load_config(config_path: str | Path = "config.toml") -> dict:
    """Load the TOML configuration file."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "rb") as f:
        return tomllib.load(f)


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
