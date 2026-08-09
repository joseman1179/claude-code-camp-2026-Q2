from __future__ import annotations

from boukensha.backends._openai_compatible import OpenAICompatibleBase


class Ollama(OpenAICompatibleBase):
    MODELS = {
        "gemma4": {
            "context_window": 128_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "gemma4:e2b": {
            "context_window": 128_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "gemma4:e4b": {
            "context_window": 128_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "gemma4:12b": {
            "context_window": 256_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "gemma4:26b": {
            "context_window": 256_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "gemma4:31b": {
            "context_window": 256_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "qwen3:30b": {
            "context_window": 256_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "qwen3:8b": {
            "context_window": 40_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "deepseek-r1:8b": {
            "context_window": 128_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
    }

    def __init__(
        self, host: str = "http://localhost:11434", model: str = ""
    ) -> None:
        self.host = host
        self._configure_model(model)

    def headers(self) -> dict:
        return {"Content-Type": "application/json"}

    def url(self) -> str:
        return f"{self.host}/api/chat"

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
