from __future__ import annotations

from boukensha.backends._openai_compatible import OpenAICompatibleBase


class OllamaCloud(OpenAICompatibleBase):
    BASE_URL = "https://ollama.com/api/chat"
    MODELS = {
        "gemma4:31b-cloud": {
            "context_window": 256_000,
            "cost_per_million": {"input": None, "output": None},
            "usage_unit": "ollama_cloud_usage",
            "usage_level": "medium",
        },
        "minimax-m3:cloud": {
            "context_window": 512_000,
            "cost_per_million": {"input": None, "output": None},
            "usage_unit": "ollama_cloud_usage",
            "usage_level": "high",
        },
        "kimi-k2.5:cloud": {
            "context_window": 256_000,
            "cost_per_million": {"input": None, "output": None},
            "usage_unit": "ollama_cloud_usage",
            "usage_level": "high",
        },
    }

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self._configure_model(model)

    def to_payload(
        self, context, max_output_tokens: int = 1024, tools=None
    ) -> dict:
        return {
            "model": self.model,
            "stream": False,
            "messages": self.to_messages(context.system, context.messages),
            "tools": tools if tools is not None else self.to_tools(context.tools),
        }

    # Ollama doesn't assign call ids — reuse the function name.
    def parse_response(self, response: dict) -> dict:
        message = response.get("message", {})
        tool_calls = message.get("tool_calls", [])

        content = []
        if message.get("content"):
            content.append({"type": "text", "text": message["content"]})

        for tc in tool_calls:
            fn = tc.get("function", {})
            content.append({
                "type": "tool_use",
                "id": fn.get("name"),
                "name": fn.get("name"),
                "input": fn.get("arguments", {}),
            })

        stop_reason = "tool_use" if tool_calls else "end_turn"
        return {"stop_reason": stop_reason, "content": content}

    # Ollama tool_calls format: no "id" or "type" fields.
    def _assistant_message(self, content) -> dict:
        if isinstance(content, str):
            blocks = [{"type": "text", "text": content}]
        else:
            blocks = content

        text = "".join(b["text"] for b in blocks if b["type"] == "text")
        tool_blocks = [b for b in blocks if b["type"] == "tool_use"]

        msg = {"role": "assistant", "content": text}
        if tool_blocks:
            msg["tool_calls"] = [
                {"function": {"name": b["name"], "arguments": b["input"]}}
                for b in tool_blocks
            ]
        return msg
