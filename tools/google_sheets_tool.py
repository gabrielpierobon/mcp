# tools/google_sheets_tool.py
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv
import importlib.util

# Load environment variables
load_dotenv()

# Check if Google API client libraries are installed
GOOGLE_APIS_AVAILABLE = (
    importlib.util.find_spec("google.auth") is not None and
    importlib.util.find_spec("googleapiclient") is not None and
    importlib.util.find_spec("google_auth_oauthlib") is not None
)

if GOOGLE_APIS_AVAILABLE:
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError
        print("INFO: Google Sheets API libraries successfully imported")
    except ImportError as e:
        print(f"WARNING: Error importing Google API components: {str(e)}")
        GOOGLE_APIS_AVAILABLE = False
else:
    print("WARNING: Google API client libraries are not installed.")
    print("To install them, run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")

# Google API scopes for Sheets
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Google API credentials paths
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")

# ======================
# CONTEXT MEMORY SYSTEM
# ======================

# Global context to store recent spreadsheets
_recent_spreadsheets_context = {
    "last_spreadsheet": None,
    "recent_spreadsheets": []  # Store multiple recent sheets
}

def _store_spreadsheet_context(spreadsheet_id: str, title: str, sheet_names: List[str], url: str):
    """Store spreadsheet context for future operations."""
    context = {
        "id": spreadsheet_id,
        "title": title,
        "default_sheet": sheet_names[0] if sheet_names else "Sheet1",
        "all_sheets": sheet_names,
        "url": url,
        "type": "spreadsheet"
    }
    _recent_spreadsheets_context["last_spreadsheet"] = context
    _recent_spreadsheets_context["recent_spreadsheets"].insert(0, context)
    # Keep only last 10 spreadsheets
    _recent_spreadsheets_context["recent_spreadsheets"] = _recent_spreadsheets_context["recent_spreadsheets"][:10]

# ======================
# AUTHENTICATION FUNCTIONS
# ======================

def get_google_credentials():
    """Get Google API credentials using OAuth2 flow."""
    if not GOOGLE_APIS_AVAILABLE:
        return None
    
    creds = None
    
    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"WARNING: Error loading existing token: {str(e)}")
    
    # If no valid credentials, run OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save refreshed credentials
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"WARNING: Error refreshing credentials: {str(e)}")
                creds = None
        
        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"ERROR: Google credentials file not found at {CREDENTIALS_FILE}")
                return None
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                
                # Save credentials for future use
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
                    
            except Exception as e:
                print(f"ERROR: OAuth flow failed: {str(e)}")
                return None
    
    return creds

def get_service(service_name: str, version: str):
    """Get Google API service client."""
    creds = get_google_credentials()
    if not creds:
        return None
    
    try:
        return build(service_name, version, credentials=creds)
    except Exception as e:
        print(f"ERROR: Failed to build {service_name} service: {str(e)}")
        return None

# ======================
# CONTEXT QUERY TOOLS
# ======================

async def list_recent_spreadsheets() -> Dict[str, Any]:
    """
    List recently created Google Spreadsheets from this session.
    
    Returns:
        Dictionary containing recent spreadsheets information
    """
    print("INFO: list_recent_spreadsheets called")
    
    return {
        "recent_spreadsheets": _recent_spreadsheets_context["recent_spreadsheets"],
        "last_spreadsheet": _recent_spreadsheets_context["last_spreadsheet"],
        "count": len(_recent_spreadsheets_context["recent_spreadsheets"]),
        "status": "success"
    }

async def find_spreadsheet_by_title(title_search: str) -> Dict[str, Any]:
    """
    Find a spreadsheet by searching its title.
    
    Args:
        title_search: Partial title to search for (case-insensitive)
    
    Returns:
        Dictionary containing matching spreadsheets
    """
    print(f"INFO: find_spreadsheet_by_title called with search: {title_search}")
    
    matching_sheets = [s for s in _recent_spreadsheets_context["recent_spreadsheets"] 
                      if title_search.lower() in s["title"].lower()]
    
    return {
        "matching_spreadsheets": matching_sheets,
        "search_term": title_search,
        "count": len(matching_sheets),
        "all_available_titles": [s["title"] for s in _recent_spreadsheets_context["recent_spreadsheets"]],
        "status": "success"
    }

# ======================
# GOOGLE SHEETS TOOLS
# ======================

async def create_google_sheet(
    title: str,
    sheet_names: Optional[List[str]] = None,
    share_with: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a new Google Sheet with optional multiple sheets and sharing.
    
    Args:
        title: Title of the new spreadsheet (required)
        sheet_names: List of sheet names to create (optional, defaults to ["Sheet1"])
        share_with: List of email addresses to share with (optional)
    
    Returns:
        Dictionary containing the created spreadsheet information
    """
    print(f"INFO: create_google_sheet called with title: {title}")
    
    if not GOOGLE_APIS_AVAILABLE:
        return {
            "error": "Google API client libraries are not installed. Please install them with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client",
            "status": "error"
        }
    
    try:
        sheets_service = get_service('sheets', 'v4')
        drive_service = get_service('drive', 'v3')
        
        if not sheets_service:
            return {
                "error": "Failed to authenticate with Google Sheets API. Please check your credentials.",
                "status": "error"
            }
        
        # Create the spreadsheet
        spreadsheet_body = {
            'properties': {
                'title': title
            }
        }
        
        # Add additional sheets if specified
        if sheet_names and len(sheet_names) > 1:
            spreadsheet_body['sheets'] = []
            for i, sheet_name in enumerate(sheet_names):
                sheet_properties = {
                    'properties': {
                        'title': sheet_name,
                        'sheetId': i
                    }
                }
                spreadsheet_body['sheets'].append(sheet_properties)
        
        request = sheets_service.spreadsheets().create(body=spreadsheet_body)
        response = request.execute()
        
        spreadsheet_id = response.get('spreadsheetId')
        spreadsheet_url = response.get('spreadsheetUrl')
        created_sheets = [sheet['properties']['title'] for sheet in response.get('sheets', [])]
        
        # Store context for future operations
        _store_spreadsheet_context(spreadsheet_id, title, created_sheets, spreadsheet_url)
        
        result = {
            "spreadsheet_id": spreadsheet_id,
            "spreadsheet_url": spreadsheet_url,
            "title": title,
            "sheets": created_sheets,
            "status": "success"
        }
        
        # Share the spreadsheet if email addresses provided
        if share_with and drive_service:
            shared_successfully = []
            for email in share_with:
                try:
                    permission = {
                        'type': 'user',
                        'role': 'writer',
                        'emailAddress': email
                    }
                    drive_service.permissions().create(
                        fileId=spreadsheet_id,
                        body=permission,
                        sendNotificationEmail=True
                    ).execute()
                    shared_successfully.append(email)
                except Exception as e:
                    print(f"WARNING: Failed to share with {email}: {str(e)}")
            
            result["shared_with"] = shared_successfully
            if len(shared_successfully) < len(share_with):
                result["sharing_warnings"] = f"Some sharing failed. Successfully shared with: {shared_successfully}"
        
        return result
        
    except HttpError as e:
        return {
            "error": f"Google Sheets API error: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: create_google_sheet failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def write_to_sheet(
    spreadsheet_id: str,
    range_name: str,
    values: List[List[str]],
    value_input_option: str = "USER_ENTERED"
) -> Dict[str, Any]:
    """
    Write data to a Google Sheet.
    
    Args:
        spreadsheet_id: ID of the spreadsheet (required)
        range_name: A1 notation range (e.g., "Sheet1!A1:C3", "A1:B10") (required)
        values: 2D array of string values to write (required) - example: [["Name", "Age"], ["John", "30"], ["Jane", "25"]]
        value_input_option: How values should be interpreted ("RAW" or "USER_ENTERED", default: "USER_ENTERED")
    
    Returns:
        Dictionary containing the update results
    """
    print(f"INFO: write_to_sheet called for spreadsheet {spreadsheet_id}")
    
    if not GOOGLE_APIS_AVAILABLE:
        return {
            "error": "Google API client libraries are not installed.",
            "status": "error"
        }
    
    try:
        service = get_service('sheets', 'v4')
        if not service:
            return {
                "error": "Failed to authenticate with Google Sheets API.",
                "status": "error"
            }
        
        body = {
            'values': values
        }
        
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            body=body
        ).execute()
        
        return {
            "spreadsheet_id": spreadsheet_id,
            "updated_range": result.get('updatedRange'),
            "updated_rows": result.get('updatedRows'),
            "updated_columns": result.get('updatedColumns'),
            "updated_cells": result.get('updatedCells'),
            "status": "success"
        }
        
    except HttpError as e:
        return {
            "error": f"Google Sheets API error: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: write_to_sheet failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def append_to_last_sheet(
    values: List[List[str]],
    start_row: Optional[int] = None,
    sheet_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Append data to the most recently created or modified spreadsheet.
    
    Args:
        values: 2D array of string values to append (required)
        start_row: Optional row number to start appending from (auto-calculated if not provided)
        sheet_name: Optional sheet name to append to (uses default sheet if not provided)
    
    Returns:
        Dictionary containing the update results
    """
    print("INFO: append_to_last_sheet called")
    
    if not _recent_spreadsheets_context["last_spreadsheet"]:
        return {
            "error": "No recent spreadsheet found. Please create a spreadsheet first or use write_to_sheet with a specific spreadsheet ID.",
            "status": "error"
        }
    
    spreadsheet_id = _recent_spreadsheets_context["last_spreadsheet"]["id"]
    target_sheet = sheet_name or _recent_spreadsheets_context["last_spreadsheet"]["default_sheet"]
    
    # If no start_row specified, find the next empty row
    if start_row is None:
        try:
            # Read existing data to find next row
            existing_data = await read_from_sheet(
                spreadsheet_id=spreadsheet_id,
                range_name=f"{target_sheet}!A:A"
            )
            start_row = len(existing_data.get("values", [])) + 1
        except Exception as e:
            print(f"WARNING: Could not determine next row, starting at row 1: {str(e)}")
            start_row = 1
    
    # Calculate the range based on data dimensions
    num_rows = len(values)
    num_cols = len(values[0]) if values else 0
    end_row = start_row + num_rows - 1
    end_col = chr(ord('A') + num_cols - 1)  # Convert to letter (A, B, C, etc.)
    
    range_name = f"{target_sheet}!A{start_row}:{end_col}{end_row}"
    
    result = await write_to_sheet(
        spreadsheet_id=spreadsheet_id,
        range_name=range_name,
        values=values,
        value_input_option="USER_ENTERED"
    )
    
    if result.get("status") == "success":
        result["appended_to"] = {
            "spreadsheet_id": spreadsheet_id,
            "sheet_name": target_sheet,
            "start_row": start_row,
            "title": _recent_spreadsheets_context["last_spreadsheet"]["title"],
            "url": _recent_spreadsheets_context["last_spreadsheet"]["url"]
        }
    
    return result

async def append_to_sheet_by_title(
    title_search: str,
    values: List[List[str]],
    start_row: Optional[int] = None,
    sheet_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Append data to a spreadsheet found by title search.
    
    Args:
        title_search: Partial title to search for in recent spreadsheets (required)
        values: 2D array of string values to append (required)
        start_row: Optional row number to start appending from
        sheet_name: Optional sheet name to append to
    
    Returns:
        Dictionary containing the update results
    """
    print(f"INFO: append_to_sheet_by_title called with search: {title_search}")
    
    # Find matching spreadsheet
    matching_sheets = [s for s in _recent_spreadsheets_context["recent_spreadsheets"] 
                      if title_search.lower() in s["title"].lower()]
    
    if not matching_sheets:
        return {
            "error": f"No spreadsheet found with title containing: {title_search}",
            "available_spreadsheets": [s["title"] for s in _recent_spreadsheets_context["recent_spreadsheets"]],
            "status": "error"
        }
    
    # Use the most recent match
    target_sheet_context = matching_sheets[0]
    spreadsheet_id = target_sheet_context["id"]
    target_sheet = sheet_name or target_sheet_context["default_sheet"]
    
    # If no start_row specified, find the next empty row
    if start_row is None:
        try:
            existing_data = await read_from_sheet(
                spreadsheet_id=spreadsheet_id,
                range_name=f"{target_sheet}!A:A"
            )
            start_row = len(existing_data.get("values", [])) + 1
        except Exception as e:
            print(f"WARNING: Could not determine next row, starting at row 1: {str(e)}")
            start_row = 1
    
    # Calculate the range based on data dimensions
    num_rows = len(values)
    num_cols = len(values[0]) if values else 0
    end_row = start_row + num_rows - 1
    end_col = chr(ord('A') + num_cols - 1)
    
    range_name = f"{target_sheet}!A{start_row}:{end_col}{end_row}"
    
    result = await write_to_sheet(
        spreadsheet_id=spreadsheet_id,
        range_name=range_name,
        values=values,
        value_input_option="USER_ENTERED"
    )
    
    if result.get("status") == "success":
        result["appended_to"] = {
            "spreadsheet_id": spreadsheet_id,
            "sheet_name": target_sheet,
            "start_row": start_row,
            "title": target_sheet_context["title"],
            "url": target_sheet_context["url"]
        }
    
    return result

async def read_from_sheet(
    spreadsheet_id: str,
    range_name: str
) -> Dict[str, Any]:
    """
    Read data from a Google Sheet.
    
    Args:
        spreadsheet_id: ID of the spreadsheet (required)
        range_name: A1 notation range (e.g., "Sheet1!A1:C10") (required)
    
    Returns:
        Dictionary containing the data from the sheet
    """
    print(f"INFO: read_from_sheet called for spreadsheet {spreadsheet_id}")
    
    if not GOOGLE_APIS_AVAILABLE:
        return {
            "error": "Google API client libraries are not installed.",
            "status": "error"
        }
    
    try:
        service = get_service('sheets', 'v4')
        if not service:
            return {
                "error": "Failed to authenticate with Google Sheets API.",
                "status": "error"
            }
        
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        values = result.get('values', [])
        
        return {
            "spreadsheet_id": spreadsheet_id,
            "range": range_name,
            "values": values,
            "row_count": len(values),
            "column_count": len(values[0]) if values else 0,
            "status": "success"
        }
        
    except HttpError as e:
        return {
            "error": f"Google Sheets API error: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: read_from_sheet failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def clear_sheet_range(
    spreadsheet_id: str,
    range_name: str
) -> Dict[str, Any]:
    """
    Clear data from a specific range in a Google Sheet.
    
    Args:
        spreadsheet_id: ID of the spreadsheet (required)
        range_name: A1 notation range to clear (e.g., "Sheet1!A1:C10") (required)
    
    Returns:
        Dictionary containing the operation results
    """
    print(f"INFO: clear_sheet_range called for spreadsheet {spreadsheet_id}")
    
    if not GOOGLE_APIS_AVAILABLE:
        return {
            "error": "Google API client libraries are not installed.",
            "status": "error"
        }
    
    try:
        service = get_service('sheets', 'v4')
        if not service:
            return {
                "error": "Failed to authenticate with Google Sheets API.",
                "status": "error"
            }
        
        result = service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            body={}
        ).execute()
        
        return {
            "spreadsheet_id": spreadsheet_id,
            "cleared_range": result.get('clearedRange'),
            "status": "success"
        }
        
    except HttpError as e:
        return {
            "error": f"Google Sheets API error: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: clear_sheet_range failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

def register(mcp_instance):
    """Register the Google Sheets tools with the MCP server"""
    if GOOGLE_APIS_AVAILABLE:
        # Core Sheets operations
        mcp_instance.tool()(create_google_sheet)
        mcp_instance.tool()(write_to_sheet)
        mcp_instance.tool()(read_from_sheet)
        mcp_instance.tool()(clear_sheet_range)
        
        # Context-aware operations
        mcp_instance.tool()(append_to_last_sheet)
        mcp_instance.tool()(append_to_sheet_by_title)
        
        # Context query tools
        mcp_instance.tool()(list_recent_spreadsheets)
        mcp_instance.tool()(find_spreadsheet_by_title)
        
        print("INFO: Google Sheets tools registered successfully")
    else:
        print("WARNING: Google Sheets tools were not registered because required libraries are not installed.")