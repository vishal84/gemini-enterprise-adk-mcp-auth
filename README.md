# Gemini Enterprise ADK MCP Auth

This repository provides a sample implementation of a Model Context Protocol (MCP) server hosted on Cloud Run as well as two ADK agents that can perform end user authentication to perform actions on behalf of an end user.

## Project Structure

- **`1_cloud_run/`**: Contains the source code and deployment scripts for a FastAPI-based MCP server designed to be deployed on Google Cloud Run.
- **`2_agents/`**: Contains sample agent definitions for use with the MCP server.

## Getting Started

This guide will walk you through deploying the MCP server and running the agents.

### 1. Deploy the MCP Server

The MCP server is a containerized FastAPI application that can be deployed to Google Cloud Run. In this section, you will authenticate with your Google Cloud project and deploy a containerized FastMCP server to Cloud Run.

To deploy the Cloud Run server, you will first need to authenticate the `gcloud` CLI to your GCP project.

#### 1. 🔑 Authenticate to Your GCP Project (CLI)

1. Sign in to Google Cloud in your browser from the CLI.

```bash
gcloud auth login
```

2. Authenticate Application Default Credentials (ADC) for local tooling.

```bash
gcloud auth application-default login
```

3. (Optional) Set your active GCP project.

```bash
gcloud config set project YOUR_PROJECT_ID
```

4. (Optional) Verify the active project is correct.

```bash
gcloud config get-value project
```

5. (Optional) Confirm the active authenticated account.

```bash
gcloud auth list
```

#### 2. 🛠️ Install Local Dependencies with `uv`

This project uses `uv` to manage Python dependencies. To install `uv`, follow these steps:

1.  Install `uv` on your local system.

    -   **macOS and Linux**:

        ```bash
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```

2.  Once `uv` is installed, you can install the project dependencies using `uv sync`.

    ```bash
    uv sync
    ```


#### 3. 🚀 Deploy to Cloud Run

Once you have authenticated to your GCP project, you can deploy the MCP server to Cloud Run using the provided `deploy.sh` script.

1.  Navigate to the `1_cloud_run` directory from the root of the project:

    ```bash
    cd 1_cloud_run
    ```

2.  Before running the script, create a `.env` file to configure the deployment. You can copy the example file:

    ```bash
    cp .env.example .env
    ```

    Then, edit the `.env` file with your desired settings for `PROJECT_ID`, `REGION`, etc. If you don't set `PROJECT_ID` in the `.env` file, the script will try to use the one from your `gcloud` configuration.

3.  Make the deployment script executable:

    ```bash
    chmod +x deploy.sh
    ```

4.  Run the deployment script:

    ```bash
    ./deploy.sh
    ```

The script will build the container image using Cloud Build, push it to Artifact Registry, and then deploy the service to Cloud Run. At the end of the process, it will print the URL of your deployed service.


## Test


Once the MCP server is deployed and local dependencies are installed, you can proceed to use the sample agents. See the `2_agents/` directory for more information.
