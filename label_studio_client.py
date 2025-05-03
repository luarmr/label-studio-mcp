import requests
from config import config

class LabelStudioClient:
    """
    Client for interacting with the Label Studio API.
    Supports both personal (Bearer <token>, default) and legacy (Token <token>) authentication schemes.
    Set LS_AUTH_TYPE in your environment or .env to 'personal' (default) or 'legacy'.
    """
    def __init__(self):
        self.base_url = config.LS_BASE_URL.rstrip('/')
        self.token = config.LS_API_TOKEN
        self.timeout = config.TIMEOUT
        # Determine auth type
        auth_type = getattr(config, 'LS_AUTH_TYPE', 'personal').lower()
        if auth_type == 'legacy':
            self.headers = {
                'Authorization': f'Token {self.token}',
                'Content-Type': 'application/json',
            }
        else:
            self.headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json',
            }

    def get(self, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}"
        try:
            resp = requests.get(url, headers=self.headers, timeout=self.timeout, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            raise RuntimeError(f"GET {url} failed: {e}")

    def post(self, endpoint, json=None, **kwargs):
        url = f"{self.base_url}{endpoint}"
        try:
            resp = requests.post(url, headers=self.headers, json=json, timeout=self.timeout, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            raise RuntimeError(f"POST {url} failed: {e}")

    def patch(self, endpoint, json=None, **kwargs):
        """
        Send a PATCH request to the Label Studio API.
        :param endpoint: API endpoint (e.g., '/api/projects/{id}/')
        :param json: (optional) JSON payload to send in the request body
        :param kwargs: (optional) Additional arguments for requests.patch
        :return: API response as dict
        """
        url = f"{self.base_url}{endpoint}"
        try:
            resp = requests.patch(url, headers=self.headers, json=json, timeout=self.timeout, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            raise RuntimeError(f"PATCH {url} failed: {e}")

    def verify_connection(self):
        """
        Verifies connectivity to Label Studio by calling /api/projects/.
        Raises a clear error if the connection fails.
        """
        try:
            self.get('/api/health')
        except Exception as e:
            raise RuntimeError(f"Label Studio connection verification failed: {e}")

    def import_tasks(self, project_id, tasks):
        """
        Import tasks into a Label Studio project.
        :param project_id: ID of the project to import tasks into
        :param tasks: List of task dicts to import
        :return: API response as dict
        """
        if not project_id or not isinstance(tasks, list) or not tasks:
            raise ValueError("project_id and a non-empty list of tasks are required.")
        endpoint = f"/api/projects/{project_id}/import"
        try:
            return self.post(endpoint, json=tasks)
        except Exception as e:
            raise RuntimeError(f"Importing tasks failed: {e}")

    def list_tasks(self, project_id, **query_params):
        """
        List tasks for a given Label Studio project.
        :param project_id: ID of the project to list tasks for
        :param query_params: Optional query parameters (page, page_size, filters, etc.)
        :return: API response as dict
        """
        if not project_id:
            raise ValueError("project_id is required.")
        endpoint = f"/api/projects/{project_id}/tasks/"
        try:
            return self.get(endpoint, params=query_params)
        except Exception as e:
            raise RuntimeError(f"Listing tasks failed: {e}")

    def export_annotations(self, project_id, **query_params):
        """
        Export annotations for a given Label Studio project.
        :param project_id: ID of the project to export annotations from
        :param query_params: Optional query parameters (exportType, etc.)
        :return: Tuple (content, content_type)
        """
        if not project_id:
            raise ValueError("project_id is required.")
        endpoint = f"/api/projects/{project_id}/export"
        url = f"{self.base_url}{endpoint}"
        try:
            resp = requests.get(url, headers=self.headers, params=query_params, timeout=self.timeout, stream=True)
            resp.raise_for_status()
            content_type = resp.headers.get('Content-Type', '')
            # For JSON, parse and return as object; for others, return raw content
            if 'application/json' in content_type:
                return resp.json(), content_type
            else:
                return resp.content, content_type
        except requests.RequestException as e:
            raise RuntimeError(f"Exporting annotations failed: {e}")

# Example usage (remove or comment out in production):
# client = LabelStudioClient()
# print(client.get('/api/projects/')) 