# Gemini Enterprise ADK MCP Auth

This repository provides a sample implementation of a Multi-Client Proxy (MCP) server for authenticating to Gemini Enterprise, along with agent definitions.

## Project Structure

- **`1_cloud_run/`**: Contains the source code and deployment scripts for a FastAPI-based MCP server designed to be deployed on Google Cloud Run.
- **`2_agents/`**: Contains sample agent definitions for use with the MCP server.

## Getting Started

This guide will walk you through deploying the MCP server and running the agents.

### 1. Deploy the MCP Server

The MCP server is a containerized FastAPI application that can be deployed to Google Cloud Run. For detailed instructions on how to deploy the server, please see the README in the `1_cloud_run` directory:

[**Cloud Run MCP Server Deployment Guide**](./1_cloud_run/README.md)

### 2. Install Local Dependencies with `uv`

This project uses `uv` to manage Python dependencies for local development and testing. `uv` is an extremely fast Python package installer and resolver.

1.  Install `uv` on your local system.

    -   **macOS and Linux**:

        ```bash
        curl -LsSf https://astral.sh/uv/install.sh | sh
        ```

    -   **Windows**:

        ```powershell
        powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
        ```

2.  Once `uv` is installed, you can install the project dependencies using `uv sync`. This will install the dependencies defined in the `pyproject.toml` file in the root of the project.

    ```bash
    uv sync
    ```

## Usage

Once the MCP server is deployed and local dependencies are installed, you can proceed to use the sample agents. See the `2_agents/` directory for more information.
