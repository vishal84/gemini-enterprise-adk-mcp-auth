# Scenario 1: Deploy an ADK Agent w/ MCP Toolset in Gemini Enterprise using Service to Service Authentication

This scenario elaborates setup and testing of an ADK agent deployed locally using `adk web` and to Agent Engine registered with Gemini Enterprise to consume an MCP server hosted on Cloud Run.

To begin, you will deploy the Cloud Run server by building a container of the MCP server found in the `1_cloud_run/` directory.  Once deployed you will follow steps to test the ADK agent locally using `adk web` then deploy it to Agent Engine and register it with Gemini Enterprise.

## Deploy the MCP Server to Cloud Run

To deploy the MCP server:

1. Navigate to the `1_cloud_run/` directory:

```bash
cd 1_cloud_run/
```



### Test the MCP Server

