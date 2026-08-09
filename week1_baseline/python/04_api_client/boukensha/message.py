from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Message:
    role: str
    content: str
    tool_use_id: str | None = None

    def __str__(self) -> str:
        id_tag = f" [{self.tool_use_id}]" if self.tool_use_id else ""
        preview = self.content[:60] + "..." if len(self.content) > 60 else self.content
        return f"#<Message role={self.role}{id_tag} content={preview}>"

    def __repr__(self) -> str:
        return str(self)
