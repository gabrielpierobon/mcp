from typing import Dict, Any, Optional, List
import httpx
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Airtable Personal Access Token from environment variables
AIRTABLE_PERSONAL_ACCESS_TOKEN = os.getenv("AIRTABLE_PERSONAL_ACCESS_TOKEN")
AIRTABLE_BASE_URL = "https://api.airtable.com/v0"

# Headers for Airtable API requests
def get_airtable_headers():
    if not AIRTABLE_PERSONAL_ACCESS_TOKEN:
        return None
    return {
        "Authorization": f"Bearer {AIRTABLE_PERSONAL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

async def create_airtable_base(
    name: str,
    workspace_id: Optional[str] = None,
    tables: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Create a new Airtable base with optional initial tables.
    
    Args:
        name: Name of the new base (required)
        workspace_id: ID of the workspace to create the base in (optional)
        tables: List of table configurations to create initially (optional)
                Format: [{"name": "Table Name", "description": "Description", "fields": [...]}]
    
    Returns:
        Dictionary containing the created base information and status
    """
    print(f"INFO: create_airtable_base called with name: {name}")
    
    headers = get_airtable_headers()
    if not headers:
        return {
            "error": "AIRTABLE_PERSONAL_ACCESS_TOKEN is not configured. Please set it in your environment variables.",
            "status": "error"
        }
    
    # Prepare the request payload
    payload = {
        "name": name
    }
    
    if workspace_id:
        payload["workspaceId"] = workspace_id
    
    # Add initial tables if provided
    if tables:
        payload["tables"] = []
        for table in tables:
            table_config = {
                "name": table.get("name", "Untitled Table"),
                "fields": table.get("fields", [
                    {"name": "Name", "type": "singleLineText"}  # Default field
                ])
            }
            if table.get("description"):
                table_config["description"] = table["description"]
            payload["tables"].append(table_config)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AIRTABLE_BASE_URL}/meta/bases",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "base_id": result.get("id"),
                    "name": result.get("name"),
                    "permission_level": result.get("permissionLevel"),
                    "tables": result.get("tables", []),
                    "status": "success"
                }
            else:
                error_detail = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                return {
                    "error": f"Failed to create base. Status: {response.status_code}",
                    "details": error_detail,
                    "status": "error"
                }
                
    except Exception as e:
        print(f"ERROR: create_airtable_base failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def create_airtable_table(
    base_id: str,
    table_name: str,
    description: Optional[str] = None,
    fields: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Create a new table in an existing Airtable base.
    
    Args:
        base_id: ID of the base to create the table in (required)
        table_name: Name of the new table (required)
        description: Description of the table (optional)
        fields: List of field configurations (optional)
                Format: [{"name": "Field Name", "type": "singleLineText", "options": {...}}]
    
    Returns:
        Dictionary containing the created table information and status
    """
    print(f"INFO: create_airtable_table called with base_id: {base_id}, table_name: {table_name}")
    
    headers = get_airtable_headers()
    if not headers:
        return {
            "error": "AIRTABLE_PERSONAL_ACCESS_TOKEN is not configured. Please set it in your environment variables.",
            "status": "error"
        }
    
    # Prepare the request payload
    payload = {
        "name": table_name
    }
    
    if description:
        payload["description"] = description
    
    # Add fields if provided, otherwise use a default field
    if fields:
        payload["fields"] = fields
    else:
        payload["fields"] = [
            {"name": "Name", "type": "singleLineText"}
        ]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AIRTABLE_BASE_URL}/meta/bases/{base_id}/tables",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "table_id": result.get("id"),
                    "name": result.get("name"),
                    "description": result.get("description"),
                    "fields": result.get("fields", []),
                    "views": result.get("views", []),
                    "status": "success"
                }
            else:
                error_detail = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                return {
                    "error": f"Failed to create table. Status: {response.status_code}",
                    "details": error_detail,
                    "status": "error"
                }
                
    except Exception as e:
        print(f"ERROR: create_airtable_table failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def list_airtable_bases() -> Dict[str, Any]:
    """
    List all Airtable bases accessible with the current API key.
    
    Returns:
        Dictionary containing the list of bases and status
    """
    print("INFO: list_airtable_bases called")
    
    headers = get_airtable_headers()
    if not headers:
        return {
            "error": "AIRTABLE_PERSONAL_ACCESS_TOKEN is not configured. Please set it in your environment variables.",
            "status": "error"
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AIRTABLE_BASE_URL}/meta/bases",
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "bases": result.get("bases", []),
                    "offset": result.get("offset"),
                    "status": "success"
                }
            else:
                error_detail = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                return {
                    "error": f"Failed to list bases. Status: {response.status_code}",
                    "details": error_detail,
                    "status": "error"
                }
                
    except Exception as e:
        print(f"ERROR: list_airtable_bases failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def get_base_schema(base_id: str) -> Dict[str, Any]:
    """
    Get the schema (tables and fields) of an Airtable base.
    
    Args:
        base_id: ID of the base to get schema for (required)
    
    Returns:
        Dictionary containing the base schema and status
    """
    print(f"INFO: get_base_schema called with base_id: {base_id}")
    
    headers = get_airtable_headers()
    if not headers:
        return {
            "error": "AIRTABLE_PERSONAL_ACCESS_TOKEN is not configured. Please set it in your environment variables.",
            "status": "error"
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AIRTABLE_BASE_URL}/meta/bases/{base_id}/tables",
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "base_id": base_id,
                    "tables": result.get("tables", []),
                    "status": "success"
                }
            else:
                error_detail = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                return {
                    "error": f"Failed to get base schema. Status: {response.status_code}",
                    "details": error_detail,
                    "status": "error"
                }
                
    except Exception as e:
        print(f"ERROR: get_base_schema failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def create_base_with_template(
    name: str,
    template: str,
    workspace_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new Airtable base using a predefined template.
    
    Args:
        name: Name of the new base (required)
        template: Template type - "project_management", "crm", "inventory", "event_planning", "content_calendar" (required)
        workspace_id: ID of the workspace to create the base in (optional)
    
    Returns:
        Dictionary containing the created base information and status
    """
    print(f"INFO: create_base_with_template called with name: {name}, template: {template}")
    
    # Define template configurations
    templates = {
        "project_management": [
            {
                "name": "Projects",
                "description": "Track project progress and details",
                "fields": [
                    {"name": "Project Name", "type": "singleLineText"},
                    {"name": "Status", "type": "singleSelect", "options": {"choices": [
                        {"name": "Not Started", "color": "redBright"},
                        {"name": "In Progress", "color": "yellowBright"},
                        {"name": "Completed", "color": "greenBright"}
                    ]}},
                    {"name": "Start Date", "type": "date"},
                    {"name": "Due Date", "type": "date"},
                    {"name": "Assigned To", "type": "multipleSelectionFromRecord"},
                    {"name": "Priority", "type": "singleSelect", "options": {"choices": [
                        {"name": "High", "color": "redBright"},
                        {"name": "Medium", "color": "yellowBright"},
                        {"name": "Low", "color": "greenBright"}
                    ]}},
                    {"name": "Description", "type": "multilineText"}
                ]
            },
            {
                "name": "Tasks",
                "description": "Individual tasks within projects",
                "fields": [
                    {"name": "Task Name", "type": "singleLineText"},
                    {"name": "Project", "type": "multipleRecordLinks"},
                    {"name": "Status", "type": "singleSelect", "options": {"choices": [
                        {"name": "To Do", "color": "redBright"},
                        {"name": "In Progress", "color": "yellowBright"},
                        {"name": "Done", "color": "greenBright"}
                    ]}},
                    {"name": "Assigned To", "type": "singleLineText"},
                    {"name": "Due Date", "type": "date"},
                    {"name": "Notes", "type": "multilineText"}
                ]
            }
        ],
        "crm": [
            {
                "name": "Contacts",
                "description": "Customer and prospect information",
                "fields": [
                    {"name": "Full Name", "type": "singleLineText"},
                    {"name": "Company", "type": "singleLineText"},
                    {"name": "Email", "type": "email"},
                    {"name": "Phone", "type": "phoneNumber"},
                    {"name": "Status", "type": "singleSelect", "options": {"choices": [
                        {"name": "Lead", "color": "blueBright"},
                        {"name": "Prospect", "color": "yellowBright"},
                        {"name": "Customer", "color": "greenBright"}
                    ]}},
                    {"name": "Last Contact", "type": "date"},
                    {"name": "Notes", "type": "multilineText"}
                ]
            },
            {
                "name": "Deals",
                "description": "Sales opportunities and deals",
                "fields": [
                    {"name": "Deal Name", "type": "singleLineText"},
                    {"name": "Contact", "type": "multipleRecordLinks"},
                    {"name": "Value", "type": "currency"},
                    {"name": "Stage", "type": "singleSelect", "options": {"choices": [
                        {"name": "Prospecting", "color": "grayBright"},
                        {"name": "Qualification", "color": "blueBright"},
                        {"name": "Proposal", "color": "yellowBright"},
                        {"name": "Negotiation", "color": "orangeBright"},
                        {"name": "Closed Won", "color": "greenBright"},
                        {"name": "Closed Lost", "color": "redBright"}
                    ]}},
                    {"name": "Close Date", "type": "date"},
                    {"name": "Probability", "type": "percent"}
                ]
            }
        ],
        "inventory": [
            {
                "name": "Products",
                "description": "Product inventory tracking",
                "fields": [
                    {"name": "Product Name", "type": "singleLineText"},
                    {"name": "SKU", "type": "singleLineText"},
                    {"name": "Category", "type": "singleSelect", "options": {"choices": [
                        {"name": "Electronics", "color": "blueBright"},
                        {"name": "Clothing", "color": "purpleBright"},
                        {"name": "Home & Garden", "color": "greenBright"},
                        {"name": "Books", "color": "orangeBright"}
                    ]}},
                    {"name": "Current Stock", "type": "number"},
                    {"name": "Minimum Stock", "type": "number"},
                    {"name": "Unit Price", "type": "currency"},
                    {"name": "Supplier", "type": "singleLineText"},
                    {"name": "Last Restocked", "type": "date"}
                ]
            }
        ],
        "event_planning": [
            {
                "name": "Events",
                "description": "Event planning and management",
                "fields": [
                    {"name": "Event Name", "type": "singleLineText"},
                    {"name": "Date", "type": "date"},
                    {"name": "Location", "type": "singleLineText"},
                    {"name": "Status", "type": "singleSelect", "options": {"choices": [
                        {"name": "Planning", "color": "yellowBright"},
                        {"name": "Confirmed", "color": "greenBright"},
                        {"name": "Completed", "color": "blueBright"},
                        {"name": "Cancelled", "color": "redBright"}
                    ]}},
                    {"name": "Expected Attendees", "type": "number"},
                    {"name": "Budget", "type": "currency"},
                    {"name": "Notes", "type": "multilineText"}
                ]
            },
            {
                "name": "Tasks",
                "description": "Event planning tasks",
                "fields": [
                    {"name": "Task", "type": "singleLineText"},
                    {"name": "Event", "type": "multipleRecordLinks"},
                    {"name": "Assigned To", "type": "singleLineText"},
                    {"name": "Due Date", "type": "date"},
                    {"name": "Status", "type": "singleSelect", "options": {"choices": [
                        {"name": "Not Started", "color": "redBright"},
                        {"name": "In Progress", "color": "yellowBright"},
                        {"name": "Completed", "color": "greenBright"}
                    ]}},
                    {"name": "Priority", "type": "singleSelect", "options": {"choices": [
                        {"name": "High", "color": "redBright"},
                        {"name": "Medium", "color": "yellowBright"},
                        {"name": "Low", "color": "greenBright"}
                    ]}}
                ]
            }
        ],
        "content_calendar": [
            {
                "name": "Content",
                "description": "Content planning and scheduling",
                "fields": [
                    {"name": "Title", "type": "singleLineText"},
                    {"name": "Content Type", "type": "singleSelect", "options": {"choices": [
                        {"name": "Blog Post", "color": "blueBright"},
                        {"name": "Social Media", "color": "purpleBright"},
                        {"name": "Video", "color": "redBright"},
                        {"name": "Newsletter", "color": "greenBright"},
                        {"name": "Podcast", "color": "orangeBright"}
                    ]}},
                    {"name": "Status", "type": "singleSelect", "options": {"choices": [
                        {"name": "Idea", "color": "grayBright"},
                        {"name": "In Progress", "color": "yellowBright"},
                        {"name": "Review", "color": "orangeBright"},
                        {"name": "Scheduled", "color": "blueBright"},
                        {"name": "Published", "color": "greenBright"}
                    ]}},
                    {"name": "Publish Date", "type": "date"},
                    {"name": "Platform", "type": "multipleSelectionFromRecord"},
                    {"name": "Author", "type": "singleLineText"},
                    {"name": "Keywords", "type": "multipleSelectionFromRecord"},
                    {"name": "Description", "type": "multilineText"}
                ]
            }
        ]
    }
    
    if template not in templates:
        return {
            "error": f"Unknown template: {template}. Available templates: {', '.join(templates.keys())}",
            "status": "error"
        }
    
    # Create the base with the template tables
    return await create_airtable_base(
        name=name,
        workspace_id=workspace_id,
        tables=templates[template]
    )

def register(mcp_instance):
    """Register the Airtable tools with the MCP server"""
    mcp_instance.tool()(create_airtable_base)
    mcp_instance.tool()(create_airtable_table)
    mcp_instance.tool()(list_airtable_bases)
    mcp_instance.tool()(get_base_schema)
    mcp_instance.tool()(create_base_with_template)