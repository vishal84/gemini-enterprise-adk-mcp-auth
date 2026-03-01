# Scenario 1: Deploy an ADK Agent w/ MCP Toolset in Gemini Enterprise using Service to Service Authentication

This scenario elaborates setup and testing of an ADK agent deployed locally using `adk web` and to Agent Engine registered with Gemini Enterprise to consume an MCP server hosted on Cloud Run. The Cloud Run server hosts an MCP server which returns sample code snippets in various languages i.e. SQL, python, json, javascript, go. The ADK agent requires the Cloud Run Invoker role in order to execute the tools that the MCP server makes available.

To begin, you will deploy the Cloud Run server by building a container of the MCP server found in the `1_cloud_run/` directory.  Once deployed you will follow steps to test the ADK agent locally using `adk web` then deploy it to Agent Engine and register it with Gemini Enterprise.

## 1. Deploy the MCP Server to Cloud Run

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

The ``deploy.sh`` script automates the deployment of a containerized application to Google Cloud Run. When you run this script, it performs the following actions:

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

### Test the MCP Server

To quickly test the deployed MCP server on Cloud Run, run the `test_mcp_client.py` script.

1. Ensure you are in the `1_cloud_run/` directory.

2. Run the [Cloud Run service proxy](https://docs.cloud.google.com/sdk/gcloud/reference/run/services/proxy) to allow your local terminal to authenticate to the service:

```bash
gcloud run services proxy code-snippet-mcp-server --region=us-central1
```

You will see output similar to the following in your terminal:

```text
Proxying to Cloud Run service [code-snippet-mcp-server] in project [project-id] region [us-central1]
http://127.0.0.1:8080 proxies to https://code-snippet-mcp-server-ofleaf4vuq-uc.a.run.app
```

3. In a new terminal window, execute the test script:

```bash
uv run python test_mcp_client.py
```

Upon execution, you should see calls to the `list_tools` operation of the MCP server and individual tool calls for `SQL` and `json` snippets.

When finished, close the terminal used to run the test script and press `Ctrl+C` in the terminal running the Cloud Run service proxy to stop the proxy.

Now that you've confirmed your MCP server is up and running on Cloud Run you will run an ADK agent locally using `adk web` to consume the MCP server in an ADK agent and consume the tools it makes available. Once tested locally, you will deploy the agent to Agent Engine and register it with Gemini Enterprise to perform the same.

## 2. Run the ADK agent locally

To run the ADK agent locally using `adk web` run do the following:

1. Navigate to the `2_adk_agents` directory:

2. Run the `setup.sh` script:

```bash
chmod +x setup.sh
./setup.sh
```

*   🆔 **Retrieves Project ID:** The script starts by getting your current Google Cloud Project ID from your `gcloud` configuration and exits if it's not set.

*   🤖 **Creates a Service Account:** It creates a dedicated service account named `code-snippet-sa` within your project. If the account already exists, it simply confirms its presence. This account will be used by Agent Engine to securely run your agent.

*   🔐 **Grants Necessary Permissions:** The script assigns two key roles to the new service account:
    *   `roles/run.invoker`: Allows the service account to invoke (run) the Cloud Run service where your tools are hosted.
    *   `roles/logging.logWriter`: Grants permission to write logs, which is essential for debugging and monitoring your agent.

*   🪣 **Creates a Staging Bucket:** It creates a Google Cloud Storage bucket with a unique name like `agent-staging-YOUR_PROJECT_ID`. This bucket is used by Agent Engine to store your agent's code and files during deployment. If the bucket already exists, it skips this step. The script also updates your `.env` file with the staging bucket name.

*   ✅ **Confirmation:** Finally, the script prints the name of the staging bucket to your console so you know where your agent's files will be staged.

When the script is finished executing you will see it has confirmed the creation of:
* A service account `code-snippet-sa@[project-id].iam.gserviceaccount.com`
* A staging bucket `agent-staging-[project-id]`
* The roles above granted to the service account

3. Run the following command:

```bash
uv run adk web
```

This will run the [ADK web](https://google.github.io/adk-docs/runtime/web-interface/) interface in your local terminal so that you can test the agent via a chat interface.

```diff
+ +-----------------------------------------------------------------------------+
+ | ADK Web Server started                                                      |
+ |                                                                             |
+ | For local testing, access at http://127.0.0.1:8000.                         |
+ +-----------------------------------------------------------------------------+
```

3. Open the link returned when running `adk web` in your browser. Change the dropdown to the `local/` folder to test your agent.

#### Test the agent locally

4. Sample agent interaction below:

<div style="background-color: #ffffff; border-radius: 8px; padding: 12px; margin-bottom: 10px; color: #000">
  <strong>User:</strong> Hi! What can you do?
</div>

<div style="background-color: #00aeff; border-radius: 8px; padding: 12px; margin-bottom: 10px; color: #000">
  <strong>Agent:</strong> Hello! I can provide you with code snippets for sql, python, javascript, json, or go. What type of code snippet would you like?</code></pre>
</div>

<div style="background-color: #ffffff; border-radius: 8px; padding: 12px; margin-bottom: 10px; color: #000000">
  <strong>User:</strong> Provide me with a SQL code snippet
</div>

<div style="background-color: #00aeff; border-radius: 8px; padding: 12px; margin-bottom: 10px; color: #000">
  <strong>Agent:</strong>
<pre><code>SELECT
    o.order_id,
    o.order_date,
    c.customer_name,
    p.product_name,
    oi.quantity,
    oi.price_per_unit
FROM
    orders AS o
JOIN
    customers AS c ON o.customer_id = c.customer_id
JOIN
    order_items AS oi ON o.order_id = oi.order_id
JOIN
    products AS p ON oi.product_id = p.product_id
WHERE
    o.order_date >= '2024-01-01'
ORDER BY
    o.order_date DESC, c.customer_name ASC;
</code></pre>
</div>

## 3. Deploy the ADK agent to Agent Engine and Register with Gemini Enterprise


