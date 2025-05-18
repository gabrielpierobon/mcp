# MCP Server and Tool Development Guide

This guide provides an overview of the n8n MCP server architecture and explains how to develop and integrate new tools.

## Server Architecture Overview

The MCP server is built using Python and leverages several key components to provide its functionality:

1.  **Main Application Script (e.g., `mcp_n8n_server.py` or your primary server script):**
    *   This is the entry point for the server.
    *   It initializes the `FastMCP` instance, loads configurations, registers tools, and starts the Uvicorn ASGI server.

2.  **`FastMCP` (`mcp.server.fastmcp.FastMCP`):**
    *   The core library that implements the Model Context Protocol.
    *   It handles tool registration, management, and the communication protocol (including SSE for real-time updates).

3.  **Starlette:**
    *   A lightweight ASGI framework/toolkit used by `FastMCP` to handle web requests, routing (e.g., `/sse`, `/messages`), and other web-server functionalities.

4.  **Uvicorn:**
    *   An ASGI server that runs the Starlette application, making it accessible over HTTP.

5.  **Environment Variables & Configuration:**
    *   The server relies on environment variables for configuration. These can be set directly in your environment or loaded from a `.env` file (using `python-dotenv`) in your project root during development.
    *   Key variables include:
        *   `MCP_SERVER_NAME`: Name for your MCP server.
        *   `N8N_BASE_URL`: Base URL of your n8n instance.
        *   `N8N_API_KEY`: API key for authenticating with your n8n instance.
        *   `MCP_HOST`: Host address for the server to listen on (e.g., `0.0.0.0`).
        *   `MCP_PORT`: Port for the server (e.g., `8000`).
        *   Any API keys or specific configurations required by individual tools.

6.  **Modular Tool Loading:**
    *   Tools are no longer defined directly in the main server script. Instead, they reside in their own Python files within the `tools/` directory.
    *   The main server script imports a `register` function from each tool module and calls it, passing the `FastMCP` instance. This registers the tool with the server.
    *   `tools/__init__.py` makes the `tools` directory a Python package.
    *   Helper functions, like `make_n8n_request` in `tools/n8n_helpers.py`, can be shared among tools.

## Tool Development Guide

Creating new tools for the MCP server involves a few straightforward steps:

### 1. Create a New Tool File

*   Navigate to the `tools/` directory in your project.
*   Create a new Python file for your tool (e.g., `my_custom_tool.py`).

### 2. Define the Tool Function

*   Inside your new tool file, define an `async` function that will perform the tool's action.
*   **Function Signature:**
    *   The function must be an `async def` function.
    *   It should accept arguments relevant to its operation. Use type hints for clarity.
    *   It must return a Python dictionary (`Dict[str, Any]`). This dictionary will be serialized to JSON and sent as the tool's output.
*   **Docstring:**
    *   Write a clear and concise docstring for your tool function. The first line should be a brief summary of what the tool does. Subsequent lines can detail arguments, behavior, and the structure of the returned dictionary.
    *   **MCP uses this docstring to understand and describe the tool to AI agents.**
*   **Logging and Error Handling:**
    *   Use `print()` for basic logging (e.g., `print(f"INFO: My tool started with {arg}")`).
    *   Handle potential errors gracefully and return an error dictionary, typically including an `"error"` key and a `"status": "error"` key. Example: `return {"error": "Something went wrong", "details": str(e), "status": "error"}`.

### 3. Implement the `register` Function

*   In the same tool file, define a function called `register`.
*   This function must accept one argument: `mcp_instance` (which will be your `FastMCP` server object).
*   Inside `register`, use the `@mcp_instance.tool()` decorator on your tool function to register it with the MCP server.

```python
# tools/my_custom_tool.py
from typing import Dict, Any
import os # For accessing environment variables if needed

async def my_custom_tool_function(param1: str, param2: int) -> Dict[str, Any]:
    """
    This is my custom tool that does something interesting.

    Args:
        param1: A string parameter.
        param2: An integer parameter.

    Returns:
        A dictionary containing the result of the operation.
    """
    print(f"INFO: my_custom_tool_function called with param1: {param1}, param2: {param2}")
    
    # Example: Accessing an API key from environment variables
    # MY_SERVICE_API_KEY = os.getenv("MY_SERVICE_API_KEY")
    # if not MY_SERVICE_API_KEY:
    #     return {"error": "MY_SERVICE_API_KEY is not configured.", "status": "error"}

    try:
        # ... your tool logic here ...
        result_data = f"Processed {param1} and {param2}"
        return {
            "result": result_data,
            "status": "success"
        }
    except Exception as e:
        print(f"ERROR: my_custom_tool_function failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

def register(mcp_instance):
    mcp_instance.tool()(my_custom_tool_function)
```

### 4. Manage Dependencies and Configuration

*   **Imports:** Add any necessary imports at the top of your tool file (e.g., `import httpx`, `import datetime`, `from .n8n_helpers import make_n8n_request`).
*   **Environment Variables:** If your tool needs API keys or other configurations, instruct users to set them as environment variables. Access them within your tool using `os.getenv("YOUR_VARIABLE_NAME")`. Clearly document any required environment variables in the tool's docstring or related documentation.
*   **Shared Helpers:** If you have common logic (like API request functions), place them in a helper file (e.g., `tools/n8n_helpers.py`) and import them into your tool using relative imports (e.g., `from .n8n_helpers import make_n8n_request`).

### 5. Update the Main Server Script

*   Open your main server script (e.g., `mcp_n8n_server.py`).
*   Import the `register` function from your new tool module:
    ```python
    from tools import my_custom_tool 
    ```
*   In the section where tools are registered, call the `register` function, passing your `mcp` instance:
    ```python
    # Initialize FastMCP server
    mcp = FastMCP(MCP_SERVER_NAME)

    # --- Register Tools ---
    # ... other tool registrations ...
    my_custom_tool.register(mcp) 
    # ...
    ```

### Example: `tools/calculator_tool.py`

```python
# tools/calculator_tool.py
from typing import Dict, Any

async def calculator(operation: str, num1: float, num2: float) -> Dict[str, Any]:
    """
    Perform basic arithmetic operations (add, subtract, multiply, divide).
    
    Args:
        operation: The operation to perform - "add", "subtract", "multiply", "divide"
        num1: The first number
        num2: The second number
        
    Returns:
        Dict containing the result and a description of the operation performed
    """
    # ... (implementation as previously defined) ...
    pass # Placeholder for brevity

def register(mcp_instance):
    mcp_instance.tool()(calculator)
```
And in `mcp_n8n_server.py`:
```python
# ... other imports ...
from tools import calculator_tool
# ...

mcp = FastMCP(MCP_SERVER_NAME)

# --- Register Tools ---
calculator_tool.register(mcp)
# ... other tool registrations ...
```

## Running the Server

Once your tools are developed and registered:

1.  Ensure all required environment variables are set (or defined in your `.env` file).
2.  Run the main server script from your terminal:
    ```bash
    python your_main_server_script.py 
    ```
    (e.g., `python mcp_n8n_server.py`)

The server will start, and Uvicorn will typically print the address where it's listening (e.g., `http://0.0.0.0:8000`). Your MCP tools will then be available for interaction.

## Best Practices

*   **Clear Docstrings:** Make your tool docstrings very descriptive. This is the primary way AI agents (and other developers) understand what your tool does and how to use it.
*   **Idempotency:** If possible, design tools to be idempotent (calling them multiple times with the same input produces the same result without unintended side effects).
*   **Error Reporting:** Provide clear error messages in the dictionary returned by the tool if something goes wrong.
*   **Security:** Be mindful of security, especially if tools interact with sensitive APIs or data. Ensure API keys are handled via environment variables and not hardcoded.
*   **Keep Tools Focused:** Each tool should ideally perform one specific task well. 