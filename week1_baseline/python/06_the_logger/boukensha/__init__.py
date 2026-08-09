from boukensha.client import Client
from boukensha.config import Config
from boukensha.context import Context
from boukensha.errors import UnknownToolError, UnsupportedModelError, ApiError
from boukensha.logger import Logger
from boukensha.message import Message
from boukensha.prompt_builder import PromptBuilder
from boukensha.registry import Registry
from boukensha.tool import Tool
from boukensha.tasks.player import Player
from boukensha.agent import Agent

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
    "Tool",
    "UnknownToolError",
    "UnsupportedModelError",
]

# Module-level state (used by Logger)
_config = None
_debug = False


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
