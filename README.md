# MCP Server for AI Integration

This project implements a comprehensive Model Context Protocol (MCP) server that provides AI agents with access to a wide range of tools and services. Built with FastMCP 2.0, it offers a modular, extensible architecture for seamless integration with various platforms and APIs.

## Overview

The Model Context Protocol (MCP) is a specification that allows AI agents to interact with external tools and services. This implementation provides a rich toolkit that enables AI agents to:

- **Search the Web**: Perform web and local searches using Brave Search API
- **Access Weather Data**: Get current conditions and forecasts for any location
- **Perform Calculations**: Execute arithmetic operations
- **Crawl Websites**: Extract content from web pages in various formats
- **Manage Airtable Data**: Create bases, tables, and query records
- **Create Google Workspace Documents**: Generate and edit Sheets, Docs, and Slides
- **Integration Ready**: Designed to work with n8n and other automation platforms

## Features

### 🌐 Web Search & Data
- **Brave Search Integration**: Web search, news, videos, and local business search
- **Weather Information**: Current conditions and forecasts using Open-Meteo API
- **Web Crawling**: Extract content from websites using Crawl4AI with support for structured data extraction

### 🧮 Utilities
- **Calculator**: Basic arithmetic operations (add, subtract, multiply, divide)
- **Context Memory**: Session-based memory for recent operations and created documents

### 📊 Airtable Integration
- **Base Management**: Create bases from templates or custom configurations
- **Data Operations**: List, search, filter, and count records across tables
- **Template Library**: Pre-built templates for CRM, project management, inventory, and more

### 📝 Google Workspace Tools
- **Google Sheets**: Create spreadsheets, write/read data, append to existing sheets
- **Google Docs**: Create documents, edit content, read existing documents
- **Google Slides**: Create presentations, add slides with content, manage placeholders

### 🏗️ Architecture
- **Modular Design**: Tools organized in separate modules for easy management
- **FastMCP 2.0**: Built on the latest FastMCP framework for optimal performance
- **SSE Support**: Server-Sent Events for real-time communication
- **Authentication**: Support for various authentication methods (Bearer, OAuth2)
- **Tool Selection**: Granular control over which tools are available to AI agents

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd mcp-server

# Install dependencies (using uv recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```env
# Server Configuration
MCP_SERVER_NAME=my-mcp-server
MCP_HOST=0.0.0.0
MCP_PORT=8000

# API Keys (obtain from respective services)
BRAVE_API_KEY=your_brave_search_api_key
AIRTABLE_PERSONAL_ACCESS_TOKEN=your_airtable_token

# Google OAuth (for Workspace tools)
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json
```

### 3. Run the Server

```bash
python run.py
```

The server will start and be available at `http://localhost:8000` with SSE endpoint at `/sse`.

## Tool Categories

### 🔍 Search Tools
- `brave_web_search`: Web search with pagination and filtering
- `brave_local_search`: Local business and service search with fallback

### 🌤️ Weather Tools
- `get_weather`: Current conditions and forecasts for any location worldwide

### 🧮 Calculation Tools
- `calculator`: Basic arithmetic operations with error handling

### 🕷️ Web Crawling Tools
- `crawl_webpage`: Extract content from web pages in markdown, HTML, or text
- `crawl_multiple_webpages`: Batch crawling with concurrency control
- `extract_structured_data`: CSS selector-based data extraction

### 📊 Airtable Tools
- **Base Management**: `list_airtable_bases`, `create_airtable_base`, `get_base_schema`
- **Template Creation**: `create_base_with_template` (CRM, project management, etc.)
- **Data Operations**: `list_records`, `search_records`, `count_records`
- **User-Friendly**: `list_records_by_base_name`, `search_records_by_base_name`

### 📝 Google Workspace Tools
- **Sheets**: `create_google_sheet`, `write_to_sheet`, `append_to_last_sheet`
- **Docs**: `create_google_doc`, `rewrite_last_doc`, `read_google_doc`
- **Slides**: `create_google_slides`, `create_slide_with_content`, `add_slide_to_last_presentation`

## Integration Guides

### n8n Integration

The MCP server works seamlessly with n8n's MCP Client Tool node:

1. **Add MCP Client Tool Node**: In your n8n workflow, add the MCP Client Tool node
2. **Configure Endpoint**: Set SSE endpoint to `http://your-server:8000/sse`
3. **Select Tools**: Choose which tools to expose to your AI agent
4. **Authentication**: Configure authentication if required

### Claude Desktop Integration

For use with Claude Desktop, add to your configuration:

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "python",
      "args": ["/path/to/your/run.py"],
      "env": {
        "BRAVE_API_KEY": "your_key_here"
      }
    }
  }
}
```

## Advanced Features

### Session Context Memory
The server maintains context between operations:
- **Recent Documents**: Automatically tracks created Google Workspace files
- **Smart Defaults**: Use "last created" spreadsheet/document for quick operations
- **Context Queries**: Find documents by title or list recent creations

### Template System
Pre-built Airtable templates for common use cases:
- **Project Management**: Projects and tasks with status tracking
- **CRM**: Contacts, deals, and sales pipeline
- **Inventory**: Product tracking with stock levels
- **Event Planning**: Events and task management
- **Content Calendar**: Content planning and scheduling

### Error Handling
Comprehensive error handling with:
- **Graceful Degradation**: Tools fail safely without breaking the server
- **Detailed Error Messages**: Clear feedback for troubleshooting
- **Status Indicators**: Consistent status reporting across all tools

## Development

### Adding New Tools

1. **Create Tool File**: Add new tool in `tools/` directory
2. **Implement Functions**: Create async functions with proper type hints
3. **Add Registration**: Include `register(mcp_instance)` function
4. **Update Server**: Import and register in `run.py`

Example:
```python
# tools/my_tool.py
async def my_function(param: str) -> Dict[str, Any]:
    """Tool description for AI agents."""
    return {"result": param, "status": "success"}

def register(mcp_instance):
    mcp_instance.tool()(my_function)
```

### Environment Setup for Development

```bash
# Install additional development dependencies
uv pip install pytest python-dotenv

# Run tests
pytest tests/

# Check specific tool functionality
python -m tests.test_mcp_crawler
```

## API Requirements

### Required API Keys

1. **Brave Search**: Get API key from [Brave Search API](https://api.search.brave.com/)
2. **Airtable**: Generate Personal Access Token from [Airtable Account](https://airtable.com/account)
3. **Google Workspace**: Set up OAuth2 credentials via [Google Cloud Console](https://console.cloud.google.com/)

### Optional Dependencies

- **Crawl4AI**: `pip install crawl4ai playwright && playwright install`
- **Google APIs**: `pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client`

## Production Deployment

### Docker Deployment (Coming Soon)
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "run.py"]
```

### Environment Variables for Production
```env
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_SERVER_NAME=production-mcp-server

# Security: Use secure token storage
BRAVE_API_KEY=${BRAVE_API_KEY}
AIRTABLE_PERSONAL_ACCESS_TOKEN=${AIRTABLE_TOKEN}
```

## Documentation

- **Tool Reference**: See `docs/tools.md` for complete tool documentation
- **Development Guide**: See `docs/server_and_tool_development.md`
- **System Prompts**: See `docs/prompt_guide.md` for LLM integration guidance
- **MCP Guide**: See `docs/mcp.md` for MCP protocol details

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Documentation**: Complete tool documentation available in `docs/` directory
- **Examples**: See `examples/` directory for usage examples

## Contributing

Contributions are welcome! Please read the development guide and:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

**Built with FastMCP 2.0** - The fast, Pythonic way to build MCP servers and clients.