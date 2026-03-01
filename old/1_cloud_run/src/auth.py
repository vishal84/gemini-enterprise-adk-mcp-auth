import asyncio
import logging
import os
import contextvars
import requests
from typing import List, Dict, Any

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.middleware import Middleware, MiddlewareContext

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

user_token = contextvars.ContextVar("user_token", default=None)

# --- Authentication Middleware ---
class AuthMiddleware(Middleware):
    """
    A custom middleware to enforce bearer token authentication.
    """
    async def on_request(self, context: MiddlewareContext, call_next):
        """
        This hook is called for every incoming request that expects a response.
        """
        logger.info(">>> 🛡️ AuthMiddleware: Checking for authorization header...")

        headers = get_http_headers() or {}
        auth_header = headers.get("authorization")

        if not auth_header or not auth_header.lower().startswith("bearer "):
            logger.warning(">>> 🛡️ AuthMiddleware: Unauthorized. Missing or invalid bearer token.")
            # Deny the request if the token is missing or invalid
            raise Exception("Unauthorized: Bearer token is missing or invalid.")

        # In a real application, you would validate the token here.
        # For this example, we'll just log that it's present.
        logger.info(">>> 🛡️ AuthMiddleware: Bearer token found. Proceeding with request.")
        # Split the header string "Bearer <token>" and get the token part.
        try:
            token = auth_header.split()[1]
            logger.info(f">>> 🛡️ AuthMiddleware: token: {token}")

            # In a real application, you would validate the token here.
            # For this example, we'll just log that it's present and extracted.
            # Store the token in the context for other tools/dependencies to use
            user_token.set(token)
            logger.info(">>> 🛡️ AuthMiddleware: Bearer token found and stored in context.")
        except IndexError:
            user_token.set(None)
            logger.warning(">>> 🛡️ AuthMiddleware: Malformed Authorization header. Token could not be extracted.")
            raise Exception("Unauthorized: Malformed Bearer token.")
        
        # If the token is valid, proceed to the next middleware or the tool itself
        return await call_next(context)

# --- MCP Server Setup ---
mcp = FastMCP("Code Snippet MCP Server")
# Add the authentication middleware to the server
mcp.add_middleware(AuthMiddleware())

# --- Tool Definitions ---
@mcp.tool()
def get_user_info_from_access_token(context: MiddlewareContext) -> str:
    """
    Uses a Google OAuth2 Access Token to retrieve user information from the userinfo endpoint.
    """
    logger.info(">>> 🛠️ Tool: 'get_user_info_from_access_token' called.")
    
    # Get the token from the context passed into the tool
    access_token = user_token.get()
    logger.info(f">>> 🛠️ Tool: Retrieved access token from context: {access_token}"
                )
    if not access_token:
        return "Error: Auth token not found in the request context. The middleware may not have run correctly."

    userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(userinfo_endpoint, headers=headers)
        response.raise_for_status()
        
        user_info = response.json()
        logger.info(f">>> 🛠️ Tool: Successfully retrieved user info: {user_info}")

        name = user_info.get("name", "N/A")
        email = user_info.get("email", "N/A")
        picture = user_info.get("picture", "N/A")

        return (
            f"Successfully retrieved user info:\n"
            f"- Name: {name}\n"
            f"- Email: {email}\n"
            f"- Picture URL: {picture}"
        )

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error while calling userinfo endpoint: {e}")
        if e.response.status_code == 401:
            return "Error: The provided access token is invalid or expired."
        return f"Error: Failed to retrieve user info. Server returned status {e.response.status_code}."
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return "An unexpected error occurred on the server while retrieving user info."

# --- Server Execution ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info(f"🚀 MCP server started on port {port}")
    asyncio.run(
        mcp.run_async(
            transport="streamable-http",
            host="0.0.0.0",
            port=port,
        )
    )
