# Gemini Enterprise ADK MCP Auth

This repository provides two sample scenarios on how to deploy ADK agents that consume an MCP server's tools both locally, using `adk web`, and via Agent Engine registered with Gemini Enterprise. Each scenario will guide you through consuming an MCP server using a service account 

### Prerequisites

To run each scenario you must have:
- A Google Cloud project
- `gcloud` installed locally
- `uv` installed locally to manage Python dependencies and create virtual environments
- A Gemini Enterprise app created in your Google Cloud project

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

This project uses `uv` to manage Python dependencies. To install `uv`, do the following:

1.  Install `uv` on your local system.

    -   **macOS and Linux**:

        ```bash
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```

    -   **Windows**:

        ```powershell
        powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
        ```

## Scenario 1: Deploy an ADK Agent w/ MCP Toolset in Gemini Enterprise using Service to Service Authentication

In scenario 1, you will deploy an MCP server hosted on Cloud Run and test its invocation using `adk web` locally and when deployed to Agent Engine and registered with Gemini Enterprise.

Navigate to the `scenario_1/` folder and open the `README.md` file to follow the guide for deploying the MCP server hosted on Cloud Run sample ADK agent locally using `adk web` and to Agent Engine registered with Gemini Enterprise to consume an MCP server

## Scenario 2: ...

