import os
import logging
import json
import requests
import google.auth
import google.auth.transport.requests
from dotenv import load_dotenv, dotenv_values

def main():
    """
    Registers a deployed Agent Engine instance to a Gemini Enterprise App.
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger(__name__)

    # --- Agent Configuration ---
    AGENT_DISPLAY_NAME = "Code Snippet Agent"
    AGENT_DESCRIPTION = "An ADK agent that returns sample code snippets from a Cloud Run hosted MCP server."

    # --- Environment Variables ---
    logger.info("Loading environment variables...")
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    load_dotenv(dotenv_path=env_path)
    env_vars = dotenv_values(dotenv_path=env_path)

    required_vars = [
        "AGENT_ENGINE_ID",
        "GEMINI_ENTERPRISE_APP_ID", # Also referred to as as_app in the API
    ]

    missing_vars = [var for var in required_vars if not env_vars.get(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please add them to your .env file in the '2_agents' directory.")
        return

    agent_engine_id = env_vars.get("AGENT_ENGINE_ID")
    gemini_enterprise_app_id = env_vars.get("GEMINI_ENTERPRISE_APP_ID")

    logger.info("Successfully loaded environment variables.")

    # --- Registration Logic ---
    try:
        logger.info("Attempting to register agent with Gemini Enterprise...")

        # Get default credentials and project ID from the environment
        credentials, project = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        access_token = credentials.token

        api_url = (
            f"https://discoveryengine.googleapis.com/v1alpha/projects/{project}/locations/global/"
            f"collections/default_collection/engines/{gemini_enterprise_app_id}/assistants/default_assistant/agents"
        )

        payload = {
            "displayName": AGENT_DISPLAY_NAME,
            "description": AGENT_DESCRIPTION,
            "adk_agent_definition": {
                "tool_settings": {
                    "tool_description": "An ADK agent that returns sample code snippets.",
                },
                "provisioned_reasoning_engine": {
                    "reasoning_engine": agent_engine_id
                },
            }
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "x-goog-user-project": project,
        }

        response = requests.post(api_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raise an exception for bad status codes

        logger.info("✅ Successfully registered agent to Gemini Enterprise!")
        logger.info(f"💬 Response: {response.json()}")

    except google.auth.exceptions.DefaultCredentialsError:
        logger.error("Authentication failed. Please run 'gcloud auth application-default login'.")
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred during the API request: {e}")
        if e.response:
            logger.error(f"Response body: {e.response.text}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
