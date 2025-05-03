from mcp_instance import mcp
from tools.project import *
from tools.task import *
from tools.user import *
from tools.analytics import *
from label_studio_client import LabelStudioClient

if __name__ == "__main__":
    # Verify Label Studio connection before starting the server
    try:
        client = LabelStudioClient()
        client.verify_connection()
        print("Label Studio connection verified. Starting MCP server...")
    except Exception as e:
        import sys
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    mcp.run() 