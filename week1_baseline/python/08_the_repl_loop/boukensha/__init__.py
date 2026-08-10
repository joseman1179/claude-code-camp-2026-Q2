from boukensha.agent import Agent
from boukensha.client import Client
from boukensha.config import Config
from boukensha.context import Context
from boukensha.errors import UnknownToolError, UnsupportedModelError, ApiError
from boukensha.logger import Logger
from boukensha.message import Message
from boukensha.prompt_builder import PromptBuilder
from boukensha.registry import Registry
from boukensha.repl import Repl
from boukensha.run_dsl import RunDSL
from boukensha.tool import Tool
from boukensha.tasks.player import Player
from boukensha.version import VERSION

__all__ = [
    "Agent",
    "ApiError",
    "Client",
    "Config",
    "Context",
    "Logger",
    "Message",
    "Player",
    "PromptBuilder",
    "Registry",
    "Repl",
    "RunDSL",
    "Tool",
    "UnknownToolError",
    "UnsupportedModelError",
    "VERSION",
]

# Module-level state (used by Logger and REPL)
_config = None
_debug = False
_quiet = False


def set_config(config) -> None:
    global _config
    _config = config


def get_config():
    return _config


def debug_mode() -> None:
    global _debug
    _debug = True


def is_debug() -> bool:
    return _debug


def set_quiet(value: bool) -> None:
    global _quiet
    _quiet = value


def is_quiet() -> bool:
    return _quiet


def run(
    task: str,
    *,
    system: str | None = None,
    model: str | None = None,
    backend: str | None = None,
    api_key: str | None = None,
    ollama_host: str = "http://localhost:11434",
    log: str | None = None,
    max_output_tokens: int | None = None,
    tools=None,
):
    """Top-level entry point. Wires all plumbing internally.

    Args:
        task: The user message to hand the agent.
        system: System prompt. Defaults to config system_prompt.
        model: Model name. Defaults to config model.
        backend: Provider name. Defaults to config provider.
        api_key: API key. Auto-resolved from env vars by backend.
        ollama_host: Ollama base URL (default http://localhost:11434).
        log: Optional JSONL path override.
        max_output_tokens: Per-reply output cap.
        tools: Callback receiving a RunDSL instance for tool registration.
    """
    import os

    from boukensha.config import Config
    from boukensha.context import Context
    from boukensha.registry import Registry
    from boukensha.run_dsl import RunDSL
    from boukensha.prompt_builder import PromptBuilder
    from boukensha.client import Client
    from boukensha.logger import Logger
    from boukensha.agent import Agent
    from boukensha.tasks.player import Player

    cfg = Config()
    set_config(cfg)

    task_class = Player
    task_settings = cfg.tasks(task_class.task_name())

    if system is None:
        system = task_class.system_prompt(
            task_settings,
            user_prompts_dir=cfg.user_prompts_dir,
            default_prompts_dir=str(Config.PROMPTS_DIR),
        )
    if model is None:
        model = task_class.model(task_settings)
    if backend is None:
        backend = task_class.provider(task_settings)

    # Resolve api_key from env vars
    if api_key is None:
        key_map = {
            "anthropic": "ANTHROPIC_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "openai": "OPENAI_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "ollama_cloud": "OLLAMA_API_KEY",
        }
        api_key = os.environ.get(key_map.get(backend, ""))

    ctx = Context(task=task_class, system=system)
    registry = Registry(ctx)

    if tools:
        dsl = RunDSL(registry)
        tools(dsl)

    # Build backend
    from boukensha.backends.anthropic import Anthropic
    from boukensha.backends.deepseek import DeepSeek
    from boukensha.backends.openai import OpenAI
    from boukensha.backends.gemini import Gemini
    from boukensha.backends.ollama import Ollama
    from boukensha.backends.ollama_cloud import OllamaCloud

    backend_map = {
        "anthropic": lambda: Anthropic(api_key=api_key, model=model),
        "deepseek": lambda: DeepSeek(api_key=api_key, model=model),
        "openai": lambda: OpenAI(api_key=api_key, model=model),
        "gemini": lambda: Gemini(api_key=api_key, model=model),
        "ollama": lambda: Ollama(host=ollama_host, model=model),
        "ollama_cloud": lambda: OllamaCloud(api_key=api_key, model=model),
    }
    if backend not in backend_map:
        raise ValueError(
            f"Unknown backend {backend!r}. "
            f"Use: {', '.join(sorted(backend_map.keys()))}"
        )
    be = backend_map[backend]()

    builder = PromptBuilder(ctx, be)
    client = Client(builder)
    effective_max = task_class.max_iterations(task_settings)
    effective_tokens = max_output_tokens or task_class.max_output_tokens(task_settings)
    logger = Logger(log=log, snapshot={
        "task": task_class.task_name(),
        "max_iterations": effective_max,
        "max_output_tokens": effective_tokens,
        "model": model,
        "provider": backend,
    })
    agent = Agent(
        context=ctx,
        registry=registry,
        builder=builder,
        client=client,
        logger=logger,
        task_settings=task_settings,
        max_iterations=effective_max,
        max_output_tokens=effective_tokens,
    )

    ctx.add_message("user", task)
    try:
        return agent.run()
    finally:
        logger.close()


def repl(
    *,
    system: str | None = None,
    model: str | None = None,
    backend: str | None = None,
    api_key: str | None = None,
    ollama_host: str = "http://localhost:11434",
    log: str | None = None,
    max_output_tokens: int | None = None,
    tools=None,
) -> None:
    """Interactive REPL: register tools once, then loop reading tasks from stdin.

    Same options as boukensha.run() minus `task`.
    """
    import os

    from boukensha.config import Config
    from boukensha.context import Context
    from boukensha.registry import Registry
    from boukensha.run_dsl import RunDSL
    from boukensha.prompt_builder import PromptBuilder
    from boukensha.client import Client
    from boukensha.logger import Logger
    from boukensha.repl import Repl
    from boukensha.tasks.player import Player

    cfg = Config()
    set_config(cfg)

    task_class = Player
    task_settings = cfg.tasks(task_class.task_name())

    if system is None:
        system = task_class.system_prompt(
            task_settings,
            user_prompts_dir=cfg.user_prompts_dir,
            default_prompts_dir=str(Config.PROMPTS_DIR),
        )
    if model is None:
        model = task_class.model(task_settings)
    if backend is None:
        backend = task_class.provider(task_settings)

    if api_key is None:
        key_map = {
            "anthropic": "ANTHROPIC_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "openai": "OPENAI_API_KEY",
            "gemini": "GEMINI_API_KEY",
            "ollama_cloud": "OLLAMA_API_KEY",
        }
        api_key = os.environ.get(key_map.get(backend, ""))

    ctx = Context(task=task_class, system=system)
    registry = Registry(ctx)

    if tools:
        dsl = RunDSL(registry)
        tools(dsl)

    from boukensha.backends.anthropic import Anthropic
    from boukensha.backends.deepseek import DeepSeek
    from boukensha.backends.openai import OpenAI
    from boukensha.backends.gemini import Gemini
    from boukensha.backends.ollama import Ollama
    from boukensha.backends.ollama_cloud import OllamaCloud

    backend_map = {
        "anthropic": lambda: Anthropic(api_key=api_key, model=model),
        "deepseek": lambda: DeepSeek(api_key=api_key, model=model),
        "openai": lambda: OpenAI(api_key=api_key, model=model),
        "gemini": lambda: Gemini(api_key=api_key, model=model),
        "ollama": lambda: Ollama(host=ollama_host, model=model),
        "ollama_cloud": lambda: OllamaCloud(api_key=api_key, model=model),
    }
    if backend not in backend_map:
        raise ValueError(
            f"Unknown backend {backend!r}. "
            f"Use: {', '.join(sorted(backend_map.keys()))}"
        )
    be = backend_map[backend]()

    builder = PromptBuilder(ctx, be)
    client = Client(builder)
    effective_max = task_class.max_iterations(task_settings)
    effective_tokens = max_output_tokens or task_class.max_output_tokens(task_settings)
    logger = Logger(log=log, snapshot={
        "task": task_class.task_name(),
        "max_iterations": effective_max,
        "max_output_tokens": effective_tokens,
        "model": model,
        "provider": backend,
    })

    repl_instance = Repl(
        context=ctx,
        registry=registry,
        builder=builder,
        client=client,
        logger=logger,
        config_dir=cfg.dir,
        provider=backend,
        model=model,
        version=VERSION,
        api_key=api_key,
        task_settings=task_settings,
        max_iterations=effective_max,
        max_output_tokens=effective_tokens,
    )
    try:
        repl_instance.start()
    except KeyboardInterrupt:
        print("\nInterrupted.")
    finally:
        logger.close()
