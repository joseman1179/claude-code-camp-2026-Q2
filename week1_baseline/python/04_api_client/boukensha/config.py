import os
from pathlib import Path

import yaml
from dotenv import load_dotenv


class Config:
    """Configuration loader for Boukensha.

    Resolves the config directory in this order:
      1. BOUKENSHA_DIR environment variable
      2. ~/.boukensha (default)
    """

    DEFAULT_DIR: Path = Path.home() / ".boukensha"

    # Default prompts shipped alongside the library code.
    PROMPTS_DIR: Path = Path(__file__).resolve().parent.parent / "prompts"

    def __init__(self) -> None:
        self.dir: str = self._resolve_dir()
        self._load_env()
        self.settings: dict = self._load_settings()

    # ---------- tasks -----------------------------------------------------

    def tasks(self, name: str | None = None) -> dict:
        """Return the full tasks hash, or a specific task's settings."""
        all_tasks: dict = self.dig("tasks") or {}
        if name:
            return all_tasks.get(name, {})
        return all_tasks

    @property
    def user_prompts_dir(self) -> str:
        """The user's prompts directory for task prompt overrides."""
        return str(Path(self.dir) / "prompts")

    # ---------- MUD connection --------------------------------------------

    @property
    def mud_host(self) -> str:
        return self.dig("mud", "host") or "localhost"

    @property
    def mud_port(self) -> int:
        return self.dig("mud", "port") or 4000

    @property
    def mud_username(self) -> str | None:
        return self.dig("mud", "username")

    @property
    def mud_password(self) -> str | None:
        return self.dig("mud", "password")

    # ---------- low-level helpers -----------------------------------------

    def dig(self, *keys: str):
        """Fetch a nested key path from settings, e.g. dig('mud', 'host')."""
        node = self.settings
        for key in keys:
            if isinstance(node, dict):
                node = node.get(key)
            else:
                return None
        return node

    def __str__(self) -> str:
        tasks_keys = ",".join(self.tasks().keys())
        return f"#<Boukensha::Config dir={self.dir} tasks={tasks_keys}>"

    def __repr__(self) -> str:
        return str(self)

    # ---------- private ---------------------------------------------------

    def _resolve_dir(self) -> str:
        raw: str | None = os.environ.get("BOUKENSHA_DIR")
        if raw:
            return str(Path(raw).resolve())
        return str(self.DEFAULT_DIR.resolve())

    def _load_env(self) -> None:
        env_file = Path(self.dir) / ".env"
        if env_file.exists():
            load_dotenv(env_file)

    def _load_settings(self) -> dict:
        settings_file = Path(self.dir) / "settings.yaml"
        if settings_file.exists():
            return yaml.safe_load(settings_file.read_text()) or {}
        return {}
