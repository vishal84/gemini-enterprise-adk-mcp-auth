# Scenario 2: Deploy an ADK Agent w/ MCP Toolset in Gemini Enterprise using End User Authentication

This scenario guides you through setting up and testing an ADK agent that consumes a toolset from an MCP server using end user authentication. The guide covers two deployment options for the agent:

*   **Local:** Running the agent with `adk web`.
*   **Agent Engine:** Deploying the agent to Agent Engine and registering it with Gemini Enterprise with an `auth_id` used for end user authentication.

The MCP server is hosted on Cloud Run and provides a tool that returns information about an end user such as their name, email address and picture URL from their identity provider. In this case of this guide, you will Google Cloud Identity.

To access these tools, the ADK agent's service account must be granted the **Cloud Run Invoker** role.

## 1. OAuth Consent Configuration

This setup involves configuring the OAuth consent screen and credentials in your Google Cloud Project and then registering those credentials as an Authorization Resource for use in agentic workflows (e.g., Agentspace). If you’ve already set up OAuth consent in your project you will not need to perform this step.

### Step 1: Configure the OAuth Consent Screen
In the Google Cloud Console:

1. Navigate to **APIs & Services > OAuth consent screen**. Click **Get Started**.
2. Give the application a name and select your GCP project’s user as the User support email address:
    - **App name:** `Gemini Enterprise`
    - **User support email:** (Use your gcp project user’s email address)

Click **Next**.

3. Under Audience select the **Internal** radio option. Click **Next**.
4. Use your gcp project user’s email address for Contact Information. Click **Next**.
5. Select the “I agree” checkbox. Then click **Continue**.

Click **Create** once the steps above are completed. 

- ✅ You should see a notification that an OAuth configuration has been created.

### Step 2: Create OAuth 2.0 Client Credentials
In this step, you register an OAuth client now that you’ve configured OAuth consent in your GCP project. 

1. Navigate to **APIs & Services > Credentials**.
2. Click **+ Create Credentials > OAuth client ID**.
    - For **Application type**, select **Web application**.
    - Enter a **Name** for your OAuth client ID. 
        - For example, `Gemini Enterprise ADK Client`

3. Under **Authorized redirect URIs**, click **Add URI**. For ADK and Vertex AI Search agents, you typically must include the following URIs:
    - `https://vertexaisearch.cloud.google.com/oauth-redirect` (redirect URI for GE)
    - `https://vertexaisearch.cloud.google.com/static/oauth/oauth.html` (same as above)
    - `http://127.0.0.1/dev-ui/` (redirect URI for ADK web)

Click **Create**. 

- ⚠️ You should see a dialog showing you your newly created **Client ID** and **Client secret**. 
- 🚨 Copy these values immediately and store them securely. You’ll need to reference these values in a later step.

Now that you’ve created an OAuth consent configuration and application credentials, you can run the steps found in the git repository’s README file to deploy the MCP server and test the agents.

## 2. Deploy the MCP Server to Cloud Run

To deploy the MCP server:

1. Navigate to the `1_cloud_run/` directory:

```bash
cd 1_cloud_run/
```

2. Make the `deploy.sh` script runnable in your terminal:

```bash
chmod +x deploy.sh
```

3. Run the `deploy.sh` script:

```bash
./deploy.sh
```

Similar to Scenario 1 in this repo, the ``deploy.sh`` script automates the deployment of a containerized application to Google Cloud Run. When you run this script, it performs the following actions:

1.  **⚙️ Configuration and Validation:**
    *   It loads any environment variables you have set in a `.env` file.
    *   It checks if you have the `gcloud` command-line tool installed.
    *   It determines your Google Cloud Project ID and a default region (`us-central1`), though you can override these with environment variables.

2.  **☁️ Enables Google Cloud Services:**
    *   It silently enables the necessary Google Cloud services for you, including Cloud Run for hosting, Artifact Registry for storing container images, and Cloud Build for running the deployment pipeline.

3.  **🔐 Permissions Management:**
    *   The script automatically grants the necessary IAM permissions to the Cloud Build service account. This allows it to deploy the application to Cloud Run on your behalf, so you don't have to manually configure these permissions.

4.  **📦 Container Repository Setup:**
    *   It ensures that a container repository exists in Artifact Registry. If it doesn't, the script creates it for you. This repository is where the container image for your application will be stored.

5.  **🚀 Application Build and Deployment:**
    *   The script initiates a Cloud Build process, which reads the ``cloudbuild.yaml`` file to build your application's container image, push it to the Artifact Registry repository, and then deploy it to Cloud Run.

6.  **🎉 Provides Service URL:**
    *   Once the deployment is complete, the script fetches the URL of your newly deployed service and prints it to the console. 

<div style="border-left: 6px solid #acacb0; background-color: #5a5a5a; padding: 15px; margin: 20px 0;">
  <p>⚠️ <strong>Important:</strong> Copy the service URL from the previous step and paste it into the <code>.env</code> file located in the <code>2_agents/</code> directory. Set it as the value for the <code>MCP_SERVER_URL</code> variable.</p>
  <p><strong>🚨 Important:</strong> Ensure the URL ends with <code>/mcp</code>.</p>
</div>







```bash
uv run adk deploy agent_engine --display_name "User Info Agent" --description "ADK agent that returns user information from an MCP server hosted on Cloud Run" --env_file .env ./agent_engine/
```
copy agent_id to .env file