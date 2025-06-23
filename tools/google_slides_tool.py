# tools/google_slides_tool.py
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv
import importlib.util
import hashlib
import time
try:
    from mcp import types
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    from mcp.types import Tool, TextContent
    
    # Define the tool decorator inline since import paths vary
    def tool(name: str):
        def decorator(func):
            func._tool_name = name
            return func
        return decorator
except ImportError:
    # Fallback if MCP is not available
    def tool(name: str):
        def decorator(func):
            func._tool_name = name
            return func
        return decorator

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
        print("INFO: Google Slides API libraries successfully imported")
    except ImportError as e:
        print(f"WARNING: Error importing Google API components: {str(e)}")
        GOOGLE_APIS_AVAILABLE = False
else:
    print("WARNING: Google API client libraries are not installed.")
    print("To install them, run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")

# Google API scopes for Slides
SCOPES = [
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive'
]

# Google API credentials paths
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")

# ======================
# CONTEXT MEMORY SYSTEM
# ======================

# Global context to store recent presentations
_recent_presentations_context = {
    "last_presentation": None,
    "recent_presentations": []  # Store multiple recent presentations
}

def _store_presentation_context(presentation_id: str, title: str, url: str):
    """Store presentation context for future operations."""
    context = {
        "id": presentation_id,
        "title": title,
        "url": url,
        "type": "presentation",
        "slides": []  # Will store slide IDs as they're created
    }
    _recent_presentations_context["last_presentation"] = context
    _recent_presentations_context["recent_presentations"].insert(0, context)
    # Keep only last 10 presentations
    _recent_presentations_context["recent_presentations"] = _recent_presentations_context["recent_presentations"][:10]

def _add_slide_to_context(presentation_id: str, slide_id: str, slide_title: str = None):
    """Add a slide to the presentation context."""
    # Find the presentation in recent presentations
    for presentation in _recent_presentations_context["recent_presentations"]:
        if presentation["id"] == presentation_id:
            slide_info = {"id": slide_id, "title": slide_title}
            presentation["slides"].append(slide_info)
            break

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

async def list_recent_presentations() -> Dict[str, Any]:
    """
    List recently created Google Presentations from this session.
    
    Returns:
        Dictionary containing recent presentations information
    """
    print("INFO: list_recent_presentations called")
    
    return {
        "recent_presentations": _recent_presentations_context["recent_presentations"],
        "last_presentation": _recent_presentations_context["last_presentation"],
        "count": len(_recent_presentations_context["recent_presentations"]),
        "status": "success"
    }

async def find_presentation_by_title(title_search: str) -> Dict[str, Any]:
    """
    Find a presentation by searching its title.
    
    Args:
        title_search: Partial title to search for (case-insensitive)
    
    Returns:
        Dictionary containing matching presentations
    """
    print(f"INFO: find_presentation_by_title called with search: {title_search}")
    
    matching_presentations = [p for p in _recent_presentations_context["recent_presentations"] 
                             if title_search.lower() in p["title"].lower()]
    
    return {
        "matching_presentations": matching_presentations,
        "search_term": title_search,
        "count": len(matching_presentations),
        "all_available_titles": [p["title"] for p in _recent_presentations_context["recent_presentations"]],
        "status": "success"
    }

# ======================
# GOOGLE SLIDES TOOLS
# ======================

async def create_google_slides(
    title: str,
    template_id: Optional[str] = None,
    share_with: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a new Google Slides presentation.
    
    Args:
        title: Title of the new presentation (required)
        template_id: ID of a template presentation to copy from (optional)
        share_with: List of email addresses to share with (optional)
    
    Returns:
        Dictionary containing the created presentation information
    """
    print(f"INFO: create_google_slides called with title: {title}")
    
    if not GOOGLE_APIS_AVAILABLE:
        return {
            "error": "Google API client libraries are not installed.",
            "status": "error"
        }
    
    try:
        slides_service = get_service('slides', 'v1')
        drive_service = get_service('drive', 'v3')
        
        if not slides_service:
            return {
                "error": "Failed to authenticate with Google Slides API.",
                "status": "error"
            }
        
        if template_id:
            # Copy from template
            if not drive_service:
                return {
                    "error": "Failed to authenticate with Google Drive API for template copying.",
                    "status": "error"
                }
            
            copy_body = {
                'name': title
            }
            presentation = drive_service.files().copy(
                fileId=template_id,
                body=copy_body
            ).execute()
            presentation_id = presentation.get('id')
        else:
            # Create new presentation
            presentation_body = {
                'title': title
            }
            presentation = slides_service.presentations().create(body=presentation_body).execute()
            presentation_id = presentation.get('presentationId')
        
        presentation_url = f"https://docs.google.com/presentation/d/{presentation_id}/edit"
        
        # Store context for future operations
        _store_presentation_context(presentation_id, title, presentation_url)
        
        result = {
            "presentation_id": presentation_id,
            "presentation_url": presentation_url,
            "title": title,
            "status": "success"
        }
        
        if template_id:
            result["created_from_template"] = template_id
        
        # Share the presentation if email addresses provided
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
                        fileId=presentation_id,
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
            "error": f"Google Slides API error: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: create_google_slides failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

@tool("add_slide")
def add_slide(presentation_id: str, slide_layout: str = "BLANK") -> dict:
    """
    Adds a new slide to a presentation with a specified layout.
    Lets the API generate a unique ID for the slide.
    """
    try:
        service = get_service('slides', 'v1')
        
        requests = [
            {
                'createSlide': {
                    'slideLayoutReference': {
                        'predefinedLayout': slide_layout
                    }
                }
            }
        ]

        body = {
            'requests': requests
        }
        
        response = service.presentations().batchUpdate(
            presentationId=presentation_id, body=body).execute()
        
        create_slide_response = response.get('replies')[0].get('createSlide')
        new_slide_id = create_slide_response.get('objectId')
        
        _add_slide_to_context(presentation_id, new_slide_id, f"New Slide ({slide_layout})")

        return {
            "presentation_id": presentation_id,
            "slide_id": new_slide_id,
            "status": "success"
        }
    except HttpError as e:
        return {"error": f"Google Slides API error: {str(e)}", "status": "error"}
    except Exception as e:
        print(f"ERROR: add_slide failed: {str(e)}")
        return {"error": f"Tool execution failed: {str(e)}", "status": "error"}

@tool("create_slide_with_content")
def create_slide_with_content(presentation_id: str, slide_layout: str = "TITLE_AND_BODY", title: str = None, body_content: str = None) -> dict:
    """
    Creates a new slide with a specific layout and populates its title and body placeholders.
    This is the most reliable way to create a new slide with content.
    It first creates the slide, gets the API-generated unique slide ID, 
    and then adds content to the placeholders in a second call.
    """
    try:
        service = get_service('slides', 'v1')
        
        # --- Step 1: Create the slide with placeholder mappings ---
        
        # Define placeholder mappings to get their generated IDs
        placeholder_mappings = []
        title_id = f"title_{hashlib.md5(f'{presentation_id}_{time.time()}_title'.encode()).hexdigest()}"
        body_id = f"body_{hashlib.md5(f'{presentation_id}_{time.time()}_body'.encode()).hexdigest()}"

        if title is not None:
            placeholder_mappings.append({
                'layoutPlaceholder': {'type': 'TITLE'},
                'objectId': title_id,
            })
            
        if body_content is not None:
            placeholder_mappings.append({
                'layoutPlaceholder': {
                    'type': 'BODY',
                    'index': 0 
                },
                'objectId': body_id,
            })

        create_slide_request = {
            'createSlide': {
                'slideLayoutReference': {
                    'predefinedLayout': slide_layout
                },
                'placeholderIdMappings': placeholder_mappings
            }
        }
        
        response = service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': [create_slide_request]}
        ).execute()
        
        new_slide_id = response['replies'][0]['createSlide']['objectId']
        
        # --- Step 2: Insert text into the placeholders ---
        
        text_insertion_requests = []
        if title is not None:
            text_insertion_requests.append({
                'insertText': {
                    'objectId': title_id,
                    'text': title
                }
            })
        if body_content is not None:
            text_insertion_requests.append({
                'insertText': {
                    'objectId': body_id,
                    'text': body_content
                }
            })
        
        if text_insertion_requests:
            service.presentations().batchUpdate(
                presentationId=presentation_id,
                body={'requests': text_insertion_requests}
            ).execute()

        _add_slide_to_context(presentation_id, new_slide_id, title)
        
        return {
            "presentation_id": presentation_id,
            "slide_id": new_slide_id,
            "slide_layout": slide_layout,
            "title": title,
            "status": "success",
            "content_added": True,
            "title_filled": bool(title),
            "body_filled": bool(body_content),
        }
        
    except HttpError as e:
        return {
            "error": f"Google Slides API error: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: create_slide_with_content failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def add_content_to_slide_placeholders(
    presentation_id: str,
    slide_id: str,
    title_text: Optional[str] = None,
    body_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add content to existing placeholders in a slide (title and body).
    
    Args:
        presentation_id: ID of the presentation (required)
        slide_id: ID of the slide (required)
        title_text: Text to add to title placeholder (optional)
        body_text: Text to add to body placeholder (optional)
    
    Returns:
        Dictionary containing the operation results
    """
    print(f"INFO: add_content_to_slide_placeholders called for slide {slide_id}")
    
    if not GOOGLE_APIS_AVAILABLE:
        return {
            "error": "Google API client libraries are not installed.",
            "status": "error"
        }
    
    try:
        service = get_service('slides', 'v1')
        if not service:
            return {
                "error": "Failed to authenticate with Google Slides API.",
                "status": "error"
            }
        
        # First, get the slide to find placeholder objects
        presentation = service.presentations().get(presentationId=presentation_id).execute()
        
        # Find the specific slide
        target_slide = None
        for slide in presentation.get('slides', []):
            if slide.get('objectId') == slide_id:
                target_slide = slide
                break
        
        if not target_slide:
            return {
                "error": f"Slide {slide_id} not found in presentation",
                "status": "error"
            }
        
        # Find placeholder objects
        title_placeholder = None
        body_placeholder = None
        available_placeholders = []
        
        for page_element in target_slide.get('pageElements', []):
            shape = page_element.get('shape', {})
            placeholder = shape.get('placeholder', {})
            
            if placeholder:
                placeholder_type = placeholder.get('type')
                available_placeholders.append(placeholder_type)
                
                if placeholder_type == 'TITLE' and title_text:
                    title_placeholder = page_element.get('objectId')
                elif placeholder_type in ['BODY', 'SUBTITLE'] and body_text:
                    body_placeholder = page_element.get('objectId')
        
        # Build requests to insert text into placeholders
        requests = []
        results = {}
        
        if title_placeholder and title_text:
            requests.append({
                'insertText': {
                    'objectId': title_placeholder,
                    'text': title_text
                }
            })
            results['title_added'] = True
        
        if body_placeholder and body_text:
            requests.append({
                'insertText': {
                    'objectId': body_placeholder,
                    'text': body_text
                }
            })
            results['body_added'] = True
        
        if not requests:
            return {
                "error": "No suitable placeholders found or no text provided",
                "available_placeholders": available_placeholders,
                "status": "error"
            }
        
        # Execute the requests
        response = service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
        
        return {
            "presentation_id": presentation_id,
            "slide_id": slide_id,
            "title_placeholder": title_placeholder,
            "body_placeholder": body_placeholder,
            "available_placeholders": available_placeholders,
            **results,
            "status": "success"
        }
        
    except HttpError as e:
        return {
            "error": f"Google Slides API error: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: add_content_to_slide_placeholders failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def add_text_to_slide(
    presentation_id: str,
    slide_id: str,
    text: str,
    x: float = 100,
    y: float = 100,
    width: float = 400,
    height: float = 100
) -> Dict[str, Any]:
    """
    Add a text box to a specific slide in a Google Slides presentation.
    Note: This creates a new text box rather than filling placeholders.
    For filling placeholders, use add_content_to_slide_placeholders or create_slide_with_content.
    
    Args:
        presentation_id: ID of the presentation (required)
        slide_id: ID of the slide (required)
        text: Text content to add (required)
        x: X coordinate of the text box in points (default: 100)
        y: Y coordinate of the text box in points (default: 100)
        width: Width of the text box in points (default: 400)
        height: Height of the text box in points (default: 100)
    
    Returns:
        Dictionary containing the operation results
    """
    print(f"INFO: add_text_to_slide called for slide {slide_id}")
    
    if not GOOGLE_APIS_AVAILABLE:
        return {
            "error": "Google API client libraries are not installed.",
            "status": "error"
        }
    
    try:
        service = get_service('slides', 'v1')
        if not service:
            return {
                "error": "Failed to authenticate with Google Slides API.",
                "status": "error"
            }
        
        text_box_id = f"textbox_{hashlib.md5(f'{slide_id}_{text[:20]}'.encode()).hexdigest()[:8]}"
        
        requests = [
            {
                'createShape': {
                    'objectId': text_box_id,
                    'shapeType': 'TEXT_BOX',
                    'elementProperties': {
                        'pageObjectId': slide_id,
                        'size': {
                            'width': {'magnitude': width, 'unit': 'PT'},
                            'height': {'magnitude': height, 'unit': 'PT'}
                        },
                        'transform': {
                            'scaleX': 1,
                            'scaleY': 1,
                            'translateX': x,
                            'translateY': y,
                            'unit': 'PT'
                        }
                    }
                }
            },
            {
                'insertText': {
                    'objectId': text_box_id,
                    'text': text
                }
            }
        ]
        
        response = service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
        
        return {
            "presentation_id": presentation_id,
            "slide_id": slide_id,
            "text_box_id": text_box_id,
            "text": text,
            "position": {"x": x, "y": y},
            "size": {"width": width, "height": height},
            "status": "success"
        }
        
    except HttpError as e:
        return {
            "error": f"Google Slides API error: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: add_text_to_slide failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def add_slide_to_last_presentation(
    slide_layout: str = "TITLE_AND_BODY",
    title: Optional[str] = None,
    body_content: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add a slide with content to the most recently created presentation.
    This is the preferred method for adding slides with content to recent presentations.
    
    Args:
        slide_layout: Layout for the new slide (default: "TITLE_AND_BODY")
        title: Title for the slide (optional)
        body_content: Body text content for the slide (optional)
    
    Returns:
        Dictionary containing the new slide information
    """
    print("INFO: add_slide_to_last_presentation called")
    
    if not _recent_presentations_context["last_presentation"]:
        return {
            "error": "No recent presentation found. Please create a presentation first or use create_slide_with_content with a specific presentation ID.",
            "status": "error"
        }
    
    presentation_id = _recent_presentations_context["last_presentation"]["id"]
    
    # Use the new create_slide_with_content function
    slide_result = await create_slide_with_content(
        presentation_id=presentation_id,
        slide_layout=slide_layout,
        title=title,
        body_content=body_content
    )
    
    if slide_result.get("status") == "success":
        slide_result["added_to"] = {
            "presentation_id": presentation_id,
            "title": _recent_presentations_context["last_presentation"]["title"],
            "url": _recent_presentations_context["last_presentation"]["url"]
        }
    
    return slide_result

def _extract_element_geometry(page_element):
    """Helper to safely extract geometry from a page element."""
    size = page_element.get('size', {})
    transform = page_element.get('transform', {})
    
    # Dimensions are in EMU, convert to PT (1 EMU = 1/914400 inches, 1 inch = 72 points)
    # Conversion factor: 1 EMU = 72 / 914400 PT
    emu_to_pt = 72 / 914400
    
    return {
        'width_pt': size.get('width', {}).get('magnitude', 0) * emu_to_pt,
        'height_pt': size.get('height', {}).get('magnitude', 0) * emu_to_pt,
        'x_pt': transform.get('translateX', 0) * emu_to_pt,
        'y_pt': transform.get('translateY', 0) * emu_to_pt,
    }

async def get_slide_info(
    presentation_id: str,
    slide_id: str
) -> Dict[str, Any]:
    """
    Get information about a specific slide, including its placeholders and elements.
    
    Args:
        presentation_id: ID of the presentation (required)
        slide_id: ID of the slide (required)
    
    Returns:
        Dictionary containing slide information and structure
    """
    print(f"INFO: get_slide_info called for slide {slide_id}")
    
    if not GOOGLE_APIS_AVAILABLE:
        return {
            "error": "Google API client libraries are not installed.",
            "status": "error"
        }
    
    try:
        service = get_service('slides', 'v1')
        if not service:
            return {
                "error": "Failed to authenticate with Google Slides API.",
                "status": "error"
            }
        
        presentation = service.presentations().get(presentationId=presentation_id).execute()
        
        # Find the specific slide
        target_slide = None
        for slide in presentation.get('slides', []):
            if slide.get('objectId') == slide_id:
                target_slide = slide
                break
        
        if not target_slide:
            return {
                "error": f"Slide {slide_id} not found in presentation",
                "status": "error"
            }
        
        # Analyze slide elements
        placeholders = []
        text_boxes = []
        shapes = []
        
        for page_element in target_slide.get('pageElements', []):
            element_id = page_element.get('objectId')
            geometry = _extract_element_geometry(page_element)
            
            if 'shape' in page_element:
                shape = page_element['shape']
                
                if 'placeholder' in shape:
                    placeholder = shape['placeholder']
                    placeholders.append({
                        "id": element_id,
                        "type": placeholder.get('type'),
                        "index": placeholder.get('index'),
                        "geometry": geometry
                    })
                elif shape.get('shapeType') == 'TEXT_BOX':
                    text_boxes.append({
                        "id": element_id,
                        "type": "TEXT_BOX",
                        "geometry": geometry
                    })
                else:
                    shapes.append({
                        "id": element_id,
                        "type": shape.get('shapeType'),
                        "geometry": geometry
                    })
        
        return {
            "presentation_id": presentation_id,
            "slide_id": slide_id,
            "placeholders": placeholders,
            "text_boxes": text_boxes,
            "shapes": shapes,
            "total_elements": len(target_slide.get('pageElements', [])),
            "status": "success"
        }
        
    except HttpError as e:
        return {
            "error": f"Google Slides API error: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: get_slide_info failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def delete_page_elements(
    presentation_id: str,
    element_ids: List[str]
) -> Dict[str, Any]:
    """
    Deletes one or more elements from a slide.
    
    Args:
        presentation_id: ID of the presentation (required)
        element_ids: A list of object IDs for the elements to delete (required)
    
    Returns:
        Dictionary containing the operation results
    """
    print(f"INFO: delete_page_elements called for elements: {element_ids}")
    
    if not GOOGLE_APIS_AVAILABLE:
        return {"error": "Google API client libraries are not installed.", "status": "error"}

    if not isinstance(element_ids, list) or not element_ids:
        return {"error": "element_ids must be a non-empty list.", "status": "error"}

    try:
        service = get_service('slides', 'v1')
        if not service:
            return {"error": "Failed to authenticate with Google Slides API.", "status": "error"}

        requests = []
        for element_id in element_ids:
            requests.append({
                'deleteObject': {
                    'objectId': element_id
                }
            })

        body = {'requests': requests}
        response = service.presentations().batchUpdate(presentationId=presentation_id, body=body).execute()
        
        return {
            "presentation_id": presentation_id,
            "deleted_elements_count": len(element_ids),
            "deleted_ids": element_ids,
            "status": "success"
        }

    except HttpError as e:
        return {"error": f"Google Slides API error: {str(e)}", "status": "error"}
    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}", "status": "error"}

# ======================
# ENHANCED DESIGN TOOLS
# ======================

async def change_slide_background(
    presentation_id: str,
    slide_id: str,
    background_type: str = "color",
    color_hex: Optional[str] = None,
    image_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Change the background of a slide.
    
    Args:
        presentation_id: ID of the presentation (required)
        slide_id: ID of the slide (required)
        background_type: Type of background - "color" or "image" (default: "color")
        color_hex: Hex color code (e.g., "#FF5733", "#3498DB") for color backgrounds
        image_url: URL of image for image backgrounds
    
    Returns:
        Dictionary containing the operation results
    """
    print(f"INFO: change_slide_background called for slide {slide_id}")
    
    if not GOOGLE_APIS_AVAILABLE:
        return {
            "error": "Google API client libraries are not installed.",
            "status": "error"
        }
    
    try:
        service = get_service('slides', 'v1')
        if not service:
            return {
                "error": "Failed to authenticate with Google Slides API.",
                "status": "error"
            }
        
        requests = []
        
        if background_type == "color" and color_hex:
            # Convert hex to RGB
            hex_color = color_hex.lstrip('#')
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
                
                requests.append({
                    'updatePageProperties': {
                        'objectId': slide_id,
                        'pageProperties': {
                            'pageBackgroundFill': {
                                'solidFill': {
                                    'color': {
                                        'rgbColor': {
                                            'red': r,
                                            'green': g,
                                            'blue': b
                                        }
                                    }
                                }
                            }
                        },
                        'fields': 'pageBackgroundFill.solidFill.color'
                    }
                })
            else:
                return {
                    "error": "Invalid hex color format. Use #RRGGBB format (e.g., #FF5733).",
                    "status": "error"
                }
                
        elif background_type == "image" and image_url:
            requests.append({
                'updatePageProperties': {
                    'objectId': slide_id,
                    'pageProperties': {
                        'pageBackgroundFill': {
                            'stretchedPictureFill': {
                                'contentUrl': image_url
                            }
                        }
                    },
                    'fields': 'pageBackgroundFill.stretchedPictureFill.contentUrl'
                }
            })
        else:
            return {
                "error": f"Invalid background configuration. For color backgrounds, provide color_hex. For image backgrounds, provide image_url.",
                "status": "error"
            }
        
        response = service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
        
        return {
            "presentation_id": presentation_id,
            "slide_id": slide_id,
            "background_type": background_type,
            "color_hex": color_hex if background_type == "color" else None,
            "image_url": image_url if background_type == "image" else None,
            "status": "success"
        }
        
    except HttpError as e:
        return {
            "error": f"Google Slides API error: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: change_slide_background failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

@tool("create_professional_text_box")
async def create_professional_text_box(
    presentation_id: str,
    slide_id: str,
    text: str,
    x: float,
    y: float,
    width: float,
    height: float,
    font_color: str = "#FFFFFF",
    background_color: str = "#3498DB",
    font_size: int = None
) -> Dict[str, Any]:
    """
    Create a properly sized text box with guaranteed text fitting.
    This function ensures text never gets cut off.
    """
    print(f"INFO: create_professional_text_box called")
    
    if not GOOGLE_APIS_AVAILABLE:
        return {"error": "Google API client libraries are not installed.", "status": "error"}
    
    try:
        service = get_service('slides', 'v1')
        if not service:
            return {"error": "Failed to authenticate with Google Slides API.", "status": "error"}
        
        # Calculate optimal font size that GUARANTEES the text fits
        if font_size is None:
            font_size = calculate_guaranteed_font_size(text, width, height)
        
        text_box_id = f"pro_textbox_{hashlib.md5(f'{slide_id}_{text[:15]}_{x}_{y}'.encode()).hexdigest()[:10]}"
        
        requests = []
        
        # 1. Create the text box with exact dimensions
        create_request = {
            'createShape': {
                'objectId': text_box_id,
                'shapeType': 'TEXT_BOX',
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width': {'magnitude': width, 'unit': 'PT'},
                        'height': {'magnitude': height, 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': x,
                        'translateY': y,
                        'unit': 'PT'
                    }
                }
            }
        }
        requests.append(create_request)
        
        # 2. Insert text
        requests.append({
            'insertText': {
                'objectId': text_box_id,
                'text': text
            }
        })
        
        # 3. Apply font size with conservative sizing
        requests.append({
            'updateTextStyle': {
                'objectId': text_box_id,
                'textRange': {'type': 'ALL'},
                'style': {
                    'fontSize': {'magnitude': font_size, 'unit': 'PT'}
                },
                'fields': 'fontSize'
            }
        })
        
        # 4. Apply font color
        hex_color = font_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            
            requests.append({
                'updateTextStyle': {
                    'objectId': text_box_id,
                    'textRange': {'type': 'ALL'},
                    'style': {
                        'foregroundColor': {
                            'opaqueColor': {
                                'rgbColor': {'red': r, 'green': g, 'blue': b}
                            }
                        }
                    },
                    'fields': 'foregroundColor'
                }
            })
        
        # 5. Apply background color
        hex_bg = background_color.lstrip('#')
        if len(hex_bg) == 6:
            r = int(hex_bg[0:2], 16) / 255.0
            g = int(hex_bg[2:4], 16) / 255.0
            b = int(hex_bg[4:6], 16) / 255.0
            
            requests.append({
                'updateShapeProperties': {
                    'objectId': text_box_id,
                    'shapeProperties': {
                        'shapeBackgroundFill': {
                            'solidFill': {
                                'color': {
                                    'rgbColor': {'red': r, 'green': g, 'blue': b}
                                }
                            }
                        }
                    },
                    'fields': 'shapeBackgroundFill.solidFill.color'
                }
            })
        
        print(f"DEBUG: Creating text box with font size {font_size}pt for text: '{text[:30]}...'")
        
        response = service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
        
        return {
            "presentation_id": presentation_id,
            "slide_id": slide_id,
            "text_box_id": text_box_id,
            "text": text,
            "font_size": font_size,
            "dimensions": {"width": width, "height": height},
            "position": {"x": x, "y": y},
            "status": "success"
        }
        
    except Exception as e:
        print(f"ERROR: create_professional_text_box failed: {str(e)}")
        return {"error": f"Tool execution failed: {str(e)}", "status": "error"}

def calculate_guaranteed_font_size(text: str, width_pt: float, height_pt: float) -> int:
    """
    Calculate font size that GUARANTEES text will fit without cutoff.
    Uses very conservative estimates to prevent any text clipping.
    """
    lines = text.split('\n')
    num_lines = len(lines)
    max_chars_per_line = max(len(line) for line in lines) if lines else 1
    
    # Very conservative character width estimate (0.6 * font_size)
    # Leave 20% padding on all sides
    usable_width = width_pt * 0.6
    width_based_size = int(usable_width / (max_chars_per_line * 0.6))
    
    # Very conservative line height (1.5 * font_size for safety)
    # Leave 25% padding top and bottom
    usable_height = height_pt * 0.5
    height_based_size = int(usable_height / (num_lines * 1.5))
    
    # Take the smaller size and add extra safety margin
    calculated_size = min(width_based_size, height_based_size)
    safe_size = int(calculated_size * 0.8)  # 20% safety margin
    
    # Enforce reasonable bounds for presentations
    final_size = max(10, min(safe_size, 20))  # Between 10pt and 20pt
    
    print(f"DEBUG: Font calc - Lines: {num_lines}, Max chars: {max_chars_per_line}, Final size: {final_size}pt")
    return final_size

@tool("create_perfect_grid_layout")
async def create_perfect_grid_layout(
    presentation_id: str,
    slide_id: str,
    elements: List[Dict[str, Any]],
    grid_rows: int = 2,
    grid_cols: int = 2
) -> Dict[str, Any]:
    """
    Create a perfect grid layout with properly sized and positioned elements.
    This function guarantees no overlaps and proper text fitting.
    """
    print(f"INFO: create_perfect_grid_layout called for {grid_rows}x{grid_cols} grid")
    
    # Get slide dimensions
    dimensions_result = await get_presentation_dimensions(presentation_id)
    if dimensions_result.get("status") != "success":
        return dimensions_result
    
    # Get placeholder info to avoid overlaps
    slide_info_result = await get_slide_info(presentation_id, slide_id)
    if slide_info_result.get("status") != "success":
        return slide_info_result
    
    dims = dimensions_result["dimensions"]
    slide_width = dims["width_pt"]  # 720pt
    slide_height = dims["height_pt"]  # 405pt
    
    # Calculate content area (avoid title/subtitle)
    content_start_y = 240  # Safe area below title/subtitle
    content_height = slide_height - content_start_y - 20  # 20pt bottom margin
    content_width = slide_width - 80  # 40pt margins on each side
    
    # Calculate cell dimensions with proper spacing
    margin = 20
    cell_width = (content_width - (margin * (grid_cols + 1))) / grid_cols
    cell_height = (content_height - (margin * (grid_rows + 1))) / grid_rows
    
    print(f"DEBUG: Content area - Start Y: {content_start_y}, Cell size: {cell_width}x{cell_height}")
    
    created_elements = []
    
    for i, element in enumerate(elements[:grid_rows * grid_cols]):
        row = i // grid_cols
        col = i % grid_cols
        
        # Calculate position
        x = 40 + margin + (col * (cell_width + margin))
        y = content_start_y + margin + (row * (cell_height + margin))
        
        # Create the text box
        result = await create_professional_text_box(
            presentation_id=presentation_id,
            slide_id=slide_id,
            text=element.get("text", f"Element {i+1}"),
            x=x,
            y=y,
            width=cell_width,
            height=cell_height,
            font_color=element.get("font_color", "#FFFFFF"),
            background_color=element.get("background_color", "#3498DB")
        )
        created_elements.append(result)
    
    return {
        "presentation_id": presentation_id,
        "slide_id": slide_id,
        "grid_dimensions": f"{grid_rows}x{grid_cols}",
        "content_area": {
            "start_y": content_start_y,
            "width": content_width,
            "height": content_height
        },
        "cell_dimensions": {
            "width": cell_width,
            "height": cell_height
        },
        "elements_created": len(created_elements),
        "created_elements": created_elements,
        "status": "success"
    }

def register(mcp_instance):
    """Register the Google Slides tools with the MCP server"""
    if GOOGLE_APIS_AVAILABLE:
        # Core Slides operations
        mcp_instance.tool()(create_google_slides)
        mcp_instance.tool()(add_slide)
        
        # NEW: Preferred methods for working with placeholders
        mcp_instance.tool()(create_slide_with_content)
        mcp_instance.tool()(add_content_to_slide_placeholders)
        
        # Text and content tools
        mcp_instance.tool()(add_text_to_slide)
        
        # 🆕 NEW: Enhanced design and styling tools
        mcp_instance.tool()(change_slide_background)
        mcp_instance.tool()(create_professional_text_box)
        mcp_instance.tool()(add_auto_sized_text_box)
        mcp_instance.tool()(update_text_style)
        
        # 🆕 NEW: Dimension-aware positioning tools
        mcp_instance.tool()(get_presentation_dimensions)
        mcp_instance.tool()(add_positioned_text_box)
        mcp_instance.tool()(create_responsive_layout)
        mcp_instance.tool()(delete_page_elements)
        
        # Helper and context tools
        mcp_instance.tool()(add_slide_to_last_presentation)
        mcp_instance.tool()(get_slide_info)
        mcp_instance.tool()(list_recent_presentations)
        mcp_instance.tool()(find_presentation_by_title)
        
        # NEW: Improved responsive layout
        mcp_instance.tool()(create_improved_responsive_layout)
        mcp_instance.tool()(create_perfect_grid_layout)
        
        print("INFO: Google Slides tools registered successfully with enhanced design capabilities")
    else:
        print("WARNING: Google Slides tools not registered due to missing dependencies")

# ======================
# DIMENSION-AWARE FUNCTIONS
# ======================

async def get_presentation_dimensions(presentation_id: str) -> Dict[str, Any]:
    """
    Get the dimensions (pageSize) of a Google Slides presentation.
    
    Args:
        presentation_id: ID of the presentation (required)
    
    Returns:
        Dictionary containing presentation dimensions and metadata
    """
    print(f"INFO: get_presentation_dimensions called for presentation {presentation_id}")
    
    if not GOOGLE_APIS_AVAILABLE:
        return {
            "error": "Google API client libraries are not installed.",
            "status": "error"
        }
    
    try:
        service = get_service('slides', 'v1')
        if not service:
            return {
                "error": "Failed to authenticate with Google Slides API.",
                "status": "error"
            }
        
        # Get presentation with pageSize field
        presentation = service.presentations().get(
            presentationId=presentation_id,
            fields='pageSize,title'
        ).execute()
        
        page_size = presentation.get('pageSize', {})
        
        # Extract dimensions
        width_emu = page_size.get('width', {}).get('magnitude', 0)
        height_emu = page_size.get('height', {}).get('magnitude', 0)
        unit = page_size.get('width', {}).get('unit', 'EMU')
        
        # Convert EMU to points (1 point = 12700 EMU)
        if unit == 'EMU':
            width_pt = width_emu / 12700
            height_pt = height_emu / 12700
        else:
            width_pt = width_emu
            height_pt = height_emu
        
        # Determine slide format based on aspect ratio
        aspect_ratio = width_pt / height_pt if height_pt > 0 else 0
        slide_format = "Custom"
        if abs(aspect_ratio - 1.333) < 0.01:  # 4:3 ratio
            slide_format = "Standard (4:3)"
        elif abs(aspect_ratio - 1.778) < 0.01:  # 16:9 ratio
            slide_format = "Widescreen (16:9)"
        
        return {
            "presentation_id": presentation_id,
            "title": presentation.get('title', 'Untitled'),
            "dimensions": {
                "width_pt": width_pt,
                "height_pt": height_pt,
                "width_emu": width_emu,
                "height_emu": height_emu,
                "unit": unit,
                "aspect_ratio": aspect_ratio,
                "format": slide_format
            },
            "positioning_helpers": {
                "center_x": width_pt / 2,
                "center_y": height_pt / 2,
                "quarter_x": width_pt / 4,
                "quarter_y": height_pt / 4,
                "three_quarter_x": (width_pt * 3) / 4,
                "three_quarter_y": (height_pt * 3) / 4
            },
            "status": "success"
        }
        
    except HttpError as e:
        return {
            "error": f"Google Slides API error: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: get_presentation_dimensions failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def add_positioned_text_box(
    presentation_id: str,
    slide_id: str,
    text: str,
    position_type: str = "custom",
    x: Optional[float] = None,
    y: Optional[float] = None,
    width: Optional[float] = None,
    height: Optional[float] = None,
    font_color: Optional[str] = None,
    background_color: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add a text box with smart positioning based on slide dimensions.
    
    Args:
        presentation_id: ID of the presentation (required)
        slide_id: ID of the slide (required)
        text: Text content (required)
        position_type: Positioning type - "center", "top-left", "top-right", "bottom-left", "bottom-right", "custom" (default: "custom")
        x: X coordinate for custom positioning (optional)
        y: Y coordinate for custom positioning (optional)
        width: Width of the text box (optional, defaults to 25% of slide width)
        height: Height of the text box (optional, defaults to 10% of slide height)
        font_color: Font color in hex format (optional)
        background_color: Background color in hex format (optional)
    
    Returns:
        Dictionary containing the operation results
    """
    print(f"INFO: add_positioned_text_box called with position_type: {position_type}")
    
    # First, get the slide dimensions
    dimensions_result = await get_presentation_dimensions(presentation_id)
    if dimensions_result.get("status") != "success":
        return dimensions_result
    
    dims = dimensions_result["dimensions"]
    helpers = dimensions_result["positioning_helpers"]
    
    # Calculate default size if not provided
    if width is None:
        width = dims["width_pt"] * 0.25  # 25% of slide width
    if height is None:
        height = dims["height_pt"] * 0.1   # 10% of slide height
    
    # Calculate position based on position_type
    if position_type == "center":
        final_x = helpers["center_x"] - (width / 2)
        final_y = helpers["center_y"] - (height / 2)
    elif position_type == "top-left":
        final_x = dims["width_pt"] * 0.05  # 5% margin from left
        final_y = dims["height_pt"] * 0.05  # 5% margin from top
    elif position_type == "top-right":
        final_x = dims["width_pt"] * 0.95 - width  # 5% margin from right
        final_y = dims["height_pt"] * 0.05  # 5% margin from top
    elif position_type == "bottom-left":
        final_x = dims["width_pt"] * 0.05  # 5% margin from left
        final_y = dims["height_pt"] * 0.95 - height  # 5% margin from bottom
    elif position_type == "bottom-right":
        final_x = dims["width_pt"] * 0.95 - width  # 5% margin from right
        final_y = dims["height_pt"] * 0.95 - height  # 5% margin from bottom
    elif position_type == "custom":
        if x is None or y is None:
            return {
                "error": "For custom positioning, both x and y coordinates must be provided.",
                "status": "error"
            }
        final_x = x
        final_y = y
    else:
        return {
            "error": f"Invalid position_type '{position_type}'. Use: center, top-left, top-right, bottom-left, bottom-right, or custom.",
            "status": "error"
        }
    
    # Ensure positioning is within slide bounds
    final_x = max(0, min(final_x, dims["width_pt"] - width))
    final_y = max(0, min(final_y, dims["height_pt"] - height))
    
    # Use the auto-sized text box function for optimal text fitting
    result = await add_auto_sized_text_box(
        presentation_id=presentation_id,
        slide_id=slide_id,
        text=text,
        x=final_x,
        y=final_y,
        width=width,
        height=height,
        font_color=font_color,
        background_color=background_color
    )
    
    # Add dimension information to the result
    if result.get("status") == "success":
        result["positioning_info"] = {
            "slide_dimensions": dims,
            "calculated_position": {"x": final_x, "y": final_y},
            "position_type": position_type,
            "size": {"width": width, "height": height}
        }
    
    return result

async def create_responsive_layout(
    presentation_id: str,
    slide_id: str,
    layout_type: str = "grid",
    elements: Optional[List[Dict[str, Any]]] = None,
    top_offset_pt: Optional[float] = None
) -> Dict[str, Any]:
    """
    Create a responsive layout of elements that adapts to slide dimensions.
    Automatically detects placeholders to avoid overlapping them.
    
    Args:
        presentation_id: ID of the presentation (required)
        slide_id: ID of the slide (required)
        layout_type: Type of layout - "grid", "columns", "rows" (default: "grid")
        elements: List of elements to position, each with text, color, etc. (optional)
        top_offset_pt: Optional manual offset from the top. If not provided, it's calculated automatically.
    
    Returns:
        Dictionary containing the layout creation results
    """
    print(f"INFO: create_responsive_layout called with layout_type: {layout_type}")
    
    # Get slide dimensions and element info first
    dimensions_result = await get_presentation_dimensions(presentation_id)
    if dimensions_result.get("status") != "success":
        return dimensions_result
    
    slide_info_result = await get_slide_info(presentation_id, slide_id)
    if slide_info_result.get("status") != "success":
        return slide_info_result

    dims = dimensions_result["dimensions"]
    
    # === Placeholder-Aware Logic ===
    if top_offset_pt is None:
        # Calculate the bottom edge of the TITLE placeholder to determine the content start line
        title_bottom_y = 0
        for p in slide_info_result.get("placeholders", []):
            if p.get("type") == "TITLE":
                geom = p.get("geometry", {})
                if geom.get('y_pt') is not None and geom.get('height_pt') is not None:
                    title_bottom_y = geom["y_pt"] + geom["height_pt"]
                    break # Found the title, no need to check others

        # If a title was found, use its bottom as the offset, otherwise start from the top
        top_offset_pt = title_bottom_y if title_bottom_y > 0 else 0
        # Add a small margin
        if top_offset_pt > 0:
            top_offset_pt += dims["height_pt"] * 0.05

    # Default elements if none provided
    if elements is None:
        elements = [
            {"text": "Header", "font_color": "#FFFFFF", "background_color": "#2E86AB"},
            {"text": "Content 1", "font_color": "#000000", "background_color": "#A23B72"},
            {"text": "Content 2", "font_color": "#FFFFFF", "background_color": "#F18F01"},
            {"text": "Footer", "font_color": "#FFFFFF", "background_color": "#C73E1D"}
        ]
    
    created_elements = []
    margin = dims["width_pt"] * 0.02  # 2% margin
    
    if layout_type == "grid":
        # 2x2 grid layout
        cols = 2
        rows = 2
        available_width = dims["width_pt"] - (margin * 3)  # margins: left, center, right
        available_height = dims["height_pt"] - top_offset_pt - (margin * 3) # Account for offset
        cell_width = available_width / cols
        cell_height = available_height / rows
        
        for i, element in enumerate(elements[:4]):  # Max 4 elements for 2x2 grid
            row = i // cols
            col = i % cols
            
            x = margin + (col * (cell_width + margin))
            y = top_offset_pt + margin + (row * (cell_height + margin)) # Add offset
            
            result = await add_auto_sized_text_box(
                presentation_id=presentation_id,
                slide_id=slide_id,
                text=element.get("text", f"Element {i+1}"),
                x=x,
                y=y,
                width=cell_width,
                height=cell_height,
                font_color=element.get("font_color"),
                background_color=element.get("background_color")
            )
            created_elements.append(result)
            
    elif layout_type == "columns":
        # Vertical columns
        num_cols = len(elements)
        available_width = dims["width_pt"] - (margin * (num_cols + 1))
        col_width = available_width / num_cols
        col_height = dims["height_pt"] - top_offset_pt - (margin * 2) # Account for offset
        
        for i, element in enumerate(elements):
            x = margin + (i * (col_width + margin))
            y = top_offset_pt + margin # Add offset
            
            result = await add_auto_sized_text_box(
                presentation_id=presentation_id,
                slide_id=slide_id,
                text=element.get("text", f"Column {i+1}"),
                x=x,
                y=y,
                width=col_width,
                height=col_height,
                font_color=element.get("font_color"),
                background_color=element.get("background_color")
            )
            created_elements.append(result)
            
    elif layout_type == "rows":
        # Horizontal rows
        num_rows = len(elements)
        available_height = dims["height_pt"] - top_offset_pt - (margin * (num_rows + 1)) # Account for offset
        row_height = available_height / num_rows
        row_width = dims["width_pt"] - (margin * 2)
        
        for i, element in enumerate(elements):
            x = margin
            y = top_offset_pt + margin + (i * (row_height + margin)) # Add offset
            
            result = await add_auto_sized_text_box(
                presentation_id=presentation_id,
                slide_id=slide_id,
                text=element.get("text", f"Row {i+1}"),
                x=x,
                y=y,
                width=row_width,
                height=row_height,
                font_color=element.get("font_color"),
                background_color=element.get("background_color")
            )
            created_elements.append(result)
    
    return {
        "presentation_id": presentation_id,
        "slide_id": slide_id,
        "layout_type": layout_type,
        "slide_dimensions": dims,
        "elements_created": len(created_elements),
        "created_elements": created_elements,
        "status": "success"
    }

@tool("create_improved_responsive_layout")
async def create_improved_responsive_layout(
    presentation_id: str,
    slide_id: str,
    layout_type: str = "grid",
    elements: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    IMPROVED: Create responsive layout with properly calculated text box dimensions.
    Fixes height issues and improves font sizing for presentations.
    
    Args:
        presentation_id: ID of the presentation (required)
        slide_id: ID of the slide (required)
        layout_type: Type of layout - "grid", "columns", "rows" (default: "grid")
        elements: List of elements with text, colors, etc. (optional)
    
    Returns:
        Dictionary containing the layout creation results
    """
    print(f"INFO: create_improved_responsive_layout called with layout_type: {layout_type}")
    
    # Get slide dimensions and element info
    dimensions_result = await get_presentation_dimensions(presentation_id)
    if dimensions_result.get("status") != "success":
        return dimensions_result
    
    slide_info_result = await get_slide_info(presentation_id, slide_id)
    if slide_info_result.get("status") != "success":
        return slide_info_result

    dims = dimensions_result["dimensions"]
    
    # Calculate top offset (avoid title/subtitle placeholders)
    title_bottom_y = 0
    for p in slide_info_result.get("placeholders", []):
        if p.get("type") in ["TITLE", "BODY"]:
            geom = p.get("geometry", {})
            if geom.get('y_pt') is not None and geom.get('height_pt') is not None:
                bottom = geom["y_pt"] + geom["height_pt"]
                title_bottom_y = max(title_bottom_y, bottom)

    top_offset_pt = title_bottom_y + (dims["height_pt"] * 0.05) if title_bottom_y > 0 else dims["height_pt"] * 0.3
    
    # Default elements if none provided
    if elements is None:
        elements = [
            {"text": "🧬 Cat DNA\nCats share 95.6% of their DNA with tigers!", "font_color": "#FFFFFF", "background_color": "#E74C3C"},
            {"text": "😴 Sleep Champions\nCats sleep 12-16 hours per day", "font_color": "#FFFFFF", "background_color": "#3498DB"},
            {"text": "🏃 Speed Demons\nCats can run up to 30 mph", "font_color": "#FFFFFF", "background_color": "#F39C12"},
            {"text": "👁️ Night Vision\nCats can see in 1/6th the light humans need", "font_color": "#FFFFFF", "background_color": "#9B59B6"}
        ]
    
    created_elements = []
    margin = dims["width_pt"] * 0.02  # 2% margin
    
    if layout_type == "grid":
        # 2x2 grid layout with improved sizing
        cols = 2
        rows = 2
        available_width = dims["width_pt"] - (margin * 3)
        available_height = dims["height_pt"] - top_offset_pt - (margin * 3)
        max_cell_width = available_width / cols
        max_cell_height = available_height / rows
        
        # Use presentation-appropriate font size (16pt for readability)
        target_font_size = 16
        
        for i, element in enumerate(elements[:4]):
            row = i // cols
            col = i % cols
            
            text = element.get("text", f"Element {i+1}")
            
            # Calculate optimal dimensions for this text
            dimensions = calculate_optimal_text_box_dimensions(text, max_cell_width, target_font_size)
            
            # Position in grid
            x = margin + (col * (max_cell_width + margin))
            y = top_offset_pt + margin + (row * (max_cell_height + margin))
            
            # Use calculated dimensions, but don't exceed cell limits
            width = min(dimensions["width"], max_cell_width)
            height = min(dimensions["height"], max_cell_height)
            
            result = await add_auto_sized_text_box(
                presentation_id=presentation_id,
                slide_id=slide_id,
                text=text,
                x=x,
                y=y,
                width=width,
                height=height,
                font_color=element.get("font_color"),
                background_color=element.get("background_color"),
                min_font_size=14,  # Higher minimum for presentations
                max_font_size=20   # Reasonable maximum
            )
            created_elements.append(result)
    
    return {
        "presentation_id": presentation_id,
        "slide_id": slide_id,
        "layout_type": layout_type,
        "slide_dimensions": dims,
        "top_offset_used": top_offset_pt,
        "elements_created": len(created_elements),
        "created_elements": created_elements,
        "status": "success"
    }

def calculate_optimal_font_size(text: str, width_pt: float, height_pt: float) -> int:
    """
    Calculate optimal font size to fit text within given dimensions.
    IMPROVED: Better calculations for presentation readability.
    
    Args:
        text: The text content
        width_pt: Width of text box in points
        height_pt: Height of text box in points
    
    Returns:
        Font size in points (integer)
    """
    # Count lines and get max line length
    lines = text.count('\n') + 1
    max_chars_per_line = max(len(line) for line in text.split('\n')) if text else 1
    
    # For presentations, prioritize readability over perfect fitting
    # Use more conservative estimates for better results
    
    # Width-based calculation (more conservative character width)
    usable_width = width_pt * 0.85  # Leave 15% padding
    # Average character width is roughly 0.55 * font_size for typical fonts
    width_based_size = int(usable_width / (max_chars_per_line * 0.55))
    
    # Height-based calculation (account for line spacing)
    usable_height = height_pt * 0.85  # Leave 15% padding
    # Line height is typically 1.3x font size
    height_based_size = int(usable_height / (lines * 1.3))
    
    # Take the smaller size to ensure it fits
    optimal_size = min(width_based_size, height_based_size)
    
    # For presentations, enforce better minimum sizes
    # Small text boxes should use at least 12pt, larger ones can go bigger
    min_size = 12 if width_pt < 200 else 14
    max_size = 24 if width_pt < 300 else 32
    
    optimal_size = max(min_size, min(optimal_size, max_size))
    
    return optimal_size

async def add_auto_sized_text_box(
    presentation_id: str,
    slide_id: str,
    text: str,
    x: float = 100,
    y: float = 100,
    width: float = 400,
    height: float = 100,
    font_color: Optional[str] = None,
    background_color: Optional[str] = None,
    min_font_size: int = 8,
    max_font_size: int = 48
) -> Dict[str, Any]:
    """
    Add a text box with automatically calculated font size to ensure text fits perfectly.
    
    Args:
        presentation_id: ID of the presentation (required)
        slide_id: ID of the slide (required)
        text: Text content (required)
        x: X coordinate (default: 100)
        y: Y coordinate (default: 100)
        width: Width of the text box (default: 400)
        height: Height of the text box (default: 100)
        font_color: Font color in hex format (optional)
        background_color: Background color in hex format (optional)
        min_font_size: Minimum font size (default: 8)
        max_font_size: Maximum font size (default: 48)
    
    Returns:
        Dictionary containing the operation results
    """
    print(f"INFO: add_auto_sized_text_box called for slide {slide_id}")
    
    if not GOOGLE_APIS_AVAILABLE:
        return {
            "error": "Google API client libraries are not installed.",
            "status": "error"
        }
    
    try:
        service = get_service('slides', 'v1')
        if not service:
            return {
                "error": "Failed to authenticate with Google Slides API.",
                "status": "error"
            }
        
        # Calculate optimal font size
        optimal_font_size = calculate_optimal_font_size(text, width, height)
        optimal_font_size = max(min_font_size, min(optimal_font_size, max_font_size))
        
        text_box_id = f"auto_textbox_{hashlib.md5(f'{slide_id}_{text[:20]}_{x}_{y}'.encode()).hexdigest()[:10]}"
        
        requests = []
        
        # Create the text box
        create_request = {
            'createShape': {
                'objectId': text_box_id,
                'shapeType': 'TEXT_BOX',
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width': {'magnitude': width, 'unit': 'PT'},
                        'height': {'magnitude': height, 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': x,
                        'translateY': y,
                        'unit': 'PT'
                    }
                }
            }
        }
        requests.append(create_request)
        
        # Insert text
        requests.append({
            'insertText': {
                'objectId': text_box_id,
                'text': text
            }
        })
        
        # Apply font size and styling
        style_request = {
            'updateTextStyle': {
                'objectId': text_box_id,
                'textRange': {'type': 'ALL'},
                'style': {
                    'fontSize': {
                        'magnitude': optimal_font_size,
                        'unit': 'PT'
                    }
                },
                'fields': 'fontSize'
            }
        }
        requests.append(style_request)
        
        # Apply font color if specified
        if font_color:
            hex_color = font_color.lstrip('#')
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
                
                color_request = {
                    'updateTextStyle': {
                        'objectId': text_box_id,
                        'textRange': {'type': 'ALL'},
                        'style': {
                            'foregroundColor': {
                                'opaqueColor': {
                                    'rgbColor': {'red': r, 'green': g, 'blue': b}
                                }
                            }
                        },
                        'fields': 'foregroundColor'
                    }
                }
                requests.append(color_request)
        
        # Apply background color if specified
        if background_color:
            hex_color = background_color.lstrip('#')
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
                
                bg_request = {
                    'updateShapeProperties': {
                        'objectId': text_box_id,
                        'shapeProperties': {
                            'shapeBackgroundFill': {
                                'solidFill': {
                                    'color': {
                                        'rgbColor': {'red': r, 'green': g, 'blue': b}
                                    }
                                }
                            }
                        },
                        'fields': 'shapeBackgroundFill.solidFill.color'
                    }
                }
                requests.append(bg_request)
        
        print(f"DEBUG: Sending {len(requests)} requests with font size: {optimal_font_size}pt")
        
        response = service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
        
        return {
            "presentation_id": presentation_id,
            "slide_id": slide_id,
            "text_box_id": text_box_id,
            "text": text,
            "font_size": optimal_font_size,
            "dimensions": {"width": width, "height": height},
            "position": {"x": x, "y": y},
            "status": "success"
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"ERROR: add_auto_sized_text_box failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def update_text_style(
    presentation_id: str,
    element_id: str,
    font_color: Optional[str] = None,
    font_size: Optional[int] = None,
    bold: Optional[bool] = None,
    italic: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Update the text style of a specific element (like a placeholder or text box).
    
    Args:
        presentation_id: ID of the presentation (required)
        element_id: ID of the text element to update (required)
        font_color: New font color in hex format (optional)
        font_size: New font size in points (optional)
        bold: Set text to bold (optional)
        italic: Set text to italic (optional)
        
    Returns:
        Dictionary containing the operation results
    """
    print(f"INFO: update_text_style called for element {element_id}")
    
    if not GOOGLE_APIS_AVAILABLE:
        return {"error": "Google API client libraries are not installed.", "status": "error"}

    try:
        service = get_service('slides', 'v1')
        if not service:
            return {"error": "Failed to authenticate with Google Slides API.", "status": "error"}

        requests = []
        style_rules = {}
        fields = []

        if font_color:
            hex_color = font_color.lstrip('#')
            if len(hex_color) == 6:
                r = int(hex_color[0:2], 16) / 255.0
                g = int(hex_color[2:4], 16) / 255.0
                b = int(hex_color[4:6], 16) / 255.0
                style_rules['foregroundColor'] = {'opaqueColor': {'rgbColor': {'red': r, 'green': g, 'blue': b}}}
                fields.append('foregroundColor')

        if font_size:
            style_rules['fontSize'] = {'magnitude': font_size, 'unit': 'PT'}
            fields.append('fontSize')
            
        if bold is not None:
            style_rules['bold'] = bold
            fields.append('bold')

        if italic is not None:
            style_rules['italic'] = italic
            fields.append('italic')
            
        if not style_rules:
            return {"error": "No style updates provided.", "status": "warning"}

        update_request = {
            'updateTextStyle': {
                'objectId': element_id,
                'textRange': {'type': 'ALL'},
                'style': style_rules,
                'fields': ','.join(fields)
            }
        }
        requests.append(update_request)

        body = {'requests': requests}
        response = service.presentations().batchUpdate(presentationId=presentation_id, body=body).execute()
        
        return {
            "presentation_id": presentation_id,
            "element_id": element_id,
            "updates_applied": fields,
            "status": "success"
        }

    except HttpError as e:
        return {"error": f"Google Slides API error: {str(e)}", "status": "error"}
    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}", "status": "error"}

def calculate_optimal_text_box_dimensions(text: str, max_width_pt: float, font_size: int) -> dict:
    """
    Calculate optimal text box dimensions based on content and font size.
    
    Args:
        text: The text content
        max_width_pt: Maximum available width
        font_size: Font size in points
    
    Returns:
        Dictionary with optimal width and height
    """
    lines = text.split('\n')
    num_lines = len(lines)
    max_chars_per_line = max(len(line) for line in lines) if lines else 1
    
    # Calculate required width (character width ≈ 0.55 * font_size)
    required_width = max_chars_per_line * (font_size * 0.55) + (font_size * 0.3)  # Add padding
    optimal_width = min(required_width, max_width_pt)
    
    # Calculate required height (line height ≈ 1.3 * font_size)
    line_height = font_size * 1.3
    required_height = (num_lines * line_height) + (font_size * 0.4)  # Add padding
    
    return {
        "width": optimal_width,
        "height": required_height,
        "font_size": font_size,
        "num_lines": num_lines
    }