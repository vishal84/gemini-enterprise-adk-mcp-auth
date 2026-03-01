# Gemini Enterprise ADK MCP Auth

This repository provides two sample scenarios on how to deploy ADK agents that consume an MCP server's tools both locally, using `adk web`, and via Agent Engine registered with Gemini Enterprise. Each scenario will guide you through consuming an MCP server using a service account 

### Prerequisites

To run each scenario you must have:
- A Google Cloud project
- `gcloud` installed locally
- `uv` installed locally to manage Python dependencies and create virtual environments


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

