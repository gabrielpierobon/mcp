# MCP Server Tools Documentation

Comprehensive documentation for all available MCP server tools organized by category.

## Available Tool Categories

| Category | Description | Functions | Status | Dependencies |
|----------|-------------|-----------|--------|-------------|
| [Screen Capture](tools/screen-capture-tools.md) | **🆕 NEW** Revolutionary visual context and desktop analysis | 5 | ✅ Available | mss, pillow |
| [RAG Knowledge Base](tools/rag_knowledge_base_README.md) | **🆕 NEW** Semantic search and retrieval system | 7 | ✅ Production Ready | chromadb, sentence-transformers, langchain-text-splitters |
| [Web Search](tools/web-search-tools.md) | Brave Search API integration | 2 | ✅ Available | API Key Required |
| [Weather](tools/weather-tools.md) | Global weather data and forecasts | 1 | ✅ Available | None |
| [Calculator](tools/calculator-tools.md) | Arithmetic operations | 1 | ✅ Available | None |
| [File System](tools/file-system-tool.md) | Local file reading and exploration | 5 | ✅ Available | None |
| [File Writing](tools/file-writing-tools.md) | Secure file creation and project setup | 5 | ✅ Available | None |
| [Web Crawling](tools/web-crawling-tools.md) | Website content extraction | 3 | ⚠️ Optional | Crawl4AI + Playwright |
| [Browser Automation](tools/browser-automation-tools.md) | Interactive browser control | 10 | ⚠️ Optional | Playwright |
| [Airtable](tools/airtable-tools.md) | Database management | 15+ | ✅ Available | API Token Required |
| [Google Sheets](tools/google-sheets-tools.md) | Spreadsheet operations | 8 | ⚠️ Optional | Google API + OAuth2 |
| [Google Docs](tools/google-docs-tools.md) | Document creation/editing | 5 | ⚠️ Optional | Google API + OAuth2 |
| [Google Slides](tools/google-slides-tools.md) | Presentation management | 10 | ⚠️ Optional | Google API + OAuth2 |

## Quick Start

### 1. Installation

**Core Tools:**
```bash
pip install fastmcp httpx python-dotenv

# NEW: Screen Capture Tool
pip install mss pillow

# NEW: RAG Knowledge Base
pip install chromadb sentence-transformers langchain-text-splitters
```

**Optional Dependencies:**
```bash
# Web crawling and browser automation
pip install crawl4ai playwright
playwright install

# Google Workspace tools
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Environment Variables

Create a `.env` file with required API keys:

```env
# Required for web search
BRAVE_API_KEY=your_brave_search_api_key

# Required for Airtable
AIRTABLE_PERSONAL_ACCESS_TOKEN=your_airtable_token

# Optional for Google Workspace tools
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json
```

### 3. Tool Selection

Tools are automatically registered based on available dependencies:
- **Core Tools**: Always available (screen capture, RAG knowledge base, web search, weather, calculator, file system, file writing, Airtable)
- **Optional Tools**: Available when dependencies are installed
- **Configuration**: Set environment variables for API-dependent tools

## Tool Categories Overview

### **🆕 Revolutionary AI Capabilities**
- **Screen Capture**: 🚀 **NEW** - Give AI agents visual awareness of your desktop with [CAPTURE] keyword integration
- **RAG Knowledge Base**: 🧠 **NEW** - Semantic search and retrieval system for intelligent context-aware responses

### Core Utilities
- **Web Search**: Find information across the internet
- **Weather**: Get current conditions and forecasts
- **Calculator**: Perform mathematical operations
- **File System**: Read and explore local files and directories
- **File Writing**: Create files and project structures in secure sandbox

### Data Management
- **Airtable**: Create and manage structured databases
- **Google Sheets**: Work with spreadsheets and data analysis

### Content Creation
- **Google Docs**: Create and edit documents
- **Google Slides**: Build and manage presentations

### Web Automation
- **Web Crawling**: Extract content from websites
- **Browser Automation**: Interactive web page control

## 🆕 New Screen Capture Capabilities

### Revolutionary Visual Context
- **Desktop Awareness**: AI agents can now "see" your screen in real-time
- **[CAPTURE] Keyword**: Natural language integration with simple keyword
- **Clipboard Integration**: Screenshots copied directly to clipboard for instant sharing
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Multi-Monitor Support**: Capture specific monitors or regions

### Available Functions
- **`quick_capture()`**: Main screenshot function with [CAPTURE] keyword support
- **`detect_and_capture()`**: Automatic detection of [CAPTURE] in messages
- **`capture_region_to_clipboard()`**: Specific screen areas
- **`capture_monitor_to_clipboard()`**: Multi-monitor support

### Usage Examples
- **`[CAPTURE] I need help with this dialog`** - Screenshot + context
- **`[CAPTURE] What should I click next?`** - Workflow guidance
- **`[CAPTURE] I'm getting an error`** - Error troubleshooting
- **`[CAPTURE]`** - General screen capture

## 🧠 NEW: RAG Knowledge Base System

### Intelligent Semantic Search
- **Context-Aware Responses**: Build agents that can access and utilize your organization's knowledge
- **Multi-Collection Support**: Organize knowledge by domain, topic, or classification
- **Source Attribution**: Full provenance tracking for all retrieved information
- **Production Ready**: Persistent ChromaDB storage with BGE-M3 embeddings

### Available Functions
- **`setup_knowledge_base()`**: Initialize the RAG system
- **`get_kb_health()`**: Monitor system health and performance  
- **`add_url_to_kb()`**: Scrape and add webpage content
- **`add_text_to_kb()`**: Add plain text content directly
- **`search_kb()`**: Semantic search with similarity ranking
- **`list_kb_sources()`**: Browse all sources and metadata
- **`get_kb_stats()`**: Comprehensive knowledge base analytics

### Key Features
- **BGE-M3 Embeddings**: State-of-the-art multilingual embeddings (8192 context length)
- **Smart Chunking**: Semantic text splitting with configurable overlap
- **Metadata Tracking**: Rich source information, timestamps, and custom fields
- **Multi-Modal Ready**: Architecture supports future image/audio content
- **Integration Friendly**: Works seamlessly with existing web crawling tools

### Usage Examples

#### Building Knowledge Bases
```python
# Add company documentation
await add_url_to_kb("https://company.com/docs", "company_knowledge")

# Add meeting notes
await add_text_to_kb(meeting_notes, "Q4_planning_meeting", "internal_docs")
```

#### Intelligent Search & Retrieval
```python
# Find relevant context for user queries
results = await search_kb("project deployment timeline", "company_knowledge")
context = [r["content"] for r in results["results"] if r["similarity_score"] > 0.7]
```

#### Multi-Collection Organization
```python
# Organize by domain
await add_url_to_kb(url, "customer_support")    # Support documentation
await add_url_to_kb(url, "technical_specs")     # Product specifications  
await add_url_to_kb(url, "company_policies")    # Internal policies
```

## 🆕 Enhanced File Writing Capabilities

### Secure Sandbox Environment
- **Playground Directory**: `C:\Users\usuario\agent_playground`
- **Complete Isolation**: Cannot write outside designated directory
- **Safe Operations**: Path validation prevents security issues

### Available Functions
- **`write_file`**: Create or overwrite individual files
- **`create_directory`**: Create directory structures
- **`write_multiple_files`**: Batch file creation for efficiency
- **`get_playground_info`**: Sandbox directory information
- **`create_project_structure`**: Complete project templates

### Project Templates
- **Web Projects**: HTML, CSS, JavaScript with proper structure
- **Python Projects**: Package structure with tests and documentation  
- **React Projects**: Complete React setup with components
- **General Projects**: Basic documentation and script structure

## Common Workflows

### **🧠 Intelligent Knowledge-Powered Assistance**
1. **RAG Knowledge Base** → Build semantic knowledge from documentation
2. **Web Search** → Find additional relevant information
3. **RAG Search** → Retrieve contextually relevant information
4. **Screen Capture** → Document current state for context
5. **File Writing** → Generate informed responses and documentation

### **🆕 Visual Desktop Assistance**
1. **Screen Capture** → See what's currently displayed
2. **Context Analysis** → AI understands your desktop environment  
3. **Specific Guidance** → Get targeted help with UI elements
4. **Error Resolution** → Visual troubleshooting of problems

### Smart Research and Documentation
1. **Web Search** → Find relevant information sources
2. **RAG Knowledge Base** → Add sources to semantic knowledge base
3. **Web Crawling** → Extract detailed content from identified sources
4. **RAG Search** → Query knowledge base for specific insights
5. **Screen Capture** → Document current research state
6. **File Writing** → Create organized, context-aware documentation
7. **Airtable** → Organize findings with structured metadata

### Intelligent Development Assistance
1. **RAG Knowledge Base** → Build knowledge base from documentation and best practices
2. **Screen Capture** → Document current development environment
3. **RAG Search** → Find relevant code patterns and solutions
4. **File System** → Read existing codebase for context
5. **File Writing** → Generate informed code with project templates
6. **Google Docs** → Create intelligent project documentation

### Context-Aware Customer Support
1. **RAG Knowledge Base** → Build comprehensive support knowledge base
2. **Screen Capture** → See customer's actual problem
3. **RAG Search** → Find relevant solutions and documentation
4. **Web Search** → Research additional solutions if needed
5. **File Writing** → Create personalized support documentation
6. **Airtable** → Track support cases with full context

### **🆕 Desktop Workflow Assistance**
1. **Screen Capture** → See current application state
2. **Visual Analysis** → AI understands UI elements and context
3. **RAG Search** → Find relevant workflow documentation
4. **File System** → Read configuration or project files
5. **Web Search** → Research solutions for detected issues
6. **File Writing** → Create documentation or configuration files
7. **Browser Automation** → Automate repetitive tasks

### Smart Content Creation Pipeline
1. **RAG Knowledge Base** → Build knowledge base from research sources
2. **Web Search** → Find additional content sources
3. **RAG Search** → Extract relevant information and insights
4. **Screen Capture** → Document reference materials and current work
5. **File Writing** → Create informed content with proper context
6. **Google Slides** → Build presentations with intelligent content
7. **Airtable** → Organize content with metadata and sources

### Intelligent Data Collection and Analysis
1. **Web Search** → Identify data sources
2. **RAG Knowledge Base** → Build knowledge base from data documentation
3. **Screen Capture** → Document data visualization dashboards
4. **RAG Search** → Find relevant analysis patterns and methodologies
5. **Weather** → Collect environmental data
6. **File System** → Read local data files
7. **Calculator** → Perform calculations
8. **File Writing** → Save processed results with intelligent insights
9. **Google Sheets** → Analyze and visualize with context-aware annotations

## API Requirements and Costs

### Required API Keys
- **Brave Search**: Paid service with free tier (2,000 queries/month)
- **Airtable**: Free tier available with usage limits
- **Google Workspace**: Free with setup required

### Free Services
- **RAG Knowledge Base**: 🧠 Local vector database with open-source models (no external dependencies)
- **Screen Capture**: 🆕 Local screen capture (no external dependencies)
- **Weather**: Open-Meteo API (no limits)
- **Calculator**: Built-in functionality
- **File System**: Local file access (no external dependencies)
- **File Writing**: Local file creation (no external dependencies)
- **Web Crawling**: Uses local browser automation
- **Browser Automation**: Uses local browser engines

### RAG Knowledge Base Costs
- **Storage**: ~2KB per text chunk (embeddings + metadata)
- **Processing**: One-time embedding generation (local BGE-M3 model)
- **Search**: Instant local similarity search (no API costs)
- **Scalability**: Handles 10K+ chunks efficiently on standard hardware

## Integration Patterns

### n8n Integration
Use the MCP Client Tool node with:
- **SSE Endpoint**: `http://your-server:8000/sse`
- **Tool Selection**: Choose specific tools for workflows
- **Authentication**: Configure API keys as needed

### Claude Desktop Integration
Add to configuration file:
```json
{
  "mcpServers": {
    "my-tools": {
      "command": "python",
      "args": ["/path/to/run.py"],
      "env": {
        "BRAVE_API_KEY": "your_key"
      }
    }
  }
}
```

### Custom Applications
Connect via:
- **HTTP API**: RESTful interface with JSON responses
- **Server-Sent Events**: Real-time communication
- **Direct Integration**: Import as Python modules

## Error Handling

All tools provide consistent error reporting:
- **Status Fields**: "success" or "error" indicators
- **Error Messages**: Detailed failure descriptions
- **Graceful Degradation**: Tools fail safely without breaking server
- **Retry Logic**: Automatic handling of temporary failures

## Performance Considerations

### Tool Performance
- **Instant**: Screen Capture, Calculator, File System, File Writing, RAG Search (after initial setup)
- **Fast**: Weather, Web Search  
- **Medium**: Airtable, Google Workspace APIs, RAG Content Ingestion
- **Slower**: Web Crawling, Browser Automation, Initial RAG Setup (model download)

### RAG Knowledge Base Performance
- **Initial Setup**: ~2-5 minutes (BGE-M3 model download: 2.27GB)
- **Content Ingestion**: ~2-5 chunks per second (embedding generation)
- **Search Speed**: ~10-50ms for collections under 10K chunks
- **Memory Usage**: ~500MB for BGE-M3 model + ~2KB per chunk

### Optimization Strategies
- **Caching**: Implement for repeated operations
- **Batch Operations**: Group related requests (especially file writing and RAG ingestion)
- **Parallel Processing**: Use concurrent tools when possible
- **Resource Management**: Close browser sessions promptly
- **File Size Limits**: Control memory usage with file reading limits
- **RAG Collections**: Organize content by domain for faster, more relevant search

## Security Best Practices

### API Key Management
- Store keys in environment variables
- Use different keys for different environments
- Rotate keys regularly
- Monitor usage and quotas

### File System Security
- **Read-only access** prevents system modification (file system tools)
- **Sandbox restrictions** limit file writing to designated directory
- **Screen capture** uses local clipboard only, no file storage
- **RAG Knowledge Base** uses local storage only, no external API calls
- File size limits prevent memory exhaustion
- Path validation prevents directory traversal
- Permission respect maintains system security

### Access Control
- Configure tool-specific permissions
- Use principle of least privilege
- Monitor tool usage and access logs
- Implement proper authentication

## 🆕 Enhanced Security Models

### Screen Capture Security
- **Local Processing**: All screenshots processed locally, no external APIs
- **Clipboard Only**: Images copied to clipboard, no file storage
- **Permission Based**: Requires system screen capture permissions
- **Memory Efficient**: Images processed in RAM, not saved to disk

### RAG Knowledge Base Security
- **Local Processing**: All embedding generation and search performed locally
- **No External APIs**: BGE-M3 model runs entirely on local hardware
- **Persistent Storage**: ChromaDB stores data locally in designated directory
- **Data Privacy**: No content sent to external services
- **Access Control**: File system permissions control database access

### File Writing Security Model
- **Sandbox Enforcement**: All file operations limited to `C:\Users\usuario\agent_playground`
- **Path Validation**: Prevents directory traversal attacks (`../`)
- **Automatic Creation**: Creates playground directory if it doesn't exist
- **Safe Resolution**: Handles both relative and absolute paths safely

### Supported File Operations
- **File Creation**: Write new files with any text content
- **Directory Creation**: Create nested directory structures
- **Batch Operations**: Write multiple files efficiently
- **Project Templates**: Generate complete project structures

### Content Types
- **Source Code**: Python, JavaScript, HTML, CSS, Java, etc.
- **Configuration**: JSON, YAML, INI, ENV files
- **Documentation**: Markdown, text files, README files
- **Data Files**: CSV, XML, SQL files
- **Scripts**: Shell, batch, PowerShell scripts

## Support and Resources

### Individual Tool Help
- See specific tool documentation for detailed information
- Check error messages for troubleshooting guidance
- Review API documentation for external services

### Development Resources
- **Development Guide**: `../server_and_tool_development.md`
- **System Prompts**: `../prompt_guide.md`
- **MCP Protocol**: `../mcp.md`

### External Documentation
- **FastMCP**: [gofastmcp.com](https://gofastmcp.com)
- **Brave Search**: [api.search.brave.com](https://api.search.brave.com)
- **Open-Meteo**: [open-meteo.com](https://open-meteo.com)
- **Airtable API**: [airtable.com/developers](https://airtable.com/developers)
- **Google APIs**: [developers.google.com](https://developers.google.com)
- **ChromaDB**: [docs.trychroma.com](https://docs.trychroma.com)
- **BGE-M3**: [huggingface.co/BAAI/bge-m3](https://huggingface.co/BAAI/bge-m3)

### Community Support
- **GitHub Issues**: Report bugs and request features
- **Documentation Updates**: Contribute improvements
- **Tool Suggestions**: Propose new tool integrations

---

*Last updated: June 13, 2025 - Added revolutionary RAG Knowledge Base System with semantic search capabilities and enhanced intelligence for all AI agents*