from __future__ import annotations

import json

from boukensha.backends._openai_compatible import OpenAICompatibleBase


class DeepSeek(OpenAICompatibleBase):
    BASE_URL = "https://api.deepseek.com/v1/chat/completions"
    MODELS = {
        "deepseek-chat": {
            "context_window": 128_000,
            "cost_per_million": {"input": 0.27, "output": 1.10},
            "usage_unit": "tokens",
        },
        "deepseek-reasoner": {
            "context_window": 128_000,
            "cost_per_million": {"input": 0.55, "output": 2.19},
            "usage_unit": "tokens",
        },
        "deepseek-v4-pro": {
            "context_window": 256_000,
            "cost_per_million": {"input": 0.50, "output": 2.00},
            "usage_unit": "tokens",
        },
    }

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self._configure_model(model)
