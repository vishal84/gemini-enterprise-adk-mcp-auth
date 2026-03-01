import os
import logging
from pathlib import Path
from httplib2 import Credentials

import google.auth
import google.auth.transport.requests
from google.auth import impersonated_credentials

from fastapi.openapi.models import OAuth2
from fastapi.openapi.models import OAuthFlowAuthorizationCode
from fastapi.openapi.models import OAuthFlows

from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.agents.callback_context import CallbackContext

from google.adk.auth import AuthConfig, AuthCredential, AuthCredentialTypes, OAuth2Auth

from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from dotenv import load_dotenv

# Load environment variables from the same directory as this file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "MCP SERVER URL NOT SET")
SERVICE_ACCOUNT_EMAIL = os.getenv("SERVICE_ACCOUNT_EMAIL")

# This function retrieves an ID token for authenticating to the Cloud Run service using the service account of the 
# running agent engine instance. The ID token is used in the Authorization header when making requests to the MCP 
# server running on Cloud Run (protected by IAM authentication).
def get_cloud_run_token(target_url: str) -> str:

    audience = target_url.split('/mcp')[0]
    logger.info(f"Audience: {audience}")

    auth_req = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)

    return id_token

def mcp_logger(log_statement: str):
    logger.info(f"[McpToolset] {log_statement}", exc_info=True)

cloud_run_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=MCP_SERVER_URL,
        headers={
            "Authorization": f"Bearer {get_cloud_run_token(MCP_SERVER_URL)}",
        }
    ),
    errlog=mcp_logger
)

root_agent = LlmAgent(
    model="gemini-2.5-pro",
    name="code_snippet_agent",
    instruction="""You are a code snippet agent that has access to an MCP tool used to retrieve code snippets.
    - If a user asks what you can do, answer that you can provide code snippets from the MCP tool you have access to.
    - Provide the types of snippets you can return i.e. sql, python, javascript, json, or go.
    - Always use the MCP tool to get code snippets, never make up code snippets on your own.
    """,
    tools=[cloud_run_mcp]
)
