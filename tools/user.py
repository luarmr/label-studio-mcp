from mcp_instance import mcp
from label_studio_client import LabelStudioClient
from error_handling import mcp_tool_error_handler
from typing import Optional

@mcp.tool(
    description="List users from Label Studio. This endpoint is paginated: use the 'page' parameter to fetch each page in sequence, starting from 1. To retrieve all users, keep incrementing 'page' and calling this tool until the 'next' field in the response is null. Each response contains 'results', 'count', 'next', and 'previous' fields."
)
@mcp_tool_error_handler
def list_users(page: Optional[int] = 1, page_size: Optional[int] = 20) -> dict:
    client = LabelStudioClient()
    params = {'page': page, 'page_size': page_size}
    return client.get('/api/users/', params=params)

@mcp.tool(
    description="List all users assigned to a specific project."
)
@mcp_tool_error_handler
def list_project_users(project_id: str) -> list:
    if not project_id:
        raise ValueError("project_id is required.")
    client = LabelStudioClient()
    endpoint = f"/api/projects/{project_id}/members/"
    return client.get(endpoint)

@mcp.tool(
    description="Get information about the currently authenticated user."
)
@mcp_tool_error_handler
def whoami() -> dict:
    client = LabelStudioClient()
    return client.get('/api/current-user/whoami') 