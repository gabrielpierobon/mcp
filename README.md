# MCP Server for AI Integration

A comprehensive Model Context Protocol (MCP) server built with FastMCP 2.5+ that provides AI agents with access to a powerful suite of tools and services. This modular, extensible server enables seamless integration with various platforms, APIs, and automation workflows.

## 🚀 Overview

The Model Context Protocol (MCP) allows AI agents to interact with external tools and services through a standardized interface. This implementation provides a rich toolkit that enables AI agents to:

- **🔍 Search & Research**: Web search, local business discovery, and content extraction
- **🌤️ Real-time Data**: Weather information and forecasts worldwide
- **🧮 Calculations**: Mathematical operations with error handling
- **📂 File System Access**: Read and explore local files and directories
- **📝 File Creation**: Write files and create project structures in secure sandbox
- **🖥️ Screen Capture**: Revolutionary visual context with [CAPTURE] keyword integration
- **🕷️ Web Automation**: Browser control and website content extraction
- **📊 Data Management**: Airtable database operations and structured data handling
- **📄 Document Creation**: Google Workspace integration (Sheets, Docs, Slides)
- **🔗 Platform Integration**: Optimized for n8n, Claude Desktop, and custom applications

## ✨ Key Features

### 🌐 Web & Search Tools
- **Brave Search Integration**: Web search, news, videos, and local business discovery
- **Real-time Weather**: Current conditions and forecasts using Open-Meteo API
- **Web Crawling**: Extract content from websites using Crawl4AI with structured data support
- **Browser Automation**: Full browser control with Playwright for interactive web tasks

### 📊 Data & Productivity
- **File System Access**: Read local files, explore directories, search content with secure read-only access
- **File Writing**: Create files and project structures in secure sandbox environment
- **Screen Capture**: **🆕 Revolutionary** visual context with [CAPTURE] keyword integration
- **Airtable Management**: Create bases, manage tables, search records with template library
- **Google Sheets**: Create spreadsheets, manipulate data, collaborative editing
- **Google Docs**: Document creation, content editing, and collaborative writing
- **Google Slides**: Presentation creation, slide management, template-based workflows
- **Calculator**: Reliable arithmetic operations with comprehensive error handling

### 🏗️ Architecture Highlights
- **FastMCP 2.5+**: Built on the latest MCP framework for optimal performance
- **Smart Launcher**: Intelligent routing between Claude Desktop and n8n modes
- **Modular Design**: Tools in separate modules for easy management and extension
- **Session Context**: Smart memory for recent operations and created documents
- **Multiple Transports**: SSE for n8n, stdio for Claude Desktop
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
# Screen capture (NEW!)
pip install mss pillow pyautogui

# Web crawling and browser automation
pip install crawl4ai playwright
playwright install

# Google Workspace integration
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 4. Launch the Server

**🆕 New Smart Launcher System:**

```bash
# Smart auto-detection (recommended)
python run.py

# Explicit modes
python run.py --http    # For n8n integration
python run.py --stdio   # For Claude Desktop
python run.py --help    # Show help

# Direct server files
python run_http.py      # Dedicated n8n server
python run_claude.py    # Dedicated Claude Desktop server
```

## 🔧 Server Modes

### 🌐 **For n8n Integration**

```bash
python run_http.py
# OR
python run.py --http
```

**n8n MCP Client Tool Configuration:**
- **SSE Endpoint**: `http://host.docker.internal:8000/sse`
- **Authentication**: None
- **Tools**: All or Selected

**Server Features:**
- ✅ SSE transport optimized for n8n
- ✅ Comprehensive error handling
- ✅ All 68+ tools available
- ✅ Environment validation and status

### 🤖 **For Claude Desktop**

```bash
python run_claude.py
# OR  
python run.py --stdio
```

**Claude Desktop Configuration:**
```json
{
  "mcpServers": {
    "enhanced-mcp-server": {
      "command": "python",
      "args": ["/absolute/path/to/run_claude.py"],
      "env": {
        "BRAVE_API_KEY": "your_brave_api_key",
        "AIRTABLE_PERSONAL_ACCESS_TOKEN": "your_airtable_token"
      }
    }
  }
}
```

**Server Features:**
- ✅ stdio transport for Claude Desktop
- ✅ Organized tool logging by category
- ✅ [CAPTURE] keyword support
- ✅ Session memory for created documents

## 🛠️ Tool Categories

| Category | Tools | API Required | Status |
|----------|-------|--------------|--------|
| **🆕 Screen Capture** | [CAPTURE] visual context | None | ✅ Core |
| **Search & Web** | 2 web search tools | Brave API | ✅ Core |
| **Weather** | Global weather data | None (Open-Meteo) | ✅ Core |
| **Calculator** | Arithmetic operations | None | ✅ Core |
| **File System** | 6 file/directory tools | None | ✅ Core |
| **File Writing** | 5 file creation tools | None | ✅ Core |
| **Web Automation** | 3 crawling + 10 browser tools | None (local) | ⚡ Optional |
| **Airtable** | 15+ database tools | Airtable Token | ✅ Core |
| **Google Sheets** | 8 spreadsheet tools | Google OAuth2 | ⚡ Optional |
| **Google Docs** | 5 document tools | Google OAuth2 | ⚡ Optional |
| **Google Slides** | 10 presentation tools | Google OAuth2 | ⚡ Optional |
| **🆕 RAG Knowledge Base** | Semantic search, ingestion, stats | chromadb, sentence-transformers | ✅ Core |

### Core Tools (Always Available)
- `quick_capture`, `detect_and_capture` - **🆕 Revolutionary** screen capture with [CAPTURE] keyword
- `brave_web_search`, `brave_local_search` - Web and local business search
- `get_weather` - Current weather and forecasts for any location
- `calculator` - Basic arithmetic with error handling
- `get_system_info`, `read_file`, `list_directory`, `find_directory` - File system exploration
- `write_file`, `create_project_structure` - **🆕** Secure file creation in sandbox
- `create_airtable_base`, `list_records`, etc. - Database management

### 🆕 Revolutionary Features

#### **Screen Capture with [CAPTURE] Keyword**
- **Natural Integration**: Use `[CAPTURE]` in any message for instant screenshots
- **Context Aware**: AI understands your screen and provides targeted guidance
- **Cross-Platform**: Works on Windows, macOS, Linux
- **Clipboard Direct**: Screenshots copied directly to clipboard for instant sharing

**Usage Examples:**
```
[CAPTURE] I need help with this dialog
[CAPTURE] What should I click next?
[CAPTURE] I'm getting an error
[CAPTURE]  # General screen capture
```

#### **Secure File Writing Sandbox**
- **Playground Directory**: `C:\Users\usuario\agent_playground`
- **Complete Isolation**: Cannot write outside designated directory
- **Project Templates**: Web, Python, React, and general project structures
- **Safe Operations**: Path validation prevents security issues

#### **Smart Context Features**
- **Session Memory**: Tracks recently created documents and spreadsheets
- **Title Search**: Find documents by name without IDs
- **Auto-append**: Add to most recent spreadsheet/document
- **Template Library**: Pre-built Airtable templates (CRM, project management, etc.)

## 🔌 Integration Examples

### n8n Workflow Integration

1. Add **MCP Client Tool** node to your workflow
2. Configure the SSE endpoint: `http://host.docker.internal:8000/sse`
3. Select which tools to expose to your AI agent
4. Configure authentication if required

```json
{
  "endpoint": "http://host.docker.internal:8000/sse",
  "authentication": "none",
  "tools": ["brave_web_search", "get_weather", "quick_capture", "read_file", "create_google_sheet"]
}
```

### Claude Desktop Integration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "enhanced-mcp-server": {
      "command": "python",
      "args": ["/absolute/path/to/run_claude.py"],
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
                "tool": "list_directory",
                "parameters": {"directory_path": "~"}
            }
        )
        return response.json()
```

## 📊 Advanced Features

### 🆕 Screen Capture Integration
Revolutionary visual context for AI agents:
- **Desktop Awareness**: AI can now "see" your screen in real-time
- **[CAPTURE] Keyword**: Natural language integration with simple keyword
- **Workflow Guidance**: Get help with any desktop application
- **Error Troubleshooting**: Visual debugging of problems
- **Multi-Monitor Support**: Capture specific monitors or regions

### File System Integration
Secure, read-only access to local files:
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Smart Path Handling**: Supports `~` for home directory and environment variables
- **Content Search**: Find files by name patterns or content
- **Token Efficient**: Enhanced limits prevent expensive API calls
- **Permission Aware**: Respects file system permissions

### 🆕 File Writing Capabilities
Secure file creation in sandbox environment:
- **Sandbox Security**: All operations limited to `C:\Users\usuario\agent_playground`
- **Project Templates**: Complete project structures (Web, Python, React, General)
- **Batch Operations**: Write multiple files efficiently
- **Path Validation**: Prevents directory traversal attacks

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

### 🆕 RAG Knowledge Base Tool
A full Retrieval-Augmented Generation (RAG) system for building, managing, and searching a semantic knowledge base. Enables your AI agents to provide accurate, source-backed responses using your own documents, URLs, and structured knowledge.
- **Semantic Search**: Finds relevant information using meaning, not just keywords
- **Content Ingestion**: Add content from URLs or plain text
- **Vector Embeddings**: Uses BGE-M3 model for high-quality embeddings
- **Multi-Collection Support**: Organize knowledge by topic or domain
- **Source Tracking**: Full metadata and provenance for all content
- **Production Ready**: Persistent storage with ChromaDB
- **Dependencies**: `chromadb`, `sentence-transformers`, `langchain-text-splitters`
- **Docs**: [RAG Knowledge Base Tool](docs/tools/rag-kb-tool.md)

**Basic Usage:**
- Add a webpage: `add_url_to_kb(url, collection_name)`
- Add text: `add_text_to_kb(text, source_name, collection_name)`
- Search: `search_kb(query, collection_name, limit)`
- List sources: `list_kb_sources(collection_name)`
- Get stats: `get_kb_stats()`

See the [tool documentation](docs/tools/rag-kb-tool.md) for advanced workflows and integration patterns.

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

2. Import and register in server files:

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

# Test specific modes
python run.py --http   # Test n8n integration
python run.py --stdio  # Test Claude Desktop
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
- **🆕 Screen Capture**: Local screen capture (no external dependencies)
- **🆕 File Writing**: Local file creation (no external dependencies)
- **Weather**: Open-Meteo API (unlimited)
- **Calculator**: Built-in functionality
- **File System**: Local file access (no external dependencies)
- **Web Crawling**: Local browser automation
- **Browser Control**: Local Playwright execution

## 📖 Documentation

- **[Complete Tool Reference](docs/tools.md)** - Detailed documentation for all tools
- **[Development Guide](docs/server_and_tool_development.md)** - Adding new tools and extending functionality
- **[System Prompts](docs/prompt_guide.md)** - LLM integration guidance
- **[MCP Protocol Guide](docs/mcp.md)** - Understanding the Model Context Protocol

### Individual Tool Documentation
- **[🆕 Screen Capture Tools](docs/tools/screen-capture-tools.md)** - Revolutionary visual context
- **[🆕 File Writing Tools](docs/tools/file-writing-tools.md)** - Secure file creation
- [Web Search Tools](docs/tools/web-search-tools.md)
- [Weather Tools](docs/tools/weather-tools.md) 
- [Calculator Tools](docs/tools/calculator-tools.md)
- [File System Tools](docs/tools/file-system-tools.md)
- [Web Crawling Tools](docs/tools/web-crawling-tools.md)
- [Browser Automation Tools](docs/tools/browser-automation-tools.md)
- [Airtable Tools](docs/tools/airtable-tools.md)
- [Google Sheets Tools](docs/tools/google-sheets-tools.md)
- [Google Docs Tools](docs/tools/google-docs-tools.md)
- [Google Slides Tools](docs/tools/google-slides-tools.md)
- [RAG Knowledge Base Tool](docs/tools/rag-kb-tool.md)

## 🚀 Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Install optional dependencies
RUN pip install crawl4ai playwright mss pillow && playwright install --with-deps

EXPOSE 8000
CMD ["python", "run_http.py"]
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

### Service Configuration

**For n8n Integration:**
```bash
# Production n8n server
python run_http.py
```

**For Claude Desktop:**
```bash
# Claude Desktop integration
python run_claude.py
```

**For Auto-Detection:**
```bash
# Smart launcher (adapts to environment)
python run.py
```

## 🛡️ Security & Best Practices

### API Key Security
- Store keys in environment variables, never in code
- Use different keys for development and production environments
- Monitor API usage and set up alerts for unusual activity
- Rotate keys regularly and update access

### File System Security
- **🆕 File Writing**: Sandbox restrictions limit operations to designated directory
- **Read-only access**: File system tools prevent accidental system modification
- **🆕 Screen capture**: Uses local clipboard only, no file storage
- File size limits prevent memory exhaustion
- Path validation prevents directory traversal attacks
- Permission respect maintains existing security boundaries

### Tool Access Control
- Use tool selection in n8n to limit available functions
- Monitor tool usage through logging
- Implement rate limiting for production deployments
- Review and audit tool access regularly

## 🎯 New Workflows & Use Cases

### **🆕 Visual Desktop Assistance**
1. **Screen Capture** → See what's currently displayed
2. **Context Analysis** → AI understands your desktop environment  
3. **Specific Guidance** → Get targeted help with UI elements
4. **Error Resolution** → Visual troubleshooting of problems

### **🆕 Development Project Creation**
1. **Screen Capture** → Document current development setup
2. **Web Search** → Research best practices
3. **File Writing** → Create project structure with templates
4. **File Writing** → Generate source code files
5. **File System** → Read existing code for reference
6. **Google Docs** → Document the project

### Research and Documentation
1. **Web Search** → Find relevant information
2. **Web Crawling** → Extract detailed content
3. **File System** → Read local research files
4. **🆕 Screen Capture** → Document current desktop state
5. **🆕 File Writing** → Create organized documentation
6. **Airtable** → Organize findings

### Data Collection and Analysis
1. **Web Search** → Gather data sources
2. **🆕 Screen Capture** → Document data visualization dashboards
3. **Weather** → Collect environmental data
4. **File System** → Read local data files
5. **Calculator** → Perform calculations
6. **🆕 File Writing** → Save processed results
7. **Google Sheets** → Analyze and visualize

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

## 🏆 Built With

- **[FastMCP 2.5+](https://gofastmcp.com)** - The fast, Pythonic way to build MCP servers
- **[Brave Search](https://api.search.brave.com)** - Privacy-focused web search
- **[Open-Meteo](https://open-meteo.com)** - Free weather API
- **[Crawl4AI](https://github.com/unclecode/crawl4ai)** - AI-friendly web crawling
- **[Playwright](https://playwright.dev)** - Browser automation
- **[Google APIs](https://developers.google.com)** - Workspace integration
- **🆕 [MSS](https://python-mss.readthedocs.io)** - Fast cross-platform screenshots

## 📝 Recent Updates

### **🆕 Version 2.5+ Features**
- **Revolutionary Screen Capture**: [CAPTURE] keyword integration for visual context
- **Secure File Writing**: Sandbox environment for safe file creation
- **Smart Launcher**: Intelligent routing between Claude Desktop and n8n modes
- **Enhanced File System**: Token-efficient operations with improved limits
- **Project Templates**: Complete project structures for Web, Python, React
- **Improved Documentation**: Comprehensive guides for all features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Ready to supercharge your AI workflows?** Get started with the installation guide above and explore the comprehensive tool documentation to unlock the full potential of your AI agents with revolutionary visual context and secure file operations!