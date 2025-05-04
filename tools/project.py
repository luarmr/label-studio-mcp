from mcp_instance import mcp
from label_studio_client import LabelStudioClient
from error_handling import mcp_tool_error_handler

@mcp.tool(
    description="List projects from Label Studio. Optionally filter by title (case-insensitive substring match) using the 'title' parameter. This endpoint is paginated with a fixed page size of 20 items: use the 'page' parameter to fetch each page in sequence, starting from 1. To retrieve all projects, keep incrementing 'page' and calling this tool until the 'next' field in the response is null. Each response contains 'results', 'count', 'next', and 'previous' fields."
)
@mcp_tool_error_handler
def list_projects(page: int = 1, title: str = None) -> dict:
    client = LabelStudioClient()
    params = {'page': page, 'page_size': 20, 'include': 'id,title,created_by,created_at,is_published'}
    if title:
        params['title'] = title
    return client.get('/api/projects/', params=params)

@mcp.tool(
    description="Create a new project in Label Studio. Requires a title and label_config. Optional fields allow further customization."
)
@mcp_tool_error_handler
def create_project(
    title: str,
    label_config: str,
    description: str = None,
    expert_instruction: str = None,
    show_instruction: bool = False,
    show_skip_button: bool = True,
    enable_empty_annotation: bool = True,
    show_annotation_history: bool = False,
    organization: int = None,
    color: str = None,
    maximum_annotations: int = 1
) -> dict:
    if not title or not label_config:
        raise ValueError("Both title and label_config are required.")
    client = LabelStudioClient()
    payload = {
        "title": title,
        "label_config": label_config,
        "description": description,
        "expert_instruction": expert_instruction,
        "show_instruction": show_instruction,
        "show_skip_button": show_skip_button,
        "enable_empty_annotation": enable_empty_annotation,
        "show_annotation_history": show_annotation_history,
        "organization": organization,
        "color": color,
        "maximum_annotations": maximum_annotations,
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    return client.post("/api/projects/", json=payload)

@mcp.tool(
    description="Fetch and return complete project details from the Label Studio API."
)
@mcp_tool_error_handler
def get_project(project_id: str) -> dict:
    if not project_id:
        raise ValueError("project_id is required.")
    client = LabelStudioClient()
    endpoint = f"/api/projects/{project_id}/"
    return client.get(endpoint)

@mcp.tool(
    description="Extract and return only the guidelines section from the project details."
)
@mcp_tool_error_handler
def get_project_guidelines(project_id: str) -> dict:
    if not project_id:
        raise ValueError("project_id is required.")
    client = LabelStudioClient()
    endpoint = f"/api/projects/{project_id}/"
    project = client.get(endpoint)
    guidelines = project.get("expert_instruction")
    if guidelines is None or not isinstance(guidelines, str):
        return {"guidelines": None, "warning": "No guidelines found for this project."}
    return {"guidelines": guidelines}

@mcp.tool(
    description="Extract and return only the label configuration from the project details."
)
@mcp_tool_error_handler
def get_label_config(project_id: str) -> dict:
    if not project_id:
        raise ValueError("project_id is required.")
    client = LabelStudioClient()
    endpoint = f"/api/projects/{project_id}/"
    project = client.get(endpoint)
    label_config = project.get("label_config")
    if label_config is None or not isinstance(label_config, str):
        return {"label_config": None, "warning": "No label_config found for this project."}
    return {"label_config": label_config}

@mcp.tool(
    description="Set the published status of a project (publish/unpublish)."
)
@mcp_tool_error_handler
def set_project_published(project_id: str, published: bool) -> dict:
    if not project_id:
        raise ValueError("project_id is required.")
    if published is None:
        raise ValueError("published is required.")
    client = LabelStudioClient()
    endpoint = f"/api/projects/{project_id}/"
    payload = {"is_published": published}
    return client.patch(endpoint, json=payload)

@mcp.tool(
    description="Update project settings and guidelines."
)
@mcp_tool_error_handler
def update_project_settings(project_id: str, title: str = None, description: str = None, expert_instruction: str = None) -> dict:
    if not project_id:
        raise ValueError("project_id is required.")
    payload = {}
    if title is not None:
        payload["title"] = title
    if description is not None:
        payload["description"] = description
    if expert_instruction is not None:
        payload["expert_instruction"] = expert_instruction
    if not payload:
        raise ValueError("At least one field (title, description, expert_instruction) must be provided.")
    client = LabelStudioClient()
    endpoint = f"/api/projects/{project_id}/"
    return client.patch(endpoint, json=payload)

@mcp.tool(
    description="Update the label configuration for a project."
)
@mcp_tool_error_handler
def update_label_config(project_id: str, label_config: str) -> dict:
    if not project_id:
        raise ValueError("project_id is required.")
    if not label_config:
        raise ValueError("label_config is required.")
    client = LabelStudioClient()
    endpoint = f"/api/projects/{project_id}/"
    payload = {"label_config": label_config}
    return client.patch(endpoint, json=payload)

@mcp.tool(
    description="Delete a project with confirmation safeguard. Requires project_id and confirm=True.",
    tags={"destructive"}
)
@mcp_tool_error_handler
def delete_project(project_id: str, confirm: bool = False) -> dict:
    if not project_id:
        raise ValueError("project_id is required.")
    if not confirm:
        return {"error": "Confirmation required to delete project. Set confirm=True."}
    client = LabelStudioClient()
    endpoint = f"/api/projects/{project_id}/"
    import requests
    url = f"{client.base_url}{endpoint}"
    try:
        resp = requests.delete(url, headers=client.headers, timeout=client.timeout)
        resp.raise_for_status()
        return {"success": True, "message": f"Project {project_id} deleted."}
    except requests.RequestException as e:
        raise RuntimeError(f"DELETE {url} failed: {e}")

@mcp.tool(
    description="Validate a labeling interface XML config for a given project. Requires project_id and label_config."
)
@mcp_tool_error_handler
def validate_label_config(
    project_id: str,
    label_config: str
) -> dict:
    if not project_id or not label_config:
        raise ValueError("Both project_id and label_config are required.")
    client = LabelStudioClient()
    endpoint = f"/api/projects/{project_id}/validate/"
    payload = {"label_config": label_config}
    return client.post(endpoint, json=payload) 