import os
import re
import logging
from ast import Dict
from pathlib import Path
from typing import Optional

from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext

from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool

from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from dotenv import load_dotenv

# Load environment variables from the parent directory as this file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

AUTH_ID = os.getenv("AUTH_ID", "user-info-auth")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "MCP SERVER URL NOT SET")

# This function retrieves a token for authenticating to the Cloud Run service using the end users credentials via an auth_id 
# registered to Gemini Enterprise. The token is used in the Authorization header when making requests to the MCP 
# server running on Cloud Run to run tool calls as the end user.
def dynamic_token_injection(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> Optional[Dict]:
    token_key = None
    pattern = re.compile(r'^AUTH_ID.*')

    state_dict = tool_context.state.to_dict()
    matched_auth = {key: value for key, value in state_dict.items() if pattern.match(key)}
    if len(matched_auth) > 0:
        token_key = list(matched_auth.keys())[0]
    else:
        print("No valid tokens found")
        return None
    access_token = tool_context.state[token_key]
    # dynamic_auth_config = {DYNAMIC_AUTH_INTERNAL_KEY: access_token}
    # args[DYNAMIC_AUTH_PARAM_NAME] = json.dumps(dynamic_auth_config)
    return None

def mcp_header_provider(readonly_context: ReadonlyContext) -> dict[str, str]:
    token = readonly_context.state.get(AUTH_ID)

    if not token:
        logger.info("No id_token or access_token found!")
        return {}
    
    return {
        "Authorization": f"Bearer {token.strip()}",
        "Accept": "application/json, text/event-stream",
        "Cache-Control": "no-cache"
    }

def mcp_logger(log_statement: str):
    logger.info(f"[McpToolset] {log_statement}", exc_info=True)

cloud_run_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=MCP_SERVER_URL,
    ),
    header_provider=mcp_header_provider,
    errlog=mcp_logger,
)

root_agent = LlmAgent(
    model="gemini-2.5-pro",
    name="code_snippet_agent",
    instruction="""You are a code snippet agent that has access to an MCP tool used to retrieve code snippets.
    - If a user asks what you can do, answer that you can provide code snippets from the MCP tool you have access to.
    - Provide the types of snippets you can return i.e. sql, python, javascript, json, or go.
    - Always use the MCP tool to get code snippets, never make up code snippets on your own.
    """,
    tools=[cloud_run_mcp],
    before_tool_callback=[dynamic_token_injection]
)
