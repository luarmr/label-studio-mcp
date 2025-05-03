from mcp_instance import mcp
from label_studio_client import LabelStudioClient
from error_handling import mcp_tool_error_handler

@mcp.tool(
    description="Extract and return only the progress metrics from the project details."
)
@mcp_tool_error_handler
def get_project_progress(project_id: str) -> dict:
    if not project_id:
        raise ValueError("project_id is required.")
    client = LabelStudioClient()
    endpoint = f"/api/projects/{project_id}/"
    project = client.get(endpoint)
    progress_fields = [
        "task_number",
        "finished_task_number",
        "total_annotations_number",
        "total_predictions_number",
        "num_tasks_with_annotations",
        "useful_annotation_number",
        "ground_truth_number",
        "skipped_annotations_number",
        "queue_total",
        "queue_done",
        "overlap_cohort_percentage",
    ]
    progress = {k: project.get(k) for k in progress_fields if k in project}
    if not progress:
        return {"progress": None, "warning": "No progress metrics found for this project."}
    return {"progress": progress} 