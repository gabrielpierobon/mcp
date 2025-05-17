import asyncio
import os
from typing import Any, Dict, List

import httpx
from mcp.server.fastmcp import FastMCP
# SseServerTransport might not be needed if mcp.sse_app() handles it
# from mcp.server.sse import SseServerTransport 
from starlette.applications import Starlette
from starlette.routing import Mount # Route might not be needed
from starlette.types import Scope, Receive, Send # Might not be needed for handlers
import uvicorn

# Optional: Load .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- Server Configuration ---
MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "n8n-integration-server")
N8N_BASE_URL = os.getenv("N8N_BASE_URL")
N8N_API_KEY = os.getenv("N8N_API_KEY")

# Initialize FastMCP server
mcp = FastMCP(MCP_SERVER_NAME)

# --- Helper for n8n API Requests (Keep this) ---
async def make_n8n_request(endpoint: str, method: str = "GET", payload: Dict[str, Any] = None) -> Dict[str, Any] | List[Any] | None:
    if not N8N_BASE_URL or not N8N_API_KEY:
        # Use a simple print if mcp.log isn't available early or if mcp object changes
        print("ERROR: n8n URL or API Key is not configured.")
        return {"error": "n8n integration is not configured on the server."}
    headers = {
        "Accept": "application/json",
        "X-N8N-API-KEY": N8N_API_KEY,
    }
    url = f"{N8N_BASE_URL.rstrip('/')}/api/v1/{endpoint.lstrip('/')}"
    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "POST":
                response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            elif method.upper() == "PUT":
                response = await client.put(url, headers=headers, json=payload, timeout=30.0)
            else: # Default to GET
                response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"ERROR: n8n API request failed (HTTP {e.response.status_code}): {e.response.text}")
            return {"error": f"n8n API error: {e.response.status_code}", "details": e.response.text}
        except httpx.RequestError as e:
            print(f"ERROR: n8n API request failed (Request Error): {str(e)}")
            return {"error": "Failed to connect to n8n.", "details": str(e)}
        except Exception as e:
            print(f"ERROR: An unexpected error occurred during n8n API request: {str(e)}")
            return {"error": "An unexpected error occurred.", "details": str(e)}

# --- MCP Tools (Keep these) ---
@mcp.tool()
async def list_n8n_workflows() -> Dict[str, Any]:
    print("INFO: Attempting to list n8n workflows.")
    if not N8N_BASE_URL or not N8N_API_KEY:
        return {"error": "n8n URL or API Key is not configured for the MCP server."}
    response_data = await make_n8n_request("workflows")
    if response_data and isinstance(response_data, dict) and "error" in response_data:
        return response_data
    if isinstance(response_data, list):
        workflows = [
            {"id": wf.get("id"), "name": wf.get("name"), "active": wf.get("active"), "createdAt": wf.get("createdAt")}
            for wf in response_data if wf.get("active")
        ]
        return {"workflows": workflows}
    print(f"WARNING: Unexpected response format from n8n /workflows endpoint: {type(response_data)}")
    return {"error": "Failed to retrieve or parse workflows from n8n.", "raw_response": str(response_data)[:500]}

@mcp.tool()
async def execute_n8n_webhook(webhook_id_or_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    print(f"INFO: Executing n8n webhook: {webhook_id_or_url}") # Simplified logging
    if not N8N_BASE_URL: # Check N8N_BASE_URL for constructing local webhook URLs
        return {"error": "n8n URL is not configured on the server for webhook execution."}
    
    target_url = webhook_id_or_url
    if not ("://" in webhook_id_or_url):
         target_url = f"{N8N_BASE_URL.rstrip('/')}/webhook/{webhook_id_or_url.lstrip('/')}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(target_url, json=payload, timeout=60.0)
            response.raise_for_status()
            try:
                return {"status_code": response.status_code, "response_data": response.json()}
            except Exception:
                return {"status_code": response.status_code, "response_text": response.text}
        except httpx.HTTPStatusError as e:
            print(f"ERROR: n8n webhook execution failed (HTTP {e.response.status_code}): {e.response.text}")
            return {"error": f"n8n webhook error: {e.response.status_code}", "details": e.response.text}
        except httpx.RequestError as e:
            print(f"ERROR: n8n webhook execution failed (Request Error): {str(e)}")
            return {"error": "Failed to connect to n8n webhook.", "details": str(e)}
        except Exception as e:
            print(f"ERROR: An unexpected error occurred during n8n webhook execution: {str(e)}")
            return {"error": "An unexpected error occurred.", "details": str(e)}

# --- Starlette App Setup ---
# Try to use mcp.sse_app() if it exists
try:
    sse_application = mcp.sse_app()
    app = Starlette(
        routes=[
            Mount("/", app=sse_application, name="mcp_sse_app"),
        ]
    )
    print("INFO: Using mcp.sse_app() for routing.")
except AttributeError:
    print("WARNING: mcp.sse_app() not found. Falling back to manual handlers (which may be problematic).")
    # Fallback to previous manual setup (which had issues, here for completeness if needed for debug)
    # This part would need SseServerTransport and the handler functions to be defined as before
    # For now, if sse_app() fails, the server will likely fail to handle routes properly without further changes.
    async def fallback_handle_sse(scope: Scope, receive: Receive, send: Send):
        await send({'type': 'http.response.start', 'status': 501, 'headers': [(b'content-type', b'text/plain')]})
        await send({'type': 'http.response.body', 'body': b'Fallback SSE handler - mcp.sse_app() not found!', 'more_body': False})
    async def fallback_handle_messages_post(scope: Scope, receive: Receive, send: Send):
        await send({'type': 'http.response.start', 'status': 501, 'headers': [(b'content-type', b'text/plain')]})
        await send({'type': 'http.response.body', 'body': b'Fallback POST handler - mcp.sse_app() not found!', 'more_body': False})
    app = Starlette(
        routes=[
            Mount("/sse", app=fallback_handle_sse, name="sse_endpoint"),
            Mount("/messages", app=fallback_handle_messages_post, name="message_post_endpoint"),
        ]
    )

# --- Main Execution ---
if __name__ == "__main__":
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8000"))
    
    # Ensure N8N_BASE_URL and N8N_API_KEY are defined before this block if used by mcp.sse_app() implicitly
    N8N_BASE_URL = os.getenv("N8N_BASE_URL") 
    N8N_API_KEY = os.getenv("N8N_API_KEY")
    MCP_SERVER_NAME = os.getenv("MCP_SERVER_NAME", "n8n-integration-server") # Ensure this is defined for print

    if not N8N_BASE_URL or not N8N_API_KEY:
        print("WARNING: N8N_BASE_URL or N8N_API_KEY environment variables are not set.")
        print("The n8n integration tools will not function correctly.")
        print("Please set them or provide a .env file.")

    print(f"Starting {MCP_SERVER_NAME} on http://{host}:{port}")
    # The SSE endpoint for n8n will depend on how sse_app() structures its routes.
    # Typically, it might create /sse and /messages under the mount point.
    # So, if mounted at "/", n8n would connect to http://actual_host_ip_or_host.docker.internal:port/sse
    print(f"SSE endpoint for n8n MCP Client Tool (if using mcp.sse_app() mounted at '/'): http://<YOUR_HOST_IP_OR_host.docker.internal>:{port}/sse")
    
    # Ensure mcp object is defined before trying to access its attributes
    # Assuming mcp = FastMCP(MCP_SERVER_NAME) is defined globally earlier in the script
    if hasattr(mcp, '_tool_manager') and hasattr(mcp._tool_manager, '_tools'):
        print(f"Registered tools: {', '.join(mcp._tool_manager._tools.keys())}")
    else:
        print("Registered tools: (Could not determine from mcp object - check structure)")
    
    # Assuming 'app' is defined globally from the try/except block for mcp.sse_app()
    uvicorn.run(app, host=host, port=port)