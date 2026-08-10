from __future__ import annotations

from boukensha.errors import UnsupportedModelError


class Base:
    MODELS: dict[str, dict] = {}

    @classmethod
    def _lookup_model(cls, model: str) -> dict | None:
        return cls.MODELS.get(str(model))

    @classmethod
    def validate_model(cls, model: str) -> str:
        model = str(model)
        if cls._lookup_model(model):
            return model
        supported = ", ".join(sorted(cls.MODELS.keys()))
        raise UnsupportedModelError(
            f"{cls.__name__} does not support model {model!r}. "
            f"Supported models: {supported}"
        )

    def _configure_model(self, model: str) -> None:
        self.model = self.validate_model(model)
        self._model_info = self.MODELS[self.model]

    @property
    def model_info(self) -> dict:
        return self._model_info

    @property
    def context_window(self) -> int:
        return self.model_info["context_window"]

    @property
    def input_token_cost_per_million(self) -> float | None:
        return self.model_info["cost_per_million"]["input"]

    @property
    def output_token_cost_per_million(self) -> float | None:
        return self.model_info["cost_per_million"]["output"]

    @property
    def usage_unit(self) -> str:
        return self.model_info["usage_unit"]

    @property
    def usage_level(self) -> str | None:
        return self.model_info.get("usage_level")

    def estimate_cost(
        self, input_tokens: int, output_tokens: int
    ) -> float | None:
        if (
            self.input_token_cost_per_million is None
            or self.output_token_cost_per_million is None
        ):
            return None
        return (
            (input_tokens * self.input_token_cost_per_million)
            + (output_tokens * self.output_token_cost_per_million)
        ) / 1_000_000.0
