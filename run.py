import asyncio
import os
from typing import Any, Dict, List

import httpx
from mcp.server.fastmcp import FastMCP
# SseServerTransport might not be needed if mcp.sse_app() handles it
# from mcp.server.sse import SseServerTransport 
from starlette.applications import Starlette
from starlette.routing import Mount # Route might not be needed
from starlette.types import Scope, Receive, Send # Might not be needed for handlers
import uvicorn

# Import tool registration functions
from tools import calculator_tool
from tools import get_weather_tool
from tools import brave_search
from tools import crawl4ai_tool
from tools import airtable_tool

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
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "n8n-integration-server")
# N8N_BASE_URL and N8N_API_KEY are fetched by tools/helpers directly using os.getenv
# No longer needed as globals here for tool functions or make_n8n_request

# Initialize FastMCP server
mcp = FastMCP(MCP_SERVER_NAME)

# --- Register Tools ---
calculator_tool.register(mcp)
get_weather_tool.register(mcp)
brave_search.register(mcp)
crawl4ai_tool.register(mcp)
airtable_tool.register(mcp)

# Register Google Workspace tools
google_sheets_tool.register(mcp)
google_docs_tool.register(mcp)
google_slides_tool.register(mcp)

# --- Helper for n8n API Requests (REMOVED - MOVED TO tools/n8n_helpers.py) ---

# --- MCP Tools (REMOVED - MOVED TO SEPARATE FILES IN tools/ FOLDER) ---

# --- Starlette App Setup ---
# Try to use mcp.sse_app() if it exists
try:
    sse_application = mcp.sse_app()
    app = Starlette(
        routes=[
            Mount("/", app=sse_application, name="mcp_sse_app"),
        ]
    )
    print("INFO: Using mcp.sse_app() for routing.")
except AttributeError:
    print("WARNING: mcp.sse_app() not found. Falling back to manual handlers (which may be problematic).")
    # Fallback to previous manual setup (which had issues, here for completeness if needed for debug)
    # This part would need SseServerTransport and the handler functions to be defined as before
    # For now, if sse_app() fails, the server will likely fail to handle routes properly without further changes.
    async def fallback_handle_sse(scope: Scope, receive: Receive, send: Send):
        await send({'type': 'http.response.start', 'status': 501, 'headers': [(b'content-type', b'text/plain')]})
        await send({'type': 'http.response.body', 'body': b'Fallback SSE handler - mcp.sse_app() not found!', 'more_body': False})
    async def fallback_handle_messages_post(scope: Scope, receive: Receive, send: Send):
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
    
    # Ensure N8N_BASE_URL and N8N_API_KEY are defined before this block if used by mcp.sse_app() implicitly
    # Assuming mcp = FastMCP(MCP_SERVER_NAME) is defined globally earlier in the script
    if hasattr(mcp, '_tool_manager') and hasattr(mcp._tool_manager, '_tools'):
        print(f"Registered tools: {', '.join(mcp._tool_manager._tools.keys())}")
    else:
        print("Registered tools: (Could not determine from mcp object - check structure)")
    
    # Assuming 'app' is defined globally from the try/except block for mcp.sse_app()
    uvicorn.run(app, host=host, port=port)