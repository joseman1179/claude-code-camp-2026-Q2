"""Shared serialization for OpenAI-compatible APIs.

OpenAI, DeepSeek, Ollama, and OllamaCloud all use the same message/tool/payload
format. This base class extracts that common logic so each backend only needs
to define BASE_URL, MODELS, and __init__.
"""

from __future__ import annotations

from boukensha.backends.base import Base


class OpenAICompatibleBase(Base):
    def to_messages(self, system: str, messages: list) -> list[dict]:
        system_msg = [{"role": "system", "content": system}]
        conversation = []
        for msg in messages:
            if msg.role == "tool_result":
                conversation.append({
                    "role": "tool",
                    "tool_call_id": msg.tool_use_id,
                    "content": msg.content,
                })
            else:
                conversation.append({"role": msg.role, "content": msg.content})
        return system_msg + conversation

    def to_tools(self, tools: dict) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": {
                        "type": "object",
                        "properties": t.parameters,
                        "required": list(t.parameters.keys()),
                    },
                },
            }
            for t in tools.values()
        ]

    def to_payload(
        self, context, max_output_tokens: int = 1024
    ) -> dict:
        return {
            "model": self.model,
            "messages": self.to_messages(context.system, context.messages),
            "tools": self.to_tools(context.tools),
            "max_tokens": max_output_tokens,
        }

    def headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def url(self) -> str:
        return self.BASE_URL
