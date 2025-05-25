# MCP Server Tools Documentation

Comprehensive documentation for all available MCP server tools organized by category.

## Available Tool Categories

| Category | Description | Functions | Status | Dependencies |
|----------|-------------|-----------|--------|-------------|
| [Web Search](web-search-tools.md) | Brave Search API integration | 2 | ✅ Available | API Key Required |
| [Weather](weather-tools.md) | Global weather data and forecasts | 1 | ✅ Available | None |
| [Calculator](calculator-tools.md) | Arithmetic operations | 1 | ✅ Available | None |
| [Web Crawling](web-crawling-tools.md) | Website content extraction | 3 | ⚠️ Optional | Crawl4AI + Playwright |
| [Browser Automation](browser-automation-tools.md) | Interactive browser control | 10 | ⚠️ Optional | Playwright |
| [Airtable](airtable-tools.md) | Database management | 15+ | ✅ Available | API Token Required |
| [Google Sheets](google-sheets-tools.md) | Spreadsheet operations | 8 | ⚠️ Optional | Google API + OAuth2 |
| [Google Docs](google-docs-tools.md) | Document creation/editing | 5 | ⚠️ Optional | Google API + OAuth2 |
| [Google Slides](google-slides-tools.md) | Presentation management | 10 | ⚠️ Optional | Google API + OAuth2 |

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
- **Core Tools**: Always available (web search, weather, calculator, Airtable)
- **Optional Tools**: Available when dependencies are installed
- **Configuration**: Set environment variables for API-dependent tools

## Tool Categories Overview

### Core Utilities
- **Web Search**: Find information across the internet
- **Weather**: Get current conditions and forecasts
- **Calculator**: Perform mathematical operations

### Data Management
- **Airtable**: Create and manage structured databases
- **Google Sheets**: Work with spreadsheets and data analysis

### Content Creation
- **Google Docs**: Create and edit documents
- **Google Slides**: Build and manage presentations

### Web Automation
- **Web Crawling**: Extract content from websites
- **Browser Automation**: Interactive web page control

## Common Workflows

### Research and Documentation
1. **Web Search** → Find relevant information
2. **Web Crawling** → Extract detailed content
3. **Google Docs** → Create research documents
4. **Airtable** → Organize findings

### Data Collection and Analysis
1. **Web Search** → Gather data sources
2. **Weather** → Collect environmental data
3. **Calculator** → Perform calculations
4. **Google Sheets** → Analyze and visualize

### Presentation Creation
1. **Web Search** → Research content
2. **Airtable** → Organize information
3. **Google Slides** → Create presentations
4. **Browser Automation** → Capture screenshots

### Automation and Monitoring
1. **Browser Automation** → Navigate websites
2. **Web Crawling** → Extract data
3. **Airtable** → Store results
4. **Weather** → Environmental monitoring

## API Requirements and Costs

### Required API Keys
- **Brave Search**: Paid service with free tier (2,000 queries/month)
- **Airtable**: Free tier available with usage limits
- **Google Workspace**: Free with setup required

### Free Services
- **Weather**: Open-Meteo API (no limits)
- **Calculator**: Built-in functionality
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
- **Fast**: Calculator, Weather, Web Search
- **Medium**: Airtable, Google Workspace APIs
- **Slower**: Web Crawling, Browser Automation

### Optimization Strategies
- **Caching**: Implement for repeated operations
- **Batch Operations**: Group related requests
- **Parallel Processing**: Use concurrent tools when possible
- **Resource Management**: Close browser sessions promptly

## Security Best Practices

### API Key Management
- Store keys in environment variables
- Use different keys for different environments
- Rotate keys regularly
- Monitor usage and quotas

### Access Control
- Configure tool-specific permissions
- Use principle of least privilege
- Monitor tool usage and access logs
- Implement proper authentication

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