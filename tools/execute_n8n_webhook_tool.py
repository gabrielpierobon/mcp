import os
from typing import Any, Dict
import httpx

async def execute_n8n_webhook(webhook_id_or_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    print(f"INFO: Executing n8n webhook: {webhook_id_or_url}")
    n8n_base_url = os.getenv("N8N_BASE_URL")
    
    if not n8n_base_url:
        return {"error": "N8N_BASE_URL is not configured on the server for webhook execution (from execute_n8n_webhook_tool)."}
    
    target_url = webhook_id_or_url
    # If it's not a full URL, construct it using N8N_BASE_URL
    if not ("://" in webhook_id_or_url):
         target_url = f"{n8n_base_url.rstrip('/')}/webhook/{webhook_id_or_url.lstrip('/')}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(target_url, json=payload, timeout=60.0)
            response.raise_for_status()
            try:
                # Try to parse JSON, but fall back to text if it fails
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

def register(mcp_instance):
    mcp_instance.tool()(execute_n8n_webhook) 