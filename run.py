import asyncio
import os
from typing import Any, Dict, List

import httpx
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount
import uvicorn

# Import tool registration functions
from tools import calculator_tool
from tools import get_weather_tool
from tools import brave_search
from tools import crawl4ai_tool
from tools import airtable_tool
from tools import playwright_browser_tool  # NEW: Browser automation tools

# Import Google Workspace tools (separate modules)
from tools import google_sheets_tool
from tools import google_docs_tool
from tools import google_slides_tool

# Optional: Load .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- Server Configuration ---
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "enhanced-mcp-server")

# Initialize FastMCP server
mcp = FastMCP(MCP_SERVER_NAME)

# --- Register Tools ---
print("INFO: Registering tools...")

# Core tools
calculator_tool.register(mcp)
get_weather_tool.register(mcp)
brave_search.register(mcp)

# Web automation tools
crawl4ai_tool.register(mcp)
playwright_browser_tool.register(mcp)  # NEW: Browser automation

# Data management tools
airtable_tool.register(mcp)

# Google Workspace tools
google_sheets_tool.register(mcp)
google_docs_tool.register(mcp)
google_slides_tool.register(mcp)

print("INFO: All tools registered successfully")

# --- Starlette App Setup ---
try:
    sse_application = mcp.sse_app()
    app = Starlette(
        routes=[
            Mount("/", app=sse_application, name="mcp_sse_app"),
        ]
    )
    print("INFO: Using mcp.sse_app() for routing.")
except AttributeError:
    print("WARNING: mcp.sse_app() not found. Using fallback handlers.")
    async def fallback_handle_sse(scope, receive, send):
        await send({'type': 'http.response.start', 'status': 501, 'headers': [(b'content-type', b'text/plain')]})
        await send({'type': 'http.response.body', 'body': b'Fallback SSE handler - mcp.sse_app() not found!', 'more_body': False})
    
    async def fallback_handle_messages_post(scope, receive, send):
        await send({'type': 'http.response.start', 'status': 501, 'headers': [(b'content-type', b'text/plain')]})
        await send({'type': 'http.response.body', 'body': b'Fallback POST handler - mcp.sse_app() not found!', 'more_body': False})
    
    app = Starlette(
        routes=[
            Mount("/sse", app=fallback_handle_sse, name="sse_endpoint"),
            Mount("/messages", app=fallback_handle_messages_post, name="message_post_endpoint"),
        ]
    )

# --- Main Execution ---
if __name__ == "__main__":
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8000"))
    
    # List registered tools
    if hasattr(mcp, '_tool_manager') and hasattr(mcp._tool_manager, '_tools'):
        registered_tools = list(mcp._tool_manager._tools.keys())
        print(f"INFO: Registered {len(registered_tools)} tools:")
        for tool in sorted(registered_tools):
            print(f"  - {tool}")
    else:
        print("INFO: Could not determine registered tools from mcp object")
    
    print(f"INFO: Starting MCP server on {host}:{port}")
    print(f"INFO: SSE endpoint available at http://{host}:{port}/sse")
    print(f"INFO: Server name: {MCP_SERVER_NAME}")
    
    uvicorn.run(app, host=host, port=port)