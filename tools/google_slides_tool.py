# tools/google_slides_tool.py
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv
import importlib.util
import hashlib

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

async def add_slide(
    presentation_id: str,
    slide_layout: str = "BLANK",
    title: Optional[str] = None,
    insert_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Add a new slide to a Google Slides presentation.
    
    Args:
        presentation_id: ID of the presentation (required)
        slide_layout: Layout for the new slide - "BLANK", "TITLE_AND_BODY", "TITLE_ONLY", "SECTION_HEADER", "TWO_COLUMNS_TEXT", "TWO_COLUMNS_TEXT_AND_IMAGE", "TITLE_AND_TWO_COLUMNS", "ONE_COLUMN_TEXT", "MAIN_POINT", "BIG_NUMBER" (default: "BLANK")
        title: Title for the slide (optional, used with layouts that have title placeholders)
        insert_index: Position to insert the slide (optional, appends at end if not specified)
    
    Returns:
        Dictionary containing the new slide information
    """
    print(f"INFO: add_slide called for presentation {presentation_id}")
    
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
        
        # Generate a unique slide ID
        slide_id = f"slide_{hashlib.md5(f'{presentation_id}_{title}_{slide_layout}'.encode()).hexdigest()[:8]}"
        
        # Create slide request
        requests = [{
            'createSlide': {
                'objectId': slide_id,
                'slideLayoutReference': {
                    'predefinedLayout': slide_layout
                }
            }
        }]
        
        # Add insertion index if specified
        if insert_index is not None:
            requests[0]['createSlide']['insertionIndex'] = insert_index
        
        response = service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests}
        ).execute()
        
        # Store slide in context
        _add_slide_to_context(presentation_id, slide_id, title)
        
        result = {
            "presentation_id": presentation_id,
            "slide_id": slide_id,
            "slide_layout": slide_layout,
            "title": title,
            "status": "success"
        }
        
        return result
        
    except HttpError as e:
        return {
            "error": f"Google Slides API error: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: add_slide failed: {str(e)}")
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

async def create_slide_with_content(
    presentation_id: str,
    slide_layout: str = "TITLE_AND_BODY",
    title: Optional[str] = None,
    body_content: Optional[str] = None,
    insert_index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Create a new slide and populate its placeholders with content in one operation.
    This is the preferred method for creating slides with content.
    
    Args:
        presentation_id: ID of the presentation (required)
        slide_layout: Layout for the new slide (default: "TITLE_AND_BODY")
        title: Title text for the slide (optional)
        body_content: Body text for the slide (optional)
        insert_index: Position to insert the slide (optional)
    
    Returns:
        Dictionary containing the new slide information and content status
    """
    print(f"INFO: create_slide_with_content called for presentation {presentation_id}")
    
    # First create the slide
    slide_result = await add_slide(
        presentation_id=presentation_id,
        slide_layout=slide_layout,
        title=title,
        insert_index=insert_index
    )
    
    if slide_result.get("status") != "success":
        return slide_result
    
    slide_id = slide_result["slide_id"]
    
    # Then add content to placeholders if provided
    if title or body_content:
        content_result = await add_content_to_slide_placeholders(
            presentation_id=presentation_id,
            slide_id=slide_id,
            title_text=title,
            body_text=body_content
        )
        
        if content_result.get("status") == "success":
            slide_result.update({
                "content_added": True,
                "title_filled": content_result.get("title_added", False),
                "body_filled": content_result.get("body_added", False),
                "available_placeholders": content_result.get("available_placeholders", [])
            })
        else:
            slide_result["content_warning"] = content_result.get("error", "Failed to add content to placeholders")
            slide_result["available_placeholders"] = content_result.get("available_placeholders", [])
    
    return slide_result

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
            
            if 'shape' in page_element:
                shape = page_element['shape']
                
                if 'placeholder' in shape:
                    placeholder = shape['placeholder']
                    placeholders.append({
                        "id": element_id,
                        "type": placeholder.get('type'),
                        "index": placeholder.get('index')
                    })
                elif shape.get('shapeType') == 'TEXT_BOX':
                    text_boxes.append({
                        "id": element_id,
                        "type": "TEXT_BOX"
                    })
                else:
                    shapes.append({
                        "id": element_id,
                        "type": shape.get('shapeType')
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

def register(mcp_instance):
    """Register the Google Slides tools with the MCP server"""
    if GOOGLE_APIS_AVAILABLE:
        # Core Slides operations
        mcp_instance.tool()(create_google_slides)
        mcp_instance.tool()(add_slide)
        
        # NEW: Preferred methods for working with placeholders
        mcp_instance.tool()(create_slide_with_content)
        mcp_instance.tool()(add_content_to_slide_placeholders)
        mcp_instance.tool()(add_slide_to_last_presentation)
        
        # Legacy text box method (still useful for custom positioning)
        mcp_instance.tool()(add_text_to_slide)
        
        # Utility functions
        mcp_instance.tool()(get_slide_info)
        
        # Context query tools
        mcp_instance.tool()(list_recent_presentations)
        mcp_instance.tool()(find_presentation_by_title)
        
        print("INFO: Google Slides tools registered successfully")
    else:
        print("WARNING: Google Slides tools were not registered because required libraries are not installed.")