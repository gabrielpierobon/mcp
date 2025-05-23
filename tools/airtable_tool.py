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

async def get_workspace_id_from_existing_base() -> str:
    """
    Get workspace ID from an existing base since there's no public API to list workspaces.
    """
    try:
        async with httpx.AsyncClient() as client:
            # List existing bases to get a workspace ID
            response = await client.get(
                f"{AIRTABLE_BASE_URL}/meta/bases",
                headers=get_airtable_headers(),
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                bases = result.get("bases", [])
                if bases:
                    # Try to get workspace info from the first base
                    # Note: This is a workaround since workspace listing isn't public
                    base_id = bases[0]["id"]
                    
                    # Get base schema which might include workspace info
                    schema_response = await client.get(
                        f"{AIRTABLE_BASE_URL}/meta/bases/{base_id}/tables",
                        headers=get_airtable_headers(),
                        timeout=30.0
                    )
                    
                    if schema_response.status_code == 200:
                        # For now, we'll return None and let Airtable create in default workspace
                        return None
                        
            return None
    except Exception:
        return None

async def create_airtable_base(
    name: str,
    workspace_id: Optional[str] = None,
    tables: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Create a new Airtable base with optional initial tables.
    
    Args:
        name: Name of the new base (required)
        workspace_id: ID of the workspace to create the base in (optional, will use default if not provided)
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
    
    # If no workspace_id provided, try to get one from existing bases
    if not workspace_id:
        workspace_id = await get_workspace_id_from_existing_base()
        if workspace_id:
            print(f"INFO: Using workspace_id from existing base: {workspace_id}")
        else:
            print("INFO: No workspace_id provided, will use default workspace")
    
    # Prepare the request payload
    payload = {
        "name": name
    }
    
    # Only add workspaceId if we have one
    if workspace_id:
        payload["workspaceId"] = workspace_id
    
    # Add initial tables if provided, otherwise create a default table
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
    else:
        # Add a default table if none provided
        payload["tables"] = [{
            "name": "Table 1",
            "fields": [
                {"name": "Name", "type": "singleLineText"}
            ]
        }]
    
    print(f"DEBUG: Payload being sent: {payload}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AIRTABLE_BASE_URL}/meta/bases",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            print(f"DEBUG: Response status: {response.status_code}")
            print(f"DEBUG: Response headers: {dict(response.headers)}")
            print(f"DEBUG: Response text: {response.text}")
            
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

async def list_records(
    base_id: str,
    table_name: str,
    fields: Optional[List[str]] = None,
    filter_formula: Optional[str] = None,
    max_records: Optional[int] = 100,
    sort: Optional[List[Dict[str, str]]] = None,
    view: Optional[str] = None
) -> Dict[str, Any]:
    """
    List records from a specific table in an Airtable base.
    
    Args:
        base_id: ID of the base (required)
        table_name: Name of the table (required)
        fields: List of field names to return (optional, returns all if not specified)
        filter_formula: Airtable formula to filter records (optional)
        max_records: Maximum number of records to return (default: 100, max: 100)
        sort: List of sort objects [{"field": "FieldName", "direction": "asc"}] (optional)
        view: Name of the view to use (optional)
    
    Returns:
        Dictionary containing the records and metadata
    """
    print(f"INFO: list_records called for base {base_id}, table {table_name}")
    
    headers = get_airtable_headers()
    if not headers:
        return {
            "error": "AIRTABLE_PERSONAL_ACCESS_TOKEN is not configured. Please set it in your environment variables.",
            "status": "error"
        }
    
    # Build query parameters
    params = {}
    
    if fields:
        for field in fields:
            params[f"fields[]"] = field
    
    if filter_formula:
        params["filterByFormula"] = filter_formula
    
    if max_records:
        params["maxRecords"] = min(max_records, 100)  # Airtable API limit
    
    if sort:
        for i, sort_obj in enumerate(sort):
            params[f"sort[{i}][field]"] = sort_obj.get("field", "")
            params[f"sort[{i}][direction]"] = sort_obj.get("direction", "asc")
    
    if view:
        params["view"] = view
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AIRTABLE_BASE_URL}/{base_id}/{table_name}",
                headers=headers,
                params=params,
                timeout=30.0
            )
            
            print(f"DEBUG: Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                records = result.get("records", [])
                
                # Format records for better readability
                formatted_records = []
                for record in records:
                    formatted_record = {
                        "id": record.get("id"),
                        "fields": record.get("fields", {}),
                        "createdTime": record.get("createdTime")
                    }
                    formatted_records.append(formatted_record)
                
                return {
                    "base_id": base_id,
                    "table_name": table_name,
                    "records": formatted_records,
                    "count": len(formatted_records),
                    "offset": result.get("offset"),
                    "filter_used": filter_formula,
                    "status": "success"
                }
            else:
                error_detail = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                return {
                    "error": f"Failed to list records. Status: {response.status_code}",
                    "details": error_detail,
                    "status": "error"
                }
                
    except Exception as e:
        print(f"ERROR: list_records failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def search_records(
    base_id: str,
    table_name: str,
    search_field: str,
    search_value: str,
    additional_fields: Optional[List[str]] = None,
    match_type: Optional[str] = "exact"
) -> Dict[str, Any]:
    """
    Search for records in a table by a specific field value.
    
    Args:
        base_id: ID of the base (required)
        table_name: Name of the table (required)
        search_field: Name of the field to search in (required)
        search_value: Value to search for (required)
        additional_fields: Additional fields to return in results (optional)
        match_type: Type of match - "exact", "contains", "starts_with" (default: "exact")
    
    Returns:
        Dictionary containing matching records
    """
    print(f"INFO: search_records called for {search_field}='{search_value}' in {table_name}")
    
    # Create filter formula based on match type
    if match_type == "exact":
        filter_formula = f"{{{search_field}}} = '{search_value}'"
    elif match_type == "contains":
        filter_formula = f"FIND('{search_value}', {{{search_field}}})"
    elif match_type == "starts_with":
        filter_formula = f"LEFT({{{search_field}}}, {len(search_value)}) = '{search_value}'"
    else:
        # Default to exact match
        filter_formula = f"{{{search_field}}} = '{search_value}'"
    
    # Include the search field plus any additional fields
    fields = [search_field]
    if additional_fields:
        fields.extend(additional_fields)
    
    return await list_records(
        base_id=base_id,
        table_name=table_name,
        fields=fields,
        filter_formula=filter_formula
    )

async def get_record_by_id(
    base_id: str,
    table_name: str,
    record_id: str
) -> Dict[str, Any]:
    """
    Get a specific record by its ID.
    
    Args:
        base_id: ID of the base (required)
        table_name: Name of the table (required)
        record_id: ID of the record to retrieve (required)
    
    Returns:
        Dictionary containing the record data
    """
    print(f"INFO: get_record_by_id called for record {record_id} in {table_name}")
    
    headers = get_airtable_headers()
    if not headers:
        return {
            "error": "AIRTABLE_PERSONAL_ACCESS_TOKEN is not configured. Please set it in your environment variables.",
            "status": "error"
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AIRTABLE_BASE_URL}/{base_id}/{table_name}/{record_id}",
                headers=headers,
                timeout=30.0
            )
            
            print(f"DEBUG: Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                return {
                    "base_id": base_id,
                    "table_name": table_name,
                    "record": {
                        "id": result.get("id"),
                        "fields": result.get("fields", {}),
                        "createdTime": result.get("createdTime")
                    },
                    "status": "success"
                }
            else:
                error_detail = response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
                return {
                    "error": f"Failed to get record. Status: {response.status_code}",
                    "details": error_detail,
                    "status": "error"
                }
                
    except Exception as e:
        print(f"ERROR: get_record_by_id failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def count_records(
    base_id: str,
    table_name: str,
    filter_formula: Optional[str] = None
) -> Dict[str, Any]:
    """
    Count records in a table, optionally with a filter.
    
    Args:
        base_id: ID of the base (required)
        table_name: Name of the table (required)
        filter_formula: Airtable formula to filter records (optional)
    
    Returns:
        Dictionary containing the record count
    """
    print(f"INFO: count_records called for table {table_name}")
    
    # Use list_records with maxRecords=1 to get count efficiently
    result = await list_records(
        base_id=base_id,
        table_name=table_name,
        fields=["Name"],  # Just get one field to minimize data transfer
        filter_formula=filter_formula,
        max_records=100  # Get sample to estimate
    )
    
    if result.get("status") == "success":
        return {
            "base_id": base_id,
            "table_name": table_name,
            "count": result.get("count", 0),
            "filter_used": filter_formula,
            "note": "Count based on first 100 records if table is larger",
            "status": "success"
        }
    else:
        return result

async def get_base_by_name(base_name: str) -> Dict[str, Any]:
    """
    Get base information by name instead of requiring the base ID.
    
    Args:
        base_name: Name of the base (e.g. "Storyteller", "mcp_test_base")
    
    Returns:
        Dictionary containing base ID and details
    """
    print(f"INFO: get_base_by_name called for '{base_name}'")
    
    # First get all bases
    bases_result = await list_airtable_bases()
    
    if bases_result.get("status") != "success":
        return bases_result
    
    # Find base by name (case-insensitive)
    bases = bases_result.get("bases", [])
    matching_base = None
    
    for base in bases:
        if base.get("name", "").lower() == base_name.lower():
            matching_base = base
            break
    
    if not matching_base:
        available_names = [base.get("name") for base in bases]
        return {
            "error": f"Base '{base_name}' not found",
            "available_bases": available_names,
            "status": "error"
        }
    
    return {
        "base_name": matching_base.get("name"),
        "base_id": matching_base.get("id"),
        "permission_level": matching_base.get("permissionLevel"),
        "status": "success"
    }

async def list_records_by_base_name(
    base_name: str,
    table_name: str,
    fields: Optional[List[str]] = None,
    filter_formula: Optional[str] = None,
    max_records: Optional[int] = 100,
    sort: Optional[List[Dict[str, str]]] = None,
    view: Optional[str] = None
) -> Dict[str, Any]:
    """
    List records using base name instead of base ID for easier usage.
    
    Args:
        base_name: Name of the base (e.g. "Storyteller")
        table_name: Name of the table
        fields: List of field names to return (optional)
        filter_formula: Airtable formula to filter records (optional)
        max_records: Maximum number of records to return (default: 100)
        sort: List of sort objects (optional)
        view: Name of the view to use (optional)
    
    Returns:
        Dictionary containing the records and metadata
    """
    print(f"INFO: list_records_by_base_name called for '{base_name}' table '{table_name}'")
    
    # Get base ID from name
    base_result = await get_base_by_name(base_name)
    
    if base_result.get("status") != "success":
        return base_result
    
    base_id = base_result.get("base_id")
    
    # Now get records using the validated base ID
    return await list_records(
        base_id=base_id,
        table_name=table_name,
        fields=fields,
        filter_formula=filter_formula,
        max_records=max_records,
        sort=sort,
        view=view
    )

async def validate_base_and_table(base_name: str, table_name: str) -> Dict[str, Any]:
    """
    Validate that a base exists and contains the specified table.
    
    Args:
        base_name: Name of the base
        table_name: Name of the table
    
    Returns:
        Dictionary with validation results and suggestions
    """
    print(f"INFO: validate_base_and_table called for '{base_name}' -> '{table_name}'")
    
    # Get base info
    base_result = await get_base_by_name(base_name)
    
    if base_result.get("status") != "success":
        return base_result
    
    base_id = base_result.get("base_id")
    
    # Get base schema to check if table exists
    schema_result = await get_base_schema(base_id)
    
    if schema_result.get("status") != "success":
        return schema_result
    
    # Check if table exists
    tables = schema_result.get("tables", [])
    table_names = [table.get("name") for table in tables]
    
    if table_name not in table_names:
        return {
            "error": f"Table '{table_name}' not found in base '{base_name}'",
            "available_tables": table_names,
            "base_id": base_id,
            "status": "error"
        }
    
    # Find the specific table
    target_table = None
    for table in tables:
        if table.get("name") == table_name:
            target_table = table
            break
    
    return {
        "base_name": base_name,
        "base_id": base_id,
        "table_name": table_name,
        "table_id": target_table.get("id") if target_table else None,
        "table_fields": [field.get("name") for field in target_table.get("fields", [])] if target_table else [],
        "validation": "success",
        "status": "success"
    }

async def search_records_by_base_name(
    base_name: str,
    table_name: str,
    search_field: str,
    search_value: str,
    additional_fields: Optional[List[str]] = None,
    match_type: Optional[str] = "exact"
) -> Dict[str, Any]:
    """
    Search records using base name for easier usage.
    
    Args:
        base_name: Name of the base (e.g. "Storyteller")
        table_name: Name of the table
        search_field: Name of the field to search in
        search_value: Value to search for
        additional_fields: Additional fields to return (optional)
        match_type: Type of match - "exact", "contains", "starts_with" (default: "exact")
    
    Returns:
        Dictionary containing matching records
    """
    print(f"INFO: search_records_by_base_name called for '{base_name}' -> '{table_name}'")
    
    # Get base ID from name
    base_result = await get_base_by_name(base_name)
    
    if base_result.get("status") != "success":
        return base_result
    
    base_id = base_result.get("base_id")
    
    # Now search records using the validated base ID
    return await search_records(
        base_id=base_id,
        table_name=table_name,
        search_field=search_field,
        search_value=search_value,
        additional_fields=additional_fields,
        match_type=match_type
    )

def register(mcp_instance):
    """Register the Airtable tools with the MCP server"""
    mcp_instance.tool()(create_airtable_base)
    mcp_instance.tool()(create_airtable_table)
    mcp_instance.tool()(list_airtable_bases)
    mcp_instance.tool()(get_base_schema)
    mcp_instance.tool()(create_base_with_template)
    mcp_instance.tool()(list_records)
    mcp_instance.tool()(search_records)
    mcp_instance.tool()(get_record_by_id)
    mcp_instance.tool()(count_records)
    mcp_instance.tool()(get_base_by_name)
    mcp_instance.tool()(list_records_by_base_name)
    mcp_instance.tool()(validate_base_and_table)
    mcp_instance.tool()(search_records_by_base_name)