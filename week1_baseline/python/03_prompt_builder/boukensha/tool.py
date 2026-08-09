from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict
    block: Callable[..., Any] | None = None

    def __str__(self) -> str:
        desc = self.description[:40] if len(self.description) > 40 else self.description
        params = list(self.parameters.keys())
        return f"#<Tool name={self.name} description={desc} params={params}>"

    def __repr__(self) -> str:
        return str(self)
