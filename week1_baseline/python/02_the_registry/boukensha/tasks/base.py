from __future__ import annotations

import os
from pathlib import Path


class Base:
    """Abstract stateless base class for task definitions.

    All behaviour is expressed as class methods that accept a settings dict —
    no instances are created. Concrete subclasses define task_name.
    """

    @classmethod
    def task_name(cls) -> str:
        raise NotImplementedError(f"{cls} must define .task_name")

    @classmethod
    def provider(cls, settings: dict) -> str:
        val = cls._fetch(settings, "provider")
        if not val:
            raise ValueError(
                f"tasks.{cls.task_name()}.provider is required in settings.yml"
            )
        return val

    @classmethod
    def model(cls, settings: dict) -> str:
        val = cls._fetch(settings, "model")
        if not val:
            raise ValueError(
                f"tasks.{cls.task_name()}.model is required in settings.yml"
            )
        return val

    @classmethod
    def prompt_override(cls, settings: dict, prompt: str = "system") -> bool:
        node = cls._fetch(settings, "prompt_override")
        if not isinstance(node, dict):
            return False
        return node.get(prompt) is True

    @classmethod
    def prompt(
        cls,
        settings: dict,
        name: str = "system",
        user_prompts_dir: str | None = None,
        default_prompts_dir: str | None = None,
    ) -> str | None:
        if cls.prompt_override(settings, name) and (
            text := cls._read_user_prompt(
                name, cls.task_name(), user_prompts_dir=user_prompts_dir
            )
        ):
            return text

        return cls._read_default_prompt(name, default_prompts_dir=default_prompts_dir)

    @classmethod
    def system_prompt(
        cls,
        settings: dict,
        user_prompts_dir: str | None = None,
        default_prompts_dir: str | None = None,
    ) -> str | None:
        return cls.prompt(
            settings,
            "system",
            user_prompts_dir=user_prompts_dir,
            default_prompts_dir=default_prompts_dir,
        )

    # ---------- private helpers -------------------------------------------

    @staticmethod
    def _fetch(settings: dict, key: str):
        return settings.get(key)

    @staticmethod
    def _read_user_prompt(
        prompt_name: str,
        task_name: str,
        user_prompts_dir: str | None = None,
    ) -> str | None:
        if not user_prompts_dir:
            return None
        return Base._read_file(
            str(Path(user_prompts_dir) / task_name / f"{prompt_name}.md")
        )

    @staticmethod
    def _read_default_prompt(
        prompt_name: str, default_prompts_dir: str | None = None
    ) -> str | None:
        if not default_prompts_dir:
            return None
        return Base._read_file(
            str(Path(default_prompts_dir) / f"{prompt_name}.md")
        )

    @staticmethod
    def _read_file(path: str) -> str | None:
        p = Path(path)
        if p.exists():
            return p.read_text().strip()
        return None
