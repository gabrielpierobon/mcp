import asyncio
import os
from typing import Any, Dict, List

import httpx
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
import uvicorn

# Optional: Load .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass # python-dotenv is not installed, proceed without it

# --- Server Configuration ---
MCP_SERVER_NAME = "n8n-integration-server"
N8N_BASE_URL = os.getenv("N8N_BASE_URL") # e.g., http://localhost:5678
N8N_API_KEY = os.getenv("N8N_API_KEY")

# Initialize FastMCP server
mcp = FastMCP(MCP_SERVER_NAME)

# --- Helper for n8n API Requests ---
async def make_n8n_request(endpoint: str, method: str = "GET", payload: Dict[str, Any] = None) -> Dict[str, Any] | List[Any] | None:
    """Makes an authenticated request to the n8n API."""
    if not N8N_BASE_URL or not N8N_API_KEY:
        mcp.log(level="error", message="n8n URL or API Key is not configured.")
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
            
            response.raise_for_status()  # Raises an exception for 4XX/5XX responses
            return response.json()
        except httpx.HTTPStatusError as e:
            mcp.log(level="error", message=f"n8n API request failed (HTTP {e.response.status_code}): {e.response.text}")
            return {"error": f"n8n API error: {e.response.status_code}", "details": e.response.text}
        except httpx.RequestError as e:
            mcp.log(level="error", message=f"n8n API request failed (Request Error): {str(e)}")
            return {"error": "Failed to connect to n8n.", "details": str(e)}
        except Exception as e:
            mcp.log(level="error", message=f"An unexpected error occurred during n8n API request: {str(e)}")
            return {"error": "An unexpected error occurred.", "details": str(e)}

# --- MCP Tools ---

@mcp.tool()
async def list_n8n_workflows() -> Dict[str, Any]:
    """
    Retrieves a list of all active workflows from the configured n8n instance.
    """
    mcp.log(level="info", message="Attempting to list n8n workflows.")
    if not N8N_BASE_URL or not N8N_API_KEY:
        return {"error": "n8n URL or API Key is not configured for the MCP server."}
        
    response_data = await make_n8n_request("workflows")
    
    if response_data and isinstance(response_data, dict) and "error" in response_data:
        return response_data # Error already formatted by make_n8n_request

    if isinstance(response_data, list):
        # Filter and simplify the output if desired
        workflows = [
            {"id": wf.get("id"), "name": wf.get("name"), "active": wf.get("active"), "createdAt": wf.get("createdAt")}
            for wf in response_data if wf.get("active")
        ]
        return {"workflows": workflows}
    
    mcp.log(level="warning", message=f"Unexpected response format from n8n /workflows endpoint: {type(response_data)}")
    return {"error": "Failed to retrieve or parse workflows from n8n.", "raw_response": str(response_data)[:500]}

@mcp.tool()
async def execute_n8n_webhook(webhook_id_or_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes an n8n webhook by its ID or full URL.
    
    Args:
        webhook_id_or_url: The ID of the n8n webhook (e.g., 'your-webhook-id') or its full URL.
        payload: A JSON object containing the data to send to the webhook.
    """
    if not N8N_BASE_URL:
        mcp.log(level="error", message="n8n URL is not configured.")
        return {"error": "n8n URL is not configured on the server."}

    if "://" in webhook_id_or_url: # If it's a full URL
        target_url = webhook_id_or_url
    else: # Assume it's a webhook ID
        target_url = f"{N8N_BASE_URL.rstrip('/')}/webhook/{webhook_id_or_url.lstrip('/')}"

    mcp.log(level="info", message=f"Executing n8n webhook: {target_url}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(target_url, json=payload, timeout=60.0) # Longer timeout for webhooks
            response.raise_for_status()
            
            try:
                return {"status_code": response.status_code, "response_data": response.json()}
            except Exception: # If response is not JSON
                return {"status_code": response.status_code, "response_text": response.text}
        except httpx.HTTPStatusError as e:
            mcp.log(level="error", message=f"n8n webhook execution failed (HTTP {e.response.status_code}): {e.response.text}")
            return {"error": f"n8n webhook error: {e.response.status_code}", "details": e.response.text}
        except httpx.RequestError as e:
            mcp.log(level="error", message=f"n8n webhook execution failed (Request Error): {str(e)}")
            return {"error": "Failed to connect to n8n webhook.", "details": str(e)}
        except Exception as e:
            mcp.log(level="error", message=f"An unexpected error occurred during n8n webhook execution: {str(e)}")
            return {"error": "An unexpected error occurred.", "details": str(e)}

# --- SSE Transport Setup ---
SSE_TRANSPORT_PATH = "/messages" # MCP standard path for SSE messaging
sse_transport = SseServerTransport(SSE_TRANSPORT_PATH)

async def handle_sse(scope, receive, send):
    """Handles the SSE connection for MCP."""
    async with sse_transport.connect_sse(scope, receive, send) as streams:
        await mcp.run_async(streams[0], streams[1])

async def handle_messages_post(scope, receive, send):
    """Handles POST requests for messages, typically for initial connection or non-SSE messages."""
    await sse_transport.handle_post_message(scope, receive, send)

# Starlette App
app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse, name="sse_endpoint"), # Keep /sse for n8n convention
        Route(SSE_TRANSPORT_PATH, endpoint=handle_messages_post, methods=["POST"], name="message_post_endpoint"),
    ]
)

# --- Main Execution ---
if __name__ == "__main__":
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_PORT", "8000"))
    
    if not N8N_BASE_URL or not N8N_API_KEY:
        print("WARNING: N8N_BASE_URL or N8N_API_KEY environment variables are not set.")
        print("The n8n integration tools will not function correctly.")
        print("Please set them or provide a .env file.")

    print(f"Starting {MCP_SERVER_NAME} on http://{host}:{port}")
    print(f"SSE endpoint for n8n MCP Client Tool: http://{host}:{port}/sse")
    print(f"Registered tools: {', '.join(mcp.tools.keys())}")
    
    uvicorn.run(app, host=host, port=port) 