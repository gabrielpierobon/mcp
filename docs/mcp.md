# Building Your Own MCP Server with Python

## Introduction

The Model Context Protocol (MCP) enables you to build servers that extend Claude's capabilities with custom tools, resources, and prompts. This guide will walk you through creating your own MCP server using Python, from setup to testing to deployment with Claude for Desktop.

## Prerequisites

Before you begin, ensure you have:

- Python 3.10 or higher installed
- Basic knowledge of Python programming
- [uv](https://github.com/astral-sh/uv) package manager (recommended) or pip
- (Optional) [Claude for Desktop](https://claude.ai/download) for testing

## 1. Setting Up Your Environment

First, let's create a dedicated project environment:

```bash
# Create and navigate to your project directory
mkdir my-mcp-server
cd my-mcp-server

# Initialize project with uv
uv init .

# Create a virtual environment
uv venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install the MCP SDK and other dependencies
uv add "mcp[cli]" httpx
```

## 2. Planning Your Server

Before writing code, decide what functionality your server will provide. For this tutorial, we'll create a simple weather server with two tools:
- `get_forecast`: Get weather forecasts for a location
- `get_alerts`: Find active weather alerts for a US state

## 3. Creating the Server File

Create a file named `weather.py` and add the following code:

```python
from typing import Any
import httpx
import asyncio
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather-server")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-mcp-server/1.0 (your-email@example.com)"

# Helper function for API requests
async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Log the error for debugging
            print(f"API request error: {e}")
            return None

# Helper function to format weather alerts
def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'Unknown')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""

# Implement the get_alerts tool
@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.
    
    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    # Validate input
    if not isinstance(state, str) or len(state) != 2:
        return "Please provide a valid two-letter US state code (e.g. CA, NY)"
    
    # Make API request
    url = f"{NWS_API_BASE}/alerts/active/area/{state.upper()}"
    data = await make_nws_request(url)
    
    # Handle API errors
    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."
    
    # Format and return results
    if not data["features"]:
        return f"No active alerts for {state.upper()}."
    
    alerts = [format_alert(feature) for feature in data["features"]]
    return f"Active alerts for {state.upper()}:\n\n" + "\n---\n".join(alerts)

# Implement the get_forecast tool
@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.
    
    Args:
        latitude: Latitude of the location (between -90 and 90)
        longitude: Longitude of the location (between -180 and 180)
    """
    # Validate input
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        return "Please provide valid coordinates: latitude (-90 to 90) and longitude (-180 to 180)"
    
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)
    
    if not points_data or "properties" not in points_data:
        return "Unable to fetch forecast data for this location. Note that the NWS API only supports US locations."
    
    # Get the forecast URL from the points response
    try:
        forecast_url = points_data["properties"]["forecast"]
    except KeyError:
        return "Forecast information not available for this location."
    
    forecast_data = await make_nws_request(forecast_url)
    
    if not forecast_data or "properties" not in forecast_data:
        return "Unable to fetch detailed forecast."
    
    # Format the periods into a readable forecast
    try:
        periods = forecast_data["properties"]["periods"]
        if not periods:
            return "No forecast periods available."
            
        forecasts = []
        for period in periods[:5]:  # Only show next 5 periods for brevity
            forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
            forecasts.append(forecast)
        
        return f"Weather forecast for {latitude}, {longitude}:\n\n" + "\n---\n".join(forecasts)
    except KeyError as e:
        return f"Error processing forecast data: missing expected field {e}"

# Run the server when executed directly
if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
```

## 4. Understanding the Code

Let's break down what this code is doing:

1. **Server Initialization**: We create a FastMCP server named "weather-server".

2. **Helper Functions**:
   - `make_nws_request`: Makes API calls to the National Weather Service with proper headers and error handling
   - `format_alert`: Formats weather alert data into a readable text format

3. **Tool Implementations**:
   - `get_alerts`: Retrieves active weather alerts for a US state
   - `get_forecast`: Gets weather forecast for a location using latitude and longitude

4. **MCP Decorator**: The `@mcp.tool()` decorator automatically:
   - Registers the function as an MCP tool
   - Generates a JSON schema from the type annotations
   - Uses the docstring for tool description and parameter documentation

5. **Server Execution**: The `mcp.run()` call starts the server using stdio transport, which is required for Claude for Desktop integration.

## 5. Testing Your Server Locally

You can test your server using the MCP Inspector, a debugging tool that allows you to interact with your server:

```bash
# Make sure you're in your virtual environment
npx -y @modelcontextprotocol/inspector uv run weather.py
```

The Inspector provides a web-based interface where you can:
- View available tools
- Test tools with different parameters
- See the complete response

## 6. Integrating with Claude for Desktop

To use your server with Claude:

1. Create or edit the Claude for Desktop configuration file:
   - On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - On Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add your server configuration:

```json
{
  "mcpServers": {
    "weather": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/YOUR/PROJECT",
        "run",
        "weather.py"
      ]
    }
  }
}
```

Replace `/ABSOLUTE/PATH/TO/YOUR/PROJECT` with the absolute path to your project directory.

3. Restart Claude for Desktop to load your server.

4. Check if your server is properly connected by clicking the hammer icon in the bottom right of the message input area. You should see your tools listed.

## 7. Enhancing Your Server

Once your basic server is working, consider these enhancements:

### Add Logging Support

```python
@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location."""
    # Use the exchange to send log messages
    mcp.log(level="info", message=f"Fetching forecast for: {latitude}, {longitude}")
    
    # Rest of the implementation
    # ...
```

### Add Resource Support

```python
# Define a resource
@mcp.resource(uri="weather://help", name="Weather API Help")
async def weather_help() -> str:
    """Returns help information about the Weather API."""
    return """
# Weather API Help

This server provides access to the National Weather Service API.

## Available Tools:
- get_forecast: Get a weather forecast for a location by latitude/longitude
- get_alerts: Get active weather alerts for a US state

## Examples:
- Get forecast for New York City: latitude=40.7128, longitude=-74.0060
- Get alerts for California: state=CA
"""
```

### Add a Prompt Template

```python
@mcp.prompt(name="weather_analysis", 
            description="Analyze weather conditions for a location",
            arguments=[
                {"name": "location", "description": "City name", "required": True}
            ])
async def weather_analysis(arguments: dict) -> dict:
    """Generate a weather analysis prompt for a location."""
    location = arguments.get("location", "")
    messages = [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": f"Please analyze the current weather conditions in {location} " +
                        f"and provide a summary of what someone should prepare for if " +
                        f"they're planning to visit there today. Consider the temperature, " +
                        f"precipitation chances, and any active weather alerts."
            }
        }
    ]
    return {"messages": messages}
```

## 8. Error Handling and Best Practices

Proper error handling is essential for a robust MCP server. Consider these best practices:

1. **Input Validation**: Always validate user inputs before processing.

2. **Graceful Error Handling**: Return helpful error messages when things go wrong.

3. **Timeouts**: Set reasonable timeouts for external API calls.

4. **Rate Limiting**: Implement rate limiting to prevent abuse of external APIs.

5. **Security**: Never expose sensitive information or allow arbitrary code execution.

6. **Documentation**: Provide clear documentation in your tool descriptions and comments.

## 9. Advanced Deployment

For production use, consider these options:

### Packaging Your Server

Create a `setup.py` file to make your server installable:

```python
from setuptools import setup, find_packages

setup(
    name="weather-mcp-server",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.0.0",
        "httpx>=0.24.0",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "weather-mcp=weather:main",
        ],
    },
)
```

### HTTP Transport for Remote Use

To expose your server via HTTP instead of stdio:

```python
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
import uvicorn

# Your existing server code...

async def handle_sse(scope, receive, send):
    async with SseServerTransport("/messages").connect_sse(scope, receive, send) as streams:
        await mcp.run_async(streams[0], streams[1])

async def handle_messages(scope, receive, send):
    await SseServerTransport("/messages").handle_post_message(scope, receive, send)

app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/messages", endpoint=handle_messages, methods=["POST"]),
    ]
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

## 10. Troubleshooting Common Issues

### Server Not Showing in Claude

If your server isn't appearing in Claude for Desktop:

1. Check the logs:
   ```bash
   # On macOS
   tail -n 20 -f ~/Library/Logs/Claude/mcp*.log
   # On Windows
   type "%APPDATA%\Claude\logs\mcp*.log"
   ```

2. Verify your `claude_desktop_config.json` syntax.

3. Ensure the paths to your server are absolute, not relative.

4. Make sure your virtual environment has all required dependencies.

### Tool Calls Failing

If tools are failing when called:

1. Test them with the Inspector first to isolate issues.

2. Check for API rate limiting or external service problems.

3. Add more detailed error logging to pinpoint the issue.

## 11. Security Considerations

When developing MCP servers, always keep security in mind:

1. **Input Sanitization**: Never trust user input. Validate and sanitize all parameters before use.

2. **Limited Permissions**: Your server should operate with the principle of least privilege.

3. **API Keys**: Never hardcode API keys. Use environment variables or secure credential storage.

4. **External API Limits**: Be respectful of external API rate limits and terms of service.

5. **Error Handling**: Don't expose sensitive information in error messages.

6. **Command Execution**: If your tools execute system commands, be extremely careful about command injection.

## 12. Extending with Custom Transports

The MCP protocol supports different transport mechanisms. While we've focused on stdio (for Claude for Desktop) and HTTP/SSE, you can create custom transports for specific needs:

```python
from mcp.protocol.transport import McpTransport
from typing import Optional, Callable, Any

class MyCustomTransport(McpTransport):
    """A custom transport implementation."""
    
    def __init__(self):
        self.on_message: Optional[Callable[[Any], None]] = None
        # Initialize your transport
        
    async def connect(self):
        # Establish connection
        pass
        
    async def send_message(self, message: Any):
        # Send message through your transport
        pass
        
    async def receive_message(self) -> Optional[Any]:
        # Receive message from your transport
        pass
        
    async def disconnect(self):
        # Close the connection
        pass
```

## Conclusion

You've now created a functional MCP server in Python that extends Claude's capabilities with custom weather tools. This same approach can be applied to build more complex servers that interact with databases, APIs, or local files.

As you become more comfortable with MCP, you can explore advanced features like tool annotations, structured results, and more sophisticated prompt templates to make your tools even more powerful.

For additional resources and community support, check out:
- [MCP Documentation](https://modelcontextprotocol.io/docs)
- [MCP GitHub Organization](https://github.com/modelcontextprotocol)
- [Python SDK Repository](https://github.com/modelcontextprotocol/python-sdk)

Happy coding!