import asyncio

from fastmcp import Client

async def test_server():
    # Test the MCP server using streamable-http transport.
    # run: gcloud run services proxy code-snippet-mcp-server --region=us-central1
    async with Client("http://localhost:8080/mcp") as client:
       
        # 1. List available tools
        tools = await client.list_tools()
        for tool in tools:
            print(f">>> 🛠️  Tool found: {tool.name}")

        # 2. Call get_code_snippet tool
        print(">>> 🪛  Calling get_code_snippet tool for SQL")
        result = await client.call_tool("get_code_snippet", {"type": "sql"})
        if not result.is_error:
            print("<<< ✅ Result:")
            # Assuming the result data is a string with the code snippet
            print(result.data)
        else:
            print(f"<<< ❌ Error: {result.data}")

         # 3. Call get_code_snippet tool
        print(">>> 🪛  Calling get_code_snippet tool for JSON")
        result = await client.call_tool("get_code_snippet", {"type": "json"})
        if not result.is_error:
            print("<<< ✅ Result:")
            # Assuming the result data is a string with the code snippet
            print(result.data)
        else:
            print(f"<<< ❌ Error: {result.data}")

if __name__ == "__main__":
    asyncio.run(test_server())