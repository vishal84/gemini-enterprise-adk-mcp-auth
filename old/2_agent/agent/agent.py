import logging
from . import patch_adk
from pathlib import Path

import google.auth
import google.auth.transport.requests
import google.oauth2.id_token

from google.adk.agents import LlmAgent

from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes
from google.adk.auth.auth_credential import HttpAuth, HttpCredentials

from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from fastapi.openapi.models import HTTPBearer

from dotenv import dotenv_values

# Load environment variables from the same directory as this file
env_path = Path(__file__).parent / '.env'
config = dotenv_values(dotenv_path=env_path) or {}

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

CLIENT_ID = config.get("CLIENT_ID")
CLIENT_SECRET = config.get("CLIENT_SECRET")
MCP_SERVER_URL = config.get("MCP_SERVER_URL", "MCP SERVER URL NOT SET")
AUTH_ID = config.get("AUTH_ID", "AUTH ID NOT SET")

class GeminiEnterpriseHttpAuth(HttpAuth):
    scheme: str = "ge_auth_resource"
    credentials: HttpCredentials = HttpCredentials()
    ge_auth_id: str

auth_credential = AuthCredential(
    auth_type=AuthCredentialTypes.HTTP,
    http=GeminiEnterpriseHttpAuth(ge_auth_id=AUTH_ID)
)
auth_scheme = HTTPBearer(bearerFormat='JWT')

def get_cloud_run_token(target_url: str) -> str:
    """
    Fetches an ID token for authenticating to a Cloud Run service.
    
    This function uses Application Default Credentials (ADC) to obtain an identity token
    that can be used to authenticate requests to Cloud Run services that require authentication.
    
    Args:
        target_url: The URL of the Cloud Run service to authenticate to.
        
    Returns:
        str: The ID token that can be used in the Authorization header.
        
    Raises:
        Exception: If unable to fetch the ID token (e.g., authentication failure).
        
    Note:
        Requires the caller to have the run.invoker role on the Cloud Run service.
    """
    auth_req = google.auth.transport.requests.Request()
    audience = target_url.split('/mcp')[0]

    try:
        id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
        logger.info(f"ID token: {id_token}")

        if not id_token:
            raise ValueError("Failed to fetch ID token: received None")
        return id_token
    except Exception as e:
        print(f"Error fetching Cloud Run ID token for {target_url}: {e}")
        raise

def mcp_header_provider(context) -> dict[str, str]:
    """
    Provides authentication headers for MCP server requests.
        
    Returns:
        dict: Headers including the Bearer token for authentication.
        
    Raises:
        Exception: If unable to get Cloud Run token.
    """
    id_token = get_cloud_run_token(MCP_SERVER_URL)
    logger.info(f"Token: \n{id_token}\n")

    return {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }

cloud_run_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=MCP_SERVER_URL,
    ),
    header_provider=mcp_header_provider,
    auth_scheme=auth_scheme,
    auth_credential=auth_credential
)

root_agent = LlmAgent(
    model="gemini-2.5-pro",
    name="code_snippet_agent",
    instruction="""You are a helpful agent that has access to an MCP tool used to retrieve code snippets.
    - If a user asks what you can do, answer that you can provide code snippets from the MCP tool you have access to.
    - Provide the function name to call to ask for a snippet:
    - `get_snippet("<type>")` where <type> can be sql, python, javascript, json, or go.
    - Always use the MCP tool to get code snippets, never make up code snippets on your own.
    """,
    tools=[cloud_run_mcp],
)
