# MCP Server for AI Integration

A comprehensive Model Context Protocol (MCP) server built with FastMCP 2.0 that provides AI agents with access to a powerful suite of tools and services. This modular, extensible server enables seamless integration with various platforms, APIs, and automation workflows.

## 🚀 Overview

The Model Context Protocol (MCP) allows AI agents to interact with external tools and services through a standardized interface. This implementation provides a rich toolkit that enables AI agents to:

- **🔍 Search & Research**: Web search, local business discovery, and content extraction
- **🌤️ Real-time Data**: Weather information and forecasts worldwide
- **🧮 Calculations**: Mathematical operations with error handling
- **🕷️ Web Automation**: Browser control and website content extraction
- **📊 Data Management**: Airtable database operations and structured data handling
- **📝 Document Creation**: Google Workspace integration (Sheets, Docs, Slides)
- **🔗 Platform Integration**: Ready for n8n, Claude Desktop, and custom applications

## ✨ Key Features

### 🌐 Web & Search Tools
- **Brave Search Integration**: Web search, news, videos, and local business discovery
- **Real-time Weather**: Current conditions and forecasts using Open-Meteo API
- **Web Crawling**: Extract content from websites using Crawl4AI with structured data support
- **Browser Automation**: Full browser control with Playwright for interactive web tasks

### 📊 Data & Productivity
- **Airtable Management**: Create bases, manage tables, search records with template library
- **Google Sheets**: Create spreadsheets, manipulate data, collaborative editing
- **Google Docs**: Document creation, content editing, and collaborative writing
- **Google Slides**: Presentation creation, slide management, template-based workflows
- **Calculator**: Reliable arithmetic operations with comprehensive error handling

### 🏗️ Architecture Highlights
- **FastMCP 2.0**: Built on the latest MCP framework for optimal performance
- **Modular Design**: Tools in separate modules for easy management and extension
- **Session Context**: Smart memory for recent operations and created documents
- **SSE Support**: Server-Sent Events for real-time communication
- **Flexible Authentication**: OAuth2, Bearer tokens, and API key support
- **Error Resilience**: Comprehensive error handling with graceful degradation

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd mcp-server

# Install with uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt

# Or with pip
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the project root:

```env
# Server Configuration
MCP_SERVER_NAME=my-mcp-server
MCP_HOST=0.0.0.0
MCP_PORT=8000

# Required API Keys
BRAVE_API_KEY=your_brave_search_api_key
AIRTABLE_PERSONAL_ACCESS_TOKEN=your_airtable_token

# Optional: Google Workspace (for Sheets, Docs, Slides)
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json
```

### 3. Optional Dependencies

For enhanced functionality, install additional tools:

```bash
# Web crawling and browser automation
pip install crawl4ai playwright
playwright install

# Google Workspace integration
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 4. Launch the Server

```bash
python run.py
```

Your server will be available at:
- **Base URL**: `http://localhost:8000`
- **SSE Endpoint**: `http://localhost:8000/sse`
- **MCP Protocol**: Ready for AI agent connections

## 🛠️ Tool Categories

| Category | Tools | API Required | Status |
|----------|-------|--------------|--------|
| **Search & Web** | 2 web search tools | Brave API | ✅ Core |
| **Weather** | Global weather data | None (Open-Meteo) | ✅ Core |
| **Calculator** | Arithmetic operations | None | ✅ Core |
| **Web Automation** | 3 crawling + 10 browser tools | None (local) | ⚡ Optional |
| **Airtable** | 15+ database tools | Airtable Token | ✅ Core |
| **Google Sheets** | 8 spreadsheet tools | Google OAuth2 | ⚡ Optional |
| **Google Docs** | 5 document tools | Google OAuth2 | ⚡ Optional |
| **Google Slides** | 10 presentation tools | Google OAuth2 | ⚡ Optional |

### Core Tools (Always Available)
- `brave_web_search`, `brave_local_search` - Web and local business search
- `get_weather` - Current weather and forecasts for any location
- `calculator` - Basic arithmetic with error handling
- `create_airtable_base`, `list_records`, etc. - Database management

### Smart Context Features
- **Session Memory**: Tracks recently created documents and spreadsheets
- **Title Search**: Find documents by name without IDs
- **Auto-append**: Add to most recent spreadsheet/document
- **Template Library**: Pre-built Airtable templates (CRM, project management, etc.)

## 🔌 Integration Examples

### n8n Workflow Integration

1. Add **MCP Client Tool** node to your workflow
2. Configure the SSE endpoint: `http://your-server:8000/sse`
3. Select which tools to expose to your AI agent
4. Configure authentication if required

```json
{
  "endpoint": "http://localhost:8000/sse",
  "authentication": "bearer",
  "tools": ["brave_web_search", "get_weather", "create_google_sheet"]
}
```

### Claude Desktop Integration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "enhanced-mcp-server": {
      "command": "python",
      "args": ["/absolute/path/to/run.py"],
      "env": {
        "BRAVE_API_KEY": "your_brave_api_key",
        "AIRTABLE_PERSONAL_ACCESS_TOKEN": "your_airtable_token"
      }
    }
  }
}
```

### Custom Application

Connect via HTTP API with JSON responses:

```python
import httpx

async def call_mcp_tool():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/messages",
            json={
                "tool": "get_weather",
                "parameters": {"location": "Tokyo, Japan"}
            }
        )
        return response.json()
```

## 📊 Advanced Features

### Airtable Template System
Create production-ready bases instantly:
- **CRM**: Customer relationship management with deals pipeline
- **Project Management**: Tasks, projects, and team coordination  
- **Inventory**: Product tracking with stock levels and suppliers
- **Event Planning**: Event management with task coordination
- **Content Calendar**: Content planning and publishing workflow

### Google Workspace Integration
Seamless document creation and management:
- **Context-Aware**: Automatically tracks recent creations
- **Smart Operations**: "Append to last sheet", "Edit recent doc"
- **Collaborative**: Built-in sharing and permission management
- **Template Support**: Copy from existing documents and presentations

### Web Automation Capabilities
Powerful browser control for complex tasks:
- **Multi-Browser**: Chrome, Firefox, Safari support
- **Session Management**: Multiple concurrent browser contexts
- **Interaction Suite**: Click, fill forms, wait for elements, execute JavaScript
- **Content Extraction**: Screenshots, accessibility trees, structured data

## 🔧 Development & Extension

### Adding New Tools

1. Create a new tool file in `tools/`:

```python
# tools/my_tool.py
from typing import Dict, Any

async def my_function(param: str) -> Dict[str, Any]:
    """Tool description for AI agents."""
    try:
        result = f"Processed: {param}"
        return {"result": result, "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "error"}

def register(mcp_instance):
    mcp_instance.tool()(my_function)
```

2. Import and register in `run.py`:

```python
from tools import my_tool
my_tool.register(mcp)
```

### Development Setup

```bash
# Install development dependencies
uv pip install pytest python-dotenv

# Run tests
pytest tests/

# Test specific tools
python -m tests.test_mcp_crawler
```

## 🔐 API Setup & Costs

### Required for Full Functionality

**Brave Search API** ([Get API Key](https://api.search.brave.com/))
- Free tier: 2,000 queries/month
- Paid plans: Higher limits available
- Usage: Web search and local business discovery

**Airtable Personal Access Token** ([Generate Token](https://airtable.com/account))
- Free tier: Generous usage limits
- Usage: Database creation and management

**Google Workspace APIs** ([Setup Guide](https://console.cloud.google.com/))
- Free tier with setup required
- OAuth2 credentials needed
- Usage: Sheets, Docs, and Slides integration

### Free Services
- **Weather**: Open-Meteo API (unlimited)
- **Calculator**: Built-in functionality
- **Web Crawling**: Local browser automation
- **Browser Control**: Local Playwright execution

## 📖 Documentation

- **[Complete Tool Reference](docs/tools.md)** - Detailed documentation for all tools
- **[Development Guide](docs/server_and_tool_development.md)** - Adding new tools and extending functionality
- **[System Prompts](docs/prompt_guide.md)** - LLM integration guidance
- **[MCP Protocol Guide](docs/mcp.md)** - Understanding the Model Context Protocol

### Individual Tool Documentation
- [Web Search Tools](docs/tools/web-search-tools.md)
- [Weather Tools](docs/tools/weather-tools.md) 
- [Calculator Tools](docs/tools/calculator-tools.md)
- [Web Crawling Tools](docs/tools/web-crawling-tools.md)
- [Browser Automation Tools](docs/tools/browser-automation-tools.md)
- [Airtable Tools](docs/tools/airtable-tools.md)
- [Google Sheets Tools](docs/tools/google-sheets-tools.md)
- [Google Docs Tools](docs/tools/google-docs-tools.md)
- [Google Slides Tools](docs/tools/google-slides-tools.md)

## 🚀 Production Deployment

### Docker Deployment (Example)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Install optional dependencies
RUN pip install crawl4ai playwright && playwright install --with-deps

EXPOSE 8000
CMD ["python", "run.py"]
```

### Environment Variables

```env
# Production settings
MCP_HOST=0.0.0.0
MCP_PORT=8000
MCP_SERVER_NAME=production-mcp-server

# Secure token management
BRAVE_API_KEY=${BRAVE_API_KEY}
AIRTABLE_PERSONAL_ACCESS_TOKEN=${AIRTABLE_TOKEN}
```

## 🛡️ Security & Best Practices

### API Key Security
- Store keys in environment variables, never in code
- Use different keys for development and production environments
- Monitor API usage and set up alerts for unusual activity
- Rotate keys regularly and update access

### Tool Access Control
- Use tool selection in n8n to limit available functions
- Monitor tool usage through logging
- Implement rate limiting for production deployments
- Review and audit tool access regularly

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-tool`
3. Add tests for new functionality
4. Ensure all tests pass: `pytest`
5. Submit a pull request

### Areas for Contribution
- New tool integrations (Slack, GitHub, etc.)
- Enhanced error handling and logging
- Performance optimizations
- Documentation improvements
- Testing and quality assurance

## 📞 Support & Community

- **Issues**: Report bugs and request features via [GitHub Issues](https://github.com/your-repo/issues)
- **Documentation**: Complete tool docs in the `docs/` directory
- **Examples**: Usage examples and workflows in `examples/` directory

## 🏆 Built With

- **[FastMCP 2.0](https://gofastmcp.com)** - The fast, Pythonic way to build MCP servers
- **[Brave Search](https://api.search.brave.com)** - Privacy-focused web search
- **[Open-Meteo](https://open-meteo.com)** - Free weather API
- **[Crawl4AI](https://github.com/unclecode/crawl4ai)** - AI-friendly web crawling
- **[Playwright](https://playwright.dev)** - Browser automation
- **[Google APIs](https://developers.google.com)** - Workspace integration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Ready to supercharge your AI workflows?** Get started with the installation guide above and explore the comprehensive tool documentation to unlock the full potential of your AI agents.