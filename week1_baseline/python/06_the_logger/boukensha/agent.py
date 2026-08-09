"""Agent loop orchestrator.

The Agent ties together Context, Registry, PromptBuilder, Client, and Logger
into a single turn: call the API → parse the response → dispatch tool calls →
inject results → repeat, until the model returns text or the iteration limit
is hit.
"""

from __future__ import annotations

from boukensha.errors import ApiError
from boukensha.logger import Logger


class Agent:
    MAX_ITERATIONS = 25
    WRAP_UP_OUTPUT_TOKENS = 400
    WRAP_UP_DIRECTIVE = (
        "You have reached your action limit for this turn. Do not call any more tools. "
        "Briefly summarize what you accomplished, what is still unfinished, and the "
        "single next action you would take."
    )

    def __init__(
        self,
        context,
        registry,
        builder,
        client,
        logger=None,
        task_settings=None,
        max_iterations=None,
        max_output_tokens=None,
    ) -> None:
        self.context = context
        self.registry = registry
        self.builder = builder
        self.client = client
        self.logger = logger if logger is not None else Logger()
        self.max_iterations = self._resolve_max_iterations(
            task_settings, max_iterations
        )
        self.max_output_tokens = self._resolve_max_output_tokens(
            task_settings, max_output_tokens
        )
        self.iteration = 0

    def run(self) -> str:
        while True:
            if self._iteration_limit_reached():
                self.logger.limit_reached(
                    kind="max_iterations", n=self.iteration, max=self.max_iterations
                )
                return self._wrap_up("max_iterations")

            self.iteration += 1
            print(f"[iteration {self.iteration}/{self.max_iterations}]")
            self.logger.iteration(n=self.iteration, max=self.max_iterations)
            self.logger.prompt(messages=self.context.messages, tools=self.context.tools)

            response = self.client.call(**self._call_opts())
            self.logger.raw(data=response)
            parsed = self.builder.parse_response(response)

            if parsed["stop_reason"] == "tool_use":
                self._handle_tool_calls(parsed["content"], response)
            else:
                text = self._extract_text(parsed["content"])
                self._log_response(text=text, response=response)
                self.logger.turn_end(reason="completed", iterations=self.iteration)
                return text

    # ---------- private ---------------------------------------------------

    def _resolve_max_iterations(self, task_settings, explicit) -> int:
        if explicit is not None:
            return int(explicit)
        if task_settings and hasattr(self.context.task, "max_iterations"):
            return self.context.task.max_iterations(task_settings)
        return self.MAX_ITERATIONS

    def _resolve_max_output_tokens(self, task_settings, explicit) -> int | None:
        if explicit is not None:
            return explicit
        if task_settings and hasattr(self.context.task, "max_output_tokens"):
            return self.context.task.max_output_tokens(task_settings)
        return None

    def _iteration_limit_reached(self) -> bool:
        return self.max_iterations > 0 and self.iteration >= self.max_iterations

    def _call_opts(self) -> dict:
        if self.max_output_tokens:
            return {"max_output_tokens": self.max_output_tokens}
        return {}

    def _wrap_up(self, reason: str) -> str:
        self.context.add_message("user", self.WRAP_UP_DIRECTIVE)
        try:
            response = self.client.call(
                tools=[], max_output_tokens=self.WRAP_UP_OUTPUT_TOKENS
            )
            text = self._extract_text(
                self.builder.parse_response(response)["content"]
            )
            text = text if text.strip() else self._fallback_message(reason)
            self._log_response(text=text, response=response)
            self.logger.turn_end(reason=reason, iterations=self.iteration)
            return text
        except ApiError:
            msg = self._fallback_message(reason)
            self.logger.turn_end(reason=reason, iterations=self.iteration)
            return msg

    def _fallback_message(self, reason: str) -> str:
        return (
            f"I reached my {self.max_iterations}-action limit for this turn "
            f"before finishing ({reason}). Ask me to continue and I'll pick "
            f"up from here."
        )

    def _extract_text(self, content: list[dict]) -> str:
        return "".join(b["text"] for b in content if b.get("type") == "text")

    def _handle_tool_calls(self, content: list[dict], response: dict) -> None:
        tool_calls = [b for b in content if b.get("type") == "tool_use"]
        reasoning = self._extract_text(content)
        self._log_response(
            text=reasoning if reasoning.strip() else f"(tool use — {len(tool_calls)} call{'s' if len(tool_calls) != 1 else ''})",
            response=response,
        )

        self.context.add_message("assistant", content)

        for block in tool_calls:
            name = block["name"]
            args = block["input"]
            use_id = block["id"]

            print(f"  tool call → {name}({args})")
            self.logger.tool_call(name=name, args=args)
            try:
                result = self.registry.dispatch(name, args)
                print(f"  tool result → {str(result)[:60]}")
                self.logger.tool_result(name=name, result=result, ok=True)
            except Exception as e:
                result = f"ERROR: {type(e).__name__}: {e}"
                print(f"  tool result → {result[:60]}")
                self.logger.tool_result(
                    name=name, result=result, ok=False, error=str(e)
                )

            self.context.add_message(
                "tool_result", str(result), tool_use_id=use_id
            )

    def _log_response(self, text: str, response: dict) -> None:
        self.logger.response(
            text=text,
            usage=self._normalized_usage(response),
            stop_reason=response.get("stop_reason"),
            task=self.context.task,
            backend=self.builder.backend,
        )

    @staticmethod
    def _normalized_usage(response: dict) -> dict | None:
        for key in ("usage", "usageMetadata"):
            if key in response:
                return response[key]
        usage = {}
        for key in ("prompt_eval_count", "eval_count"):
            if key in response:
                usage[key] = response[key]
        return usage or None
