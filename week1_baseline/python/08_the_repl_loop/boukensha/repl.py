"""Interactive REPL session loop.

Reads tasks from stdin, runs the agent, prints replies, loops back.
Context is shared across turns so conversation history accumulates.
"""

from __future__ import annotations

from boukensha.agent import Agent


class Repl:
    PROMPT = "boukensha> "

    HELP = """\
Commands:
  /quiet   suppress logging output
  /loud    re-enable logging output
  /clear   wipe conversation history (tools stay)
  /exit    leave the REPL
  /help    show this message"""

    def __init__(
        self,
        context,
        registry,
        builder,
        client,
        logger,
        config_dir=None,
        provider=None,
        model=None,
        version=None,
        api_key=None,
        task_settings=None,
        max_iterations=None,
        max_output_tokens=None,
    ) -> None:
        self.context = context
        self.registry = registry
        self.builder = builder
        self.client = client
        self.logger = logger
        self.task_settings = task_settings
        self.max_iterations = max_iterations
        self.max_output_tokens = max_output_tokens
        self.config_dir = config_dir
        self.provider = provider
        self.model = model
        self.version = version
        self.api_key = api_key
        self.turn = 0

    def start(self) -> None:
        print(self._banner())

        while True:
            try:
                raw = input(self.PROMPT)
            except (EOFError, KeyboardInterrupt):
                print()
                break

            raw = raw.strip()
            if not raw:
                continue

            if raw in ("/exit", "/quit"):
                print("Goodbye.")
                break
            elif raw == "/help":
                print(self.HELP)
                continue
            elif raw == "/quiet":
                import boukensha
                boukensha.set_quiet(True)
                print("(logging suppressed — type /loud to re-enable)")
                continue
            elif raw == "/loud":
                import boukensha
                boukensha.set_quiet(False)
                print("(logging enabled)")
                continue
            elif raw == "/clear":
                self.context.clear_messages()
                self.turn = 0
                print("(conversation history cleared)")
                continue

            self._run_turn(raw)

    # ---------- private ---------------------------------------------------

    def _banner(self) -> str:
        key_status = (
            "✓ API key set"
            if self.api_key and self.api_key.strip()
            else "✗ API key not set"
        )
        provider_line = f"{self.provider or 'default'} ({self.model or 'default'})  {key_status}"
        ver = self.version or "?.?.?"

        return f"""

╔══════════════════════════════════════╗
║  BOUKENSHA MUD Assistant (v{ver}){" " * (9 - len(ver))}║
╚══════════════════════════════════════╝
  config:    {self.config_dir or '(default)'}
  provider:  {provider_line}

  /quiet or /loud   toggle logging
  /clear           reset conversation history
  /exit or /quit    leave the REPL
"""

    def _run_turn(self, input_text: str) -> None:
        self.turn += 1
        self.logger.turn(n=self.turn)

        self.context.add_message("user", input_text)

        agent = Agent(
            context=self.context,
            registry=self.registry,
            builder=self.builder,
            client=self.client,
            logger=self.logger,
            task_settings=self.task_settings,
            max_iterations=self.max_iterations,
            max_output_tokens=self.max_output_tokens,
        )
        result = agent.run()

        print()
        print(result)
