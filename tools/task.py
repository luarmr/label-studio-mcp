from mcp_instance import mcp
from label_studio_client import LabelStudioClient
from error_handling import mcp_tool_error_handler
from typing import Optional, List, Dict
import base64

@mcp.tool(
    description="Import a list of tasks into a Label Studio project. Requires a project_id and a non-empty list of tasks. The 'tasks' parameter is required and must be a non-empty list; omitting it or providing an empty list will result in an error."
)
@mcp_tool_error_handler
def import_tasks(
    project_id: str,
    tasks: List[Dict]
) -> dict:
    if not project_id or not isinstance(tasks, list) or not tasks:
        raise ValueError("project_id and a non-empty list of tasks are required.")
    client = LabelStudioClient()
    return client.import_tasks(str(project_id), tasks)

@mcp.tool(
    description="List tasks for a given Label Studio project. Supports pagination with custom page sizes via 'page' and 'page_size' parameters. Supports filtering via the 'filters' parameter. Annotation results can be included in the response by using the appropriate query parameters. Each response includes pagination metadata (total, next, previous) to help navigate through all tasks."
)
@mcp_tool_error_handler
def list_tasks(
    project_id: str,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    filters: Optional[dict] = None,
    **kwargs
) -> dict:
    if not project_id:
        raise ValueError("project_id is required.")
    client = LabelStudioClient()
    query_params = {}
    if page is not None:
        query_params['page'] = page
    if page_size is not None:
        query_params['page_size'] = page_size
    if filters is not None:
        query_params['filters'] = filters
    query_params.update(kwargs)
    return client.list_tasks(project_id, **query_params)

@mcp.tool(
    description="Export annotations for a given Label Studio project. Optionally specify exportType for format."
)
@mcp_tool_error_handler
def export_annotations(
    project_id: str,
    exportType: Optional[str] = None,
    **kwargs
) -> dict:
    if not project_id:
        raise ValueError("project_id is required.")
    client = LabelStudioClient()
    query_params = {}
    if exportType is not None:
        query_params['exportType'] = exportType
    query_params.update(kwargs)
    content, content_type = client.export_annotations(project_id, **query_params)
    if 'json' in content_type.lower():
        return {'content': content, 'content_type': content_type}
    else:
        encoded = base64.b64encode(content).decode('utf-8')
        return {'content': encoded, 'content_type': content_type, 'encoding': 'base64'} 