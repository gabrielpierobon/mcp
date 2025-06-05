#!/usr/bin/env python3
"""
Simple FastMCP server for n8n integration.
Uses FastMCP's built-in transport without custom routing.
"""

import os
import sys
import logging
from fastmcp import FastMCP

# Import tool registration functions
from tools import calculator_tool
from tools import get_weather_tool
from tools import brave_search
from tools import crawl4ai_tool
from tools import airtable_tool
from tools import playwright_browser_tool
from tools import google_sheets_tool
from tools import google_docs_tool
from tools import google_slides_tool
from tools import file_system_tool
from tools import file_writing_tool
from tools import screen_capture_tool

# Optional: Load .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# --- Server Configuration ---
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "n8n-mcp-server")
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))

logger.info(f"🚀 Starting MCP Server for n8n")
logger.info(f"Server: {MCP_SERVER_NAME}")
logger.info(f"Address: http://{MCP_HOST}:{MCP_PORT}")

# Initialize FastMCP server with settings
mcp = FastMCP(name=MCP_SERVER_NAME)

# --- Register Tools ---
logger.info("📦 Registering tools...")

# Core tools (always available)
calculator_tool.register(mcp)
get_weather_tool.register(mcp)
brave_search.register(mcp)
file_system_tool.register(mcp)
file_writing_tool.register(mcp)
screen_capture_tool.register(mcp)

# Data management
airtable_tool.register(mcp)

# Web automation (optional dependencies)
crawl4ai_tool.register(mcp)
playwright_browser_tool.register(mcp)

# Google Workspace (optional dependencies)
google_sheets_tool.register(mcp)
google_docs_tool.register(mcp)
google_slides_tool.register(mcp)

# Count registered tools
if hasattr(mcp, '_tool_manager') and hasattr(mcp._tool_manager, '_tools'):
    registered_tools = list(mcp._tool_manager._tools.keys())
    logger.info(f"✅ Registered {len(registered_tools)} tools")
else:
    logger.info("✅ Tools registered")

def log_environment_info():
    """Log environment status."""
    api_keys = {
        "BRAVE_API_KEY": "✅" if os.getenv("BRAVE_API_KEY") else "❌",
        "AIRTABLE_TOKEN": "✅" if os.getenv("AIRTABLE_PERSONAL_ACCESS_TOKEN") else "❌",
    }
    
    logger.info("🔑 API Keys:")
    for key, status in api_keys.items():
        logger.info(f"   {key}: {status}")

def main():
    """Main function to start the server."""
    
    log_environment_info()
    
    logger.info("🌐 Starting MCP server for n8n...")
    logger.info("")
    logger.info("🔗 n8n MCP Client Tool Configuration:")
    logger.info(f"   Try these endpoints in order:")
    logger.info(f"   1. http://host.docker.internal:{MCP_PORT}")
    logger.info(f"   2. http://host.docker.internal:{MCP_PORT}/sse")
    logger.info(f"   3. http://host.docker.internal:{MCP_PORT}/mcp")
    logger.info(f"   Authentication: None")
    logger.info("")
    logger.info("⚡ Starting server...")
    
    try:
        # Method 1: Try HTTP Streamable
        logger.info("🔄 Attempting HTTP transport...")
        mcp.run(transport="http", host=MCP_HOST, port=MCP_PORT)
        
    except Exception as e1:
        logger.warning(f"HTTP transport failed: {str(e1)}")
        
        try:
            # Method 2: Try SSE transport  
            logger.info("🔄 Attempting SSE transport...")
            mcp.run(transport="sse", host=MCP_HOST, port=MCP_PORT)
            
        except Exception as e2:
            logger.warning(f"SSE transport failed: {str(e2)}")
            
            try:
                # Method 3: Default run
                logger.info("🔄 Attempting default run...")
                mcp.run()
                
            except Exception as e3:
                logger.error(f"❌ All methods failed:")
                logger.error(f"   HTTP: {str(e1)}")
                logger.error(f"   SSE: {str(e2)}")
                logger.error(f"   Default: {str(e3)}")
                logger.error("")
                logger.error("💡 Check FastMCP version: pip list | grep fastmcp")
                logger.error("💡 Try updating: pip install --upgrade fastmcp")
                sys.exit(1)

if __name__ == "__main__":
    main()