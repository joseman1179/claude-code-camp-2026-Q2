from boukensha.errors import UnknownToolError
from boukensha.tool import Tool


class Registry:
    def __init__(self, context):
        self.context = context

    def tool(self, name, description, parameters=None):
        """Register a tool on the context. Returns a decorator."""
        def decorator(block):
            registered = Tool(str(name), description, parameters or {}, block)
            self.context.register_tool(registered)
            return block
        return decorator

    def dispatch(self, name, args=None):
        tool = self.context.tools.get(str(name))
        if tool is None:
            raise UnknownToolError(f"No tool registered as '{name}'")
        # Python ** unpacking works directly with string keys —
        # no symbol conversion needed (unlike Ruby's transform_keys(&:to_sym)).
        return tool.block(**(args or {}))
