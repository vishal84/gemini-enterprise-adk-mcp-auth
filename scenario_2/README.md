# Scenario 2: Deploy an ADK Agent w/ MCP Toolset in Gemini Enterprise using End User Authentication

This scenario guides you through setting up and testing an ADK agent that consumes a toolset from an MCP server using end user authentication. The guide covers two deployment options for the agent:

*   **Local:** Running the agent with `adk web`.
*   **Agent Engine:** Deploying the agent to Agent Engine and registering it with Gemini Enterprise with an `auth_id` used for end user authentication.

The MCP server is hosted on Cloud Run and provides a tool that returns information about an end user such as their name, email address and picture URL from their identity provider. In this case of this guide, you will Google Cloud Identity.

To access these tools, the ADK agent's service account must be granted the **Cloud Run Invoker** role.

## 1. OAuth Consent Configuration

In order to create an OAuth 2.0 application with credentials that can be used by the agent deployed in this scenario, you must create an OAuth 2.0 consent configuration in your Google Cloud project.

Follow the steps below to do so:

1.  Navigate to the **Google Cloud Console** in your browser.

2. 


To begin, you will deploy the Cloud Run server by building a container of the MCP server found in the `1_cloud_run/` directory.  Once deployed you will follow steps to test the ADK agent locally using `adk web` then deploy it to Agent Engine and register it with Gemini Enterprise.

