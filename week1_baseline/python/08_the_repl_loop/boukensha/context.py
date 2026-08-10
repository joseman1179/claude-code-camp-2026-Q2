from __future__ import annotations

from boukensha.message import Message


class Context:
    def __init__(self, task, system: str | None = None) -> None:
        self.task = task
        self.system: str | None = system
        self.messages: list[Message] = []
        self.tools: dict[str, object] = {}

    def register_tool(self, tool) -> None:
        self.tools[tool.name] = tool

    def add_message(
        self, role: str, content: str, tool_use_id: str | None = None
    ) -> None:
        self.messages.append(Message(role, content, tool_use_id))

    @property
    def tool_count(self) -> int:
        return len(self.tools)

    @property
    def turn_count(self) -> int:
        return len(self.messages)

    def clear_messages(self) -> None:
        """Drop all conversation history, keeping tools and system prompt."""
        self.messages = []

    def __str__(self) -> str:
        task_name = self.task.task_name() if hasattr(self.task, "task_name") else str(self.task)
        return f"#<Context task={task_name} turns={self.turn_count} tools={self.tool_count}>"

    def __repr__(self) -> str:
        return str(self)
