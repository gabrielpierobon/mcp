# MCP Server Tools Documentation

Comprehensive documentation for all available MCP server tools organized by category.

## Available Tool Categories

| Category | Description | Functions | Status | Dependencies |
|----------|-------------|-----------|--------|-------------|
| [Web Search](tools/web-search-tools.md) | Brave Search API integration | 2 | ✅ Available | API Key Required |
| [Weather](tools/weather-tools.md) | Global weather data and forecasts | 1 | ✅ Available | None |
| [Calculator](tools/calculator-tools.md) | Arithmetic operations | 1 | ✅ Available | None |
| [File System](tools/file-system-tools.md) | Local file reading and exploration | 5 | ✅ Available | None |
| [File Writing](tools/file-writing-tools.md) | **NEW** Secure file creation and project setup | 5 | ✅ Available | None |
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
- **Core Tools**: Always available (web search, weather, calculator, file system, file writing, Airtable)
- **Optional Tools**: Available when dependencies are installed
- **Configuration**: Set environment variables for API-dependent tools

## Tool Categories Overview

### Core Utilities
- **Web Search**: Find information across the internet
- **Weather**: Get current conditions and forecasts
- **Calculator**: Perform mathematical operations
- **File System**: Read and explore local files and directories
- **File Writing**: 🆕 Create files and project structures in secure sandbox

### Data Management
- **Airtable**: Create and manage structured databases
- **Google Sheets**: Work with spreadsheets and data analysis

### Content Creation
- **Google Docs**: Create and edit documents
- **Google Slides**: Build and manage presentations

### Web Automation
- **Web Crawling**: Extract content from websites
- **Browser Automation**: Interactive web page control

## 🆕 New File Writing Capabilities

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

### Research and Documentation
1. **Web Search** → Find relevant information
2. **Web Crawling** → Extract detailed content
3. **File System** → Read local research files
4. **File Writing** → 🆕 Create organized documentation
5. **Airtable** → Organize findings

### Development Project Creation
1. **Web Search** → Research best practices
2. **File Writing** → 🆕 Create project structure with templates
3. **File Writing** → 🆕 Generate source code files
4. **File System** → Read existing code for reference
5. **Google Docs** → Document the project

### Data Collection and Analysis
1. **Web Search** → Gather data sources
2. **Weather** → Collect environmental data
3. **File System** → Read local data files
4. **Calculator** → Perform calculations
5. **File Writing** → 🆕 Save processed results
6. **Google Sheets** → Analyze and visualize

### Local File Management and Development
1. **File System** → Explore directory structures
2. **File System** → Search for specific files or content
3. **File System** → Read configuration files and documents
4. **File Writing** → 🆕 Create new configurations and scripts
5. **File Writing** → 🆕 Set up complete development environments
6. **Airtable** → Catalog file information

### Presentation Creation
1. **Web Search** → Research content
2. **File System** → Read local reference materials
3. **File Writing** → 🆕 Create supporting documentation
4. **Airtable** → Organize information
5. **Google Slides** → Create presentations
6. **Browser Automation** → Capture screenshots

### Automation and Monitoring
1. **Browser Automation** → Navigate websites
2. **Web Crawling** → Extract data
3. **File System** → Process local files
4. **File Writing** → 🆕 Generate automation scripts
5. **Airtable** → Store results
6. **Weather** → Environmental monitoring

## API Requirements and Costs

### Required API Keys
- **Brave Search**: Paid service with free tier (2,000 queries/month)
- **Airtable**: Free tier available with usage limits
- **Google Workspace**: Free with setup required

### Free Services
- **Weather**: Open-Meteo API (no limits)
- **Calculator**: Built-in functionality
- **File System**: Local file access (no external dependencies)
- **File Writing**: 🆕 Local file creation (no external dependencies)
- **Web Crawling**: Uses local browser automation
- **Browser Automation**: Uses local browser engines

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
- **Fast**: Calculator, Weather, Web Search, File System, File Writing
- **Medium**: Airtable, Google Workspace APIs
- **Slower**: Web Crawling, Browser Automation

### Optimization Strategies
- **Caching**: Implement for repeated operations
- **Batch Operations**: Group related requests (especially file writing)
- **Parallel Processing**: Use concurrent tools when possible
- **Resource Management**: Close browser sessions promptly
- **File Size Limits**: Control memory usage with file reading limits

## Security Best Practices

### API Key Management
- Store keys in environment variables
- Use different keys for different environments
- Rotate keys regularly
- Monitor usage and quotas

### File System Security
- **Read-only access** prevents system modification (file system tools)
- **Sandbox restrictions** limit file writing to designated directory
- File size limits prevent memory exhaustion
- Path validation prevents directory traversal
- Permission respect maintains system security

### Access Control
- Configure tool-specific permissions
- Use principle of least privilege
- Monitor tool usage and access logs
- Implement proper authentication

## 🆕 File Writing Security Model

### Sandbox Enforcement
- **Restricted Directory**: All file operations limited to `C:\Users\usuario\agent_playground`
- **Path Validation**: Prevents directory traversal attacks (`../`)
- **Automatic Creation**: Creates playground directory if it doesn't exist
- **Safe Resolution**: Handles both relative and absolute paths safely

### Supported Operations
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

### Community Support
- **GitHub Issues**: Report bugs and request features
- **Documentation Updates**: Contribute improvements
- **Tool Suggestions**: Propose new tool integrations

---

*Last updated: January 2025*