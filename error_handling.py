import logging
import traceback
import functools

class MCPError(Exception):
    def __init__(self, message, status_code=500, error_type="internal_error", details=None):
        super().__init__(message)
        self.status_code = status_code
        self.error_type = error_type
        self.details = details

    def to_dict(self):
        return {
            "error": {
                "type": self.error_type,
                "message": str(self),
                "status_code": self.status_code,
                "details": self.details,
            }
        }

def map_exception_to_mcp_error(exc):
    if isinstance(exc, ValueError):
        return MCPError(str(exc), status_code=400, error_type="validation_error")
    if isinstance(exc, RuntimeError):
        return MCPError(str(exc), status_code=502, error_type="upstream_error")
    if isinstance(exc, MCPError):
        return exc
    # Fallback for unexpected errors
    return MCPError("Internal server error", status_code=500, error_type="internal_error", details=traceback.format_exc())

def mcp_tool_error_handler(tool_func):
    @functools.wraps(tool_func)
    def wrapper(*args, **kwargs):
        try:
            return tool_func(*args, **kwargs)
        except Exception as exc:
            mcp_err = map_exception_to_mcp_error(exc)
            logging.error(f"MCP Tool Error: {mcp_err.error_type} - {mcp_err} (status {mcp_err.status_code})")
            return mcp_err.to_dict()
    return wrapper 