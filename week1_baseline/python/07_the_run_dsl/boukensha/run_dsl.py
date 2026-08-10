"""RunDSL is the object passed to the tools callback inside boukensha.run().

It exposes only `tool`, keeping the DSL surface intentionally small.
"""

from __future__ import annotations


class RunDSL:
    def __init__(self, registry) -> None:
        self._registry = registry

    def tool(self, name: str, description: str, parameters=None):
        """Register a tool via decorator. Delegates to Registry.tool()."""
        return self._registry.tool(
            name, description=description, parameters=parameters
        )
