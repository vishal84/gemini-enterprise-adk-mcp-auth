import os
import logging
from pathlib import Path

import google.auth
import google.auth.transport.requests
from google.auth import impersonated_credentials

from fastapi.openapi.models import OAuth2
from fastapi.openapi.models import OAuthFlowAuthorizationCode
from fastapi.openapi.models import OAuthFlows

from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext

from google.adk.auth.auth_credential import AuthCredential
from google.adk.auth.auth_credential import AuthCredentialTypes
from google.adk.auth.auth_credential import OAuth2Auth

from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from dotenv import load_dotenv

# Load environment variables from the same directory as this file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "MCP SERVER URL NOT SET")
SERVICE_ACCOUNT_EMAIL = os.getenv("SERVICE_ACCOUNT_EMAIL")

# Define the OAuth2 authentication scheme for OpenID Connect with Google as the provider. The token returned
# by this flow will be used to provide the MCP server headers it can use to make authorization decisions based 
# on the authenticated user's identity and permissions. The scopes defined here specify the level of access the 
# token will have, including access to the user's email, profile, and cloud platform resources.
auth_scheme = OAuth2(
    flows=OAuthFlows(
        authorizationCode=OAuthFlowAuthorizationCode(
            authorizationUrl="https://accounts.google.com/o/oauth2/auth",
            tokenUrl="https://oauth2.googleapis.com/token",
            refreshUrl="https://oauth2.googleapis.com/token",
            scopes={
                "https://www.googleapis.com/auth/cloud-platform": "Cloud platform scope",
                "https://www.googleapis.com/auth/userinfo.email": "Email access scope",
                "https://www.googleapis.com/auth/userinfo.profile": "Profile access scope",
                "openid": "OpenID Connect scope",
            },
        )
    )
)

auth_credential = AuthCredential(
    auth_type=AuthCredentialTypes.OPEN_ID_CONNECT,
    oauth2=OAuth2Auth(
        client_id=CLIENT_ID, 
        client_secret=CLIENT_SECRET,
        redirect_uri="http://127.0.0.1:8000/dev-ui/",
    ),
)

# This function retrieves an ID token for authenticating to the Cloud Run service using impersonated credentials.
# It first loads the source credentials from the environment (which could be user credentials or service account 
# credentials), then creates impersonated credentials for the target service account, and finally generates an 
# ID token with the appropriate audience for the Cloud Run service. The ID token is used in the Authorization 
# header when making requests to the MCP server running on Cloud Run (protected by IAM authentication).
def get_cloud_run_token(target_url: str) -> str:

    audience = target_url.split('/mcp')[0]
    logger.info(f"Audience: {audience}")

    auth_req = google.auth.transport.requests.Request()

    target_scopes = [
        "https://www.googleapis.com/auth/cloud-platform",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid"
    ]

    logger.info("Loading source credentials from environment (ADC)...")
    source_credentials, _ = google.auth.default()
    
    target_credentials = impersonated_credentials.Credentials(
        source_credentials=source_credentials,
        target_principal=SERVICE_ACCOUNT_EMAIL,
        target_scopes = target_scopes,
    )

    jwt_token = impersonated_credentials.IDTokenCredentials(
        target_credentials=target_credentials,
        target_audience=audience,
        include_email=True,
    )

    try:
        jwt_token.refresh(auth_req)
        id_token = jwt_token.token

        # Use a tool like jwt.io to decode the token and verify 
        # your user is impersonating the service account
        logger.info(f"ID token: {id_token}")

        if not id_token:
            raise ValueError("Failed to fetch ID token: received None")
        return id_token
    except Exception as e:
        print(f"Error fetching Cloud Run ID token for {target_url}: {e}")
        raise

def mcp_header_provider(readonly_context: ReadonlyContext) -> dict[str, str]:
    
    id_token = get_cloud_run_token(MCP_SERVER_URL)

    # Construct headers for MCP requests, including the ID token for authentication
    return {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }

def mcp_logger(log_statement: str):
    logger.info(f"[McpToolset] {log_statement}", exc_info=True)

cloud_run_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=MCP_SERVER_URL,
        headers={
            "Authorization": f"Bearer {get_cloud_run_token(MCP_SERVER_URL)}",
        }
    ),
    # header_provider=mcp_header_provider,
    # auth_scheme=auth_scheme,
    # auth_credential=auth_credential,
    errlog=mcp_logger
)

root_agent = LlmAgent(
    model="gemini-2.5-pro",
    name="code_snippet_agent",
    instruction="""You are a helpful agent that has access to an MCP tool used to retrieve code snippets.
    - If a user asks what you can do, answer that you can provide code snippets from the MCP tool you have access to.
    - Provide the type as an input required to ask for a code snippet i.e. sql, python, javascript, json, or go.
    - Always use the MCP tool to get code snippets, never make up code snippets on your own.
    """,
    tools=[cloud_run_mcp],
)
