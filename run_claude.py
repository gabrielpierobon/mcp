#!/usr/bin/env python3
"""
Dedicated stdio server for Claude Desktop integration.
This server runs exclusively in stdio mode for Claude Desktop.
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
from tools import rag_knowledge_base_tool

# Optional: Load .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging to stderr (important for stdio mode)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# --- Server Configuration ---
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "claude-mcp-server")

logger.info(f"🤖 Starting MCP Server for Claude Desktop")
logger.info(f"Server: {MCP_SERVER_NAME}")
logger.info(f"Transport: stdio")

# Initialize FastMCP server
mcp = FastMCP(MCP_SERVER_NAME)

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

rag_knowledge_base_tool.register(mcp)

# Count registered tools
if hasattr(mcp, '_tool_manager') and hasattr(mcp._tool_manager, '_tools'):
    registered_tools = list(mcp._tool_manager._tools.keys())
    logger.info(f"✅ Registered {len(registered_tools)} tools:")
    
    # Group tools by category for better organization
    core_tools = [t for t in registered_tools if any(x in t for x in ['calculator', 'get_weather', 'brave_', 'read_file', 'write_file', 'quick_capture'])]
    data_tools = [t for t in registered_tools if any(x in t for x in ['airtable', 'google_sheets', 'google_docs', 'google_slides'])]
    web_tools = [t for t in registered_tools if any(x in t for x in ['crawl', 'navigate', 'click', 'browser'])]
    file_tools = [t for t in registered_tools if any(x in t for x in ['list_directory', 'search_files', 'get_file', 'create_project'])]
    
    if core_tools:
        logger.info(f"   🔧 Core: {', '.join(sorted(core_tools))}")
    if data_tools:
        logger.info(f"   📊 Data: {', '.join(sorted(data_tools))}")
    if web_tools:
        logger.info(f"   🌐 Web: {', '.join(sorted(web_tools))}")
    if file_tools:
        logger.info(f"   📁 Files: {', '.join(sorted(file_tools))}")
        
else:
    logger.info("✅ Tools registered (count unavailable)")

# --- Environment Status ---
def log_environment_status():
    """Log the status of important environment variables and dependencies."""
    logger.info("🔧 Environment Status:")
    
    # API Keys
    api_status = {
        "BRAVE_API_KEY": "🟢" if os.getenv("BRAVE_API_KEY") else "🔴",
        "AIRTABLE_TOKEN": "🟢" if os.getenv("AIRTABLE_PERSONAL_ACCESS_TOKEN") else "🔴",
        "GOOGLE_CREDS": "🟢" if os.path.exists(os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")) else "🔴"
    }
    
    for key, status in api_status.items():
        logger.info(f"   {key}: {status}")
    
    # Optional features
    features = {}
    try:
        import crawl4ai
        features["Web Crawling"] = "🟢"
    except ImportError:
        features["Web Crawling"] = "🔴"
    
    try:
        import playwright
        features["Browser Automation"] = "🟢"
    except ImportError:
        features["Browser Automation"] = "🔴"
        
    try:
        import google.auth
        features["Google Workspace"] = "🟢"
    except ImportError:
        features["Google Workspace"] = "🔴"
        
    try:
        import mss
        features["Screen Capture"] = "🟢"
    except ImportError:
        features["Screen Capture"] = "🔴"
    
    logger.info("📦 Optional Features:")
    for feature, status in features.items():
        logger.info(f"   {feature}: {status}")

# --- Main Execution ---
def main():
    """Main function to start the stdio server for Claude Desktop."""
    
    # Log environment status
    log_environment_status()
    
    logger.info("")
    logger.info("🤖 Ready for Claude Desktop integration!")
    logger.info("💡 Key Features Available:")
    logger.info("   • [CAPTURE] keyword for screenshots")
    logger.info("   • File system exploration and writing")
    logger.info("   • Web search and weather data")
    logger.info("   • Airtable database management")
    if os.getenv("BRAVE_API_KEY"):
        logger.info("   • Web search enabled ✓")
    if os.getenv("AIRTABLE_PERSONAL_ACCESS_TOKEN"):
        logger.info("   • Airtable integration enabled ✓")
    logger.info("")
    logger.info("🚀 Starting stdio transport...")
    
    try:
        # Start the MCP server with stdio transport
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()