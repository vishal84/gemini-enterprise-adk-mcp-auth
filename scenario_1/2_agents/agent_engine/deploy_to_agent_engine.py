import os
import logging
import vertexai
from vertexai import agent_engines
from vertexai.agent_engines import AdkApp
from agent import root_agent
from dotenv import load_dotenv, dotenv_values, set_key

local_agent = AdkApp(
    agent=root_agent,
    enable_tracing=True
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)
env_vars = dotenv_values(dotenv_path=env_path)

GOOGLE_CLOUD_PROJECT=env_vars.get("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION=env_vars.get("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET=env_vars.get("STAGING_BUCKET")
MCP_SERVER_URL=env_vars.get("MCP_SERVER_URL")
SERVICE_ACCOUNT_EMAIL=env_vars.get("SERVICE_ACCOUNT_EMAIL")

vertexai.init(
  project=GOOGLE_CLOUD_PROJECT,
  location=GOOGLE_CLOUD_LOCATION,
  staging_bucket=STAGING_BUCKET
)

client = vertexai.Client(
  project=GOOGLE_CLOUD_PROJECT,
  location=GOOGLE_CLOUD_LOCATION,
)

# Create on Agent Engine
remote_app = client.agent_engines.create(
  agent=local_agent,
  config=dict(
    agent_framework="google-adk",
    display_name="Code Snippet Agent",
    description="An ADK agent that returns sample code snippets.",
    gcs_dir_name="code-snippet-agent",
    # Use the staging bucket created when running the setup.sh script for deployment
    staging_bucket=STAGING_BUCKET,
    # Use the code-snippet-sa created to test locally for deployment
    service_account=SERVICE_ACCOUNT_EMAIL,
    extra_packages=["./agent_engine"],
    requirements=[
        "google-cloud-aiplatform[adk,agent_engines]",
        "fastmcp==2.13.1",
        "google-adk>=1.20.0",
        "python-dotenv>=1.0.0",
        "google-auth>=2.30.0",
    ],
    env_vars={
      "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
      "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
      "MCP_SERVER_URL": MCP_SERVER_URL,
    },
  ),
)

# Print the agent engine ID, you will need it in the later steps to initialize
# the ADK `VertexAiSessionService`.
_agent_engine_id=remote_app.api_resource.name
print(f"Agent Engine ID: {_agent_engine_id}")

def update_env_file(agent_engine_id, env_file_path):
  """Updates the .env file with the agent engine ID."""
  try:
    set_key(env_file_path, "AGENT_ENGINE_ID", agent_engine_id)
    print(f"Updated AGENT_ENGINE_ID in {env_file_path} to {agent_engine_id}")
  except Exception as e:
    print(f"Error updating .env file: {e}")

# log remote_app
logging.info(
  f"Deployed agent to Vertex AI Agent Engine successfully, resource name: {_agent_engine_id}"
)

# Update the .env file with the new Agent Engine ID
update_env_file(_agent_engine_id, env_path)