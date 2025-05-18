import os
from typing import Any, Dict, List
import httpx

async def make_n8n_request(endpoint: str, method: str = "GET", payload: Dict[str, Any] = None) -> Dict[str, Any] | List[Any] | None:
    n8n_base_url = os.getenv("N8N_BASE_URL")
    n8n_api_key = os.getenv("N8N_API_KEY")

    if not n8n_base_url or not n8n_api_key:
        # Use a simple print if mcp.log isn't available early or if mcp object changes
        print(f"ERROR: n8n URL or API Key is not configured (called from n8n_helpers). ENV N8N_BASE_URL: {'set' if n8n_base_url else 'not set'}, N8N_API_KEY: {'set' if n8n_api_key else 'not set'}")
        return {"error": "n8n integration is not configured on the server."}
    headers = {
        "Accept": "application/json",
        "X-N8N-API-KEY": n8n_api_key,
    }
    url = f"{n8n_base_url.rstrip('/')}/api/v1/{endpoint.lstrip('/')}"
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