import os
from typing import Any, Dict, List
from .n8n_helpers import make_n8n_request # Relative import

async def list_n8n_workflows() -> Dict[str, Any]:
    print("INFO: Attempting to list n8n workflows.")
    # These are fetched by make_n8n_request, but good to check early if needed for other logic
    n8n_base_url = os.getenv("N8N_BASE_URL") 
    n8n_api_key = os.getenv("N8N_API_KEY")
    if not n8n_base_url or not n8n_api_key:
        return {"error": "n8n URL or API Key is not configured for the MCP server (from list_n8n_workflows_tool)."}
    
    response_data = await make_n8n_request("workflows")
    
    if response_data and isinstance(response_data, dict) and "error" in response_data:
        return response_data # Error already formatted by make_n8n_request
        
    if isinstance(response_data, list):
        workflows = [
            {"id": wf.get("id"), "name": wf.get("name"), "active": wf.get("active"), "createdAt": wf.get("createdAt")}
            for wf in response_data if wf.get("active") # Filter for active workflows
        ]
        return {"workflows": workflows}
        
    print(f"WARNING: Unexpected response format from n8n /workflows endpoint: {type(response_data)}")
    return {"error": "Failed to retrieve or parse workflows from n8n.", "raw_response": str(response_data)[:500]}

def register(mcp_instance):
    mcp_instance.tool()(list_n8n_workflows) 