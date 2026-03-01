# Gemini Enterprise ADK MCP Auth

This repository provides two sample scenarios for deploying an ADK agent that consumes tools from an MCP server using different authentication mechanisms. The guides cover running the agent both locally with `adk web` and deploying it to Agent Engine for use in Gemini Enterprise.

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

See the `scenario_1/README.md` file for a comprehensive guide that covers:

- Deploying the MCP server to Cloud Run.
- Running the ADK agent locally with `adk web`.
- Deploying the ADK agent to Agent Engine and registering with Gemini Enterprise.

## Scenario 2: Deploy an ADK Agent w/ MCP Toolset in Gemini Enterprise using End User Based Authentication


