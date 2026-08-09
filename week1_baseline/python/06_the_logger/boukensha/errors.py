class UnknownToolError(Exception):
    """Raised when dispatch is called with an unregistered tool name."""
    pass


class ApiError(Exception):
    """Raised when an API request fails after all retries."""
    pass


class UnsupportedModelError(Exception):
    """Raised when a backend is given a model it doesn't support."""
    pass
