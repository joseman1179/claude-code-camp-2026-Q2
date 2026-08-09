from __future__ import annotations


class PromptBuilder:
    def __init__(self, context, backend) -> None:
        self.context = context
        self.backend = backend

    def to_messages(self) -> list[dict]:
        return self.backend.to_messages(self.context.messages)

    def to_tools(self) -> list[dict]:
        return self.backend.to_tools(self.context.tools)

    def to_api_payload(
        self, max_output_tokens: int = 1024, tools=None
    ) -> dict:
        return self.backend.to_payload(
            self.context, max_output_tokens=max_output_tokens, tools=tools
        )

    def parse_response(self, response: dict) -> dict:
        return self.backend.parse_response(response)

    def headers(self) -> dict:
        return self.backend.headers()

    def url(self) -> str:
        return self.backend.url()
