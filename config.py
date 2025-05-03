import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

class Config:
    """
    Centralized configuration for the MCP Label Studio server.
    Loads from environment variables or .env file.
    
    Environment variables:
    - LS_BASE_URL: Label Studio base URL (required)
    - LS_API_TOKEN: Label Studio API token (required)
    - LS_TIMEOUT: Request timeout in seconds (optional, default: 10)
    - LS_AUTH_TYPE: 'personal' (default, Bearer <token>) or 'legacy' (Token <token>)
    """
    def __init__(self):
        self.LS_BASE_URL = os.getenv('LS_BASE_URL')
        self.LS_API_TOKEN = os.getenv('LS_API_TOKEN')
        self.TIMEOUT = int(os.getenv('LS_TIMEOUT', '10'))  # seconds
        self.LS_AUTH_TYPE = os.getenv('LS_AUTH_TYPE', 'personal')
        # Validation
        missing = []
        if not self.LS_BASE_URL:
            missing.append('LS_BASE_URL')
        if not self.LS_API_TOKEN:
            missing.append('LS_API_TOKEN')
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    def __repr__(self):
        return (
            f"Config(LS_BASE_URL={self.LS_BASE_URL}, "
            f"LS_API_TOKEN={'***' if self.LS_API_TOKEN else None}, "
            f"TIMEOUT={self.TIMEOUT}, "
            f"LS_AUTH_TYPE={self.LS_AUTH_TYPE})"
        )

config = Config() 