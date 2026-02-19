# Cloud Run MCP Server

In this section, you will authenticate with your Google Cloud project and deploy a containerized FastMCP server to Cloud Run.

To deploy the Cloud Run server, you will first need to authenticate the `gcloud` CLI to your GCP project.

## 1. Authenticate to Your GCP Project (CLI)

1. Sign in to Google Cloud in your browser from the CLI.

```bash
gcloud auth login
```

2. Authenticate Application Default Credentials (ADC) for local tooling.

```bash
gcloud auth application-default login
```

3. Set your active GCP project.

```bash
gcloud config set project YOUR_PROJECT_ID
```

4. Verify the active project is correct.

```bash
gcloud config get-value project
```

5. (Optional) Confirm the active authenticated account.

```bash
gcloud auth list
```

