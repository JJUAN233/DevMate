from pathlib import Path
from langchain_core.tools import tool

from .config import get_config
from .logger import get_logger

logger = get_logger(__name__)

config = get_config()
skills_dir_path = config.get("skills", {}).get("skills_dir", ".skills")
skills_dir = Path(skills_dir_path)

# Ensure directory exists on load
skills_dir.mkdir(parents=True, exist_ok=True)


@tool
def list_skills() -> str:
    """List all available stored skills in the repository."""
    skills = []
    if skills_dir.exists():
        for d in skills_dir.iterdir():
            if d.is_dir() and (d / "SKILL.md").exists():
                skills.append(d.name)

    if not skills:
        return "No skills currently available."

    return "Available skills: " + ", ".join(skills)


@tool
def read_skill(skill_name: str) -> str:
    """Read the instructions of a specific skill by its name."""
    logger.info("Reading skill: %s", skill_name)
    skill_file = skills_dir / skill_name / "SKILL.md"
    if skill_file.exists():
        with open(skill_file, "r", encoding="utf-8") as f:
            return f.read()
    return f"Skill '{skill_name}' not found."


@tool
def save_skill(skill_name: str, content: str) -> str:
    """Save a successful task pattern as a new skill to be reused later.
    Provide a concise skill_name (folder name) and markdown content explaining how to perform the task.
    """
    logger.info("Saving new skill: %s", skill_name)
    try:
        target_dir = skills_dir / skill_name
        target_dir.mkdir(parents=True, exist_ok=True)
        with open(target_dir / "SKILL.md", "w", encoding="utf-8") as f:
            f.write(content)
        return f"Skill '{skill_name}' successfully saved."
    except Exception as e:
        logger.error("Failed to save skill %s: %s", skill_name, e)
        return f"Failed to save skill: {e}"
