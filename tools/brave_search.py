# tools/brave_search.py
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import os
import httpx
import json

# Load environment variables from .env file
load_dotenv()

# Get Brave API key from environment variables
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
print(f"DEBUG: BRAVE_API_KEY loaded: {'Yes' if BRAVE_API_KEY else 'No'}")

BRAVE_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"
BRAVE_LOCAL_SEARCH_URL = "https://api.search.brave.com/res/v1/web/local"

async def brave_web_search(
    query: str, 
    count: Optional[int] = 10, 
    offset: Optional[int] = 0
) -> Dict[str, Any]:
    """
    Execute web searches using Brave Search API with pagination and filtering.
    
    Args:
        query: Search terms (required)
        count: Results per page (optional, max 20)
        offset: Pagination offset (optional, max 9)
        
    Returns:
        Dictionary containing search results, metadata, and status
    """
    print(f"INFO: brave_web_search called with query: {query}, count: {count}, offset: {offset}")
    
    if not BRAVE_API_KEY:
        return {"error": "BRAVE_API_KEY is not configured.", "status": "error"}
    
    # Validate inputs
    if count is not None and (count < 1 or count > 20):
        return {"error": "Count must be between 1 and 20", "status": "error"}
    
    if offset is not None and (offset < 0 or offset > 9):
        return {"error": "Offset must be between 0 and 9", "status": "error"}
    
    # Prepare request parameters
    params = {
        "q": query,
        "count": count if count is not None else 10,
        "offset": offset if offset is not None else 0
    }
    
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                BRAVE_SEARCH_URL,
                params=params,
                headers=headers
            )
            
            if response.status_code != 200:
                return {
                    "error": f"Brave Search API returned status code {response.status_code}",
                    "details": response.text,
                    "status": "error"
                }
            
            search_results = response.json()
            
            # Debug the raw response structure
            print(f"DEBUG: API response keys: {list(search_results.keys())}")
            
            # Extract results from the appropriate sections
            web_results = search_results.get("web", {}).get("results", [])
            news_results = search_results.get("news", {}).get("results", [])
            videos_results = search_results.get("videos", {}).get("results", [])
            
            # Combine all results
            all_results = web_results + news_results + videos_results
            
            # Format response structure
            formatted_results = {
                "query": query,
                "results": all_results,
                "total_count": search_results.get("web", {}).get("totalCount", 0),
                "news_count": len(news_results),
                "videos_count": len(videos_results),
                "web_count": len(web_results),
                "mixed": search_results.get("mixed", {}),
                # Include the full response for debugging
                "search_info": {
                    "available_sections": list(search_results.keys())
                },
                "status": "success"
            }
            
            return formatted_results
            
    except Exception as e:
        print(f"ERROR: brave_web_search failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def brave_local_search(
    query: str,
    count: Optional[int] = 10
) -> Dict[str, Any]:
    """
    Search for local businesses and services using Brave Search API.
    Automatically falls back to web search if no local results found.
    
    Args:
        query: Local search terms (required)
        count: Number of results (optional, max 20)
        
    Returns:
        Dictionary containing local search results, metadata, and status
    """
    print(f"INFO: brave_local_search called with query: {query}, count: {count}")
    
    if not BRAVE_API_KEY:
        return {"error": "BRAVE_API_KEY is not configured.", "status": "error"}
    
    # Validate inputs
    if count is not None and (count < 1 or count > 20):
        return {"error": "Count must be between 1 and 20", "status": "error"}
    
    # Prepare request parameters
    params = {
        "q": query,
        "count": count if count is not None else 10
    }
    
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                BRAVE_LOCAL_SEARCH_URL,
                params=params,
                headers=headers
            )
            
            if response.status_code != 200:
                return {
                    "error": f"Brave Local Search API returned status code {response.status_code}",
                    "details": response.text,
                    "status": "error"
                }
            
            search_results = response.json()
            
            # Debug the raw response structure
            print(f"DEBUG: Local API response keys: {list(search_results.keys())}")
            
            # Check if we have local results
            local_places = search_results.get("local", {}).get("places", [])
            
            if not local_places:
                print(f"INFO: No local results found, falling back to web search")
                # Fallback to web search
                return await brave_web_search(query, count)
            
            # Format response structure
            formatted_results = {
                "query": query,
                "places": local_places,
                "total_count": len(local_places),
                "status": "success"
            }
            
            return formatted_results
            
    except Exception as e:
        print(f"ERROR: brave_local_search failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

def register(mcp_instance):
    """Register the Brave Search tools with the MCP server"""
    mcp_instance.tool()(brave_web_search)
    mcp_instance.tool()(brave_local_search)