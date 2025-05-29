import asyncio
import os
from typing import Any, Dict, List
import logging
import sys

import httpx
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount
import uvicorn

# Import tool registration functions
from tools import calculator_tool
from tools import get_weather_tool
from tools import brave_search
from tools import crawl4ai_tool
from tools import airtable_tool
from tools import playwright_browser_tool

# Import Google Workspace tools (separate modules)
from tools import google_sheets_tool
from tools import google_docs_tool
from tools import google_slides_tool

# Import file system tools (read and write)
from tools import file_system_tool
from tools import file_writing_tool  # NEW: File writing capabilities

from tools import screen_capture_tool

# Optional: Load .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging to stderr instead of stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Important: use stderr, not stdout
)
logger = logging.getLogger(__name__)

# --- Server Configuration ---
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "enhanced-mcp-server")

# Initialize FastMCP server
mcp = FastMCP(MCP_SERVER_NAME)

# --- Register Tools ---
logger.info("Registering tools...")

# Core tools
calculator_tool.register(mcp)
get_weather_tool.register(mcp)
brave_search.register(mcp)

# Web automation tools
crawl4ai_tool.register(mcp)
playwright_browser_tool.register(mcp)

# Data management tools
airtable_tool.register(mcp)

# Google Workspace tools
google_sheets_tool.register(mcp)
google_docs_tool.register(mcp)
google_slides_tool.register(mcp)

# File system tools (read-only and write capabilities)
file_system_tool.register(mcp)
file_writing_tool.register(mcp)  # NEW: Register file writing tools

screen_capture_tool.register(mcp)

logger.info("All tools registered successfully")

# --- Starlette App Setup ---
try:
    sse_application = mcp.sse_app()
    app = Starlette(
        routes=[
            Mount("/", app=sse_application, name="mcp_sse_app"),
        ]
    )
    logger.info("Using mcp.sse_app() for routing.")
except AttributeError:
    logger.warning("mcp.sse_app() not found. Using fallback handlers.")
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
    # Detect if running from Claude Desktop (stdio) or standalone (HTTP)
    import sys
    
    # List registered tools
    if hasattr(mcp, '_tool_manager') and hasattr(mcp._tool_manager, '_tools'):
        registered_tools = list(mcp._tool_manager._tools.keys())
        logger.info(f"Registered {len(registered_tools)} tools:")
        for tool in sorted(registered_tools):
            logger.info(f"  - {tool}")
    
    # Check if running from Claude Desktop (has specific env or args pattern)
    if len(sys.argv) == 1 and not os.getenv("MCP_FORCE_HTTP"):
        # Default to stdio for Claude Desktop
        logger.info("Starting MCP server with stdio transport for Claude Desktop")
        mcp.run(transport="stdio")
    else:
        # HTTP/SSE for n8n and other integrations
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "8000"))
        
        logger.info(f"Starting MCP server on {host}:{port}")
        logger.info(f"SSE endpoint: http://{host}:{port}/sse")
        
        uvicorn.run(app, host=host, port=port)