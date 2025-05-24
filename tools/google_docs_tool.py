# tools/google_docs_tool.py
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
        print("INFO: Google Docs API libraries successfully imported")
    except ImportError as e:
        print(f"WARNING: Error importing Google API components: {str(e)}")
        GOOGLE_APIS_AVAILABLE = False
else:
    print("WARNING: Google API client libraries are not installed.")
    print("To install them, run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")

# Google API scopes for Docs
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
]

# Google API credentials paths
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "token.json")

# ======================
# CONTEXT MEMORY SYSTEM
# ======================

# Global context to store recent documents
_recent_documents_context = {
    "last_document": None,
    "recent_documents": []  # Store multiple recent docs
}

def _store_document_context(document_id: str, title: str, url: str):
    """Store document context for future operations."""
    context = {
        "id": document_id,
        "title": title,
        "url": url,
        "type": "document"
    }
    _recent_documents_context["last_document"] = context
    _recent_documents_context["recent_documents"].insert(0, context)
    # Keep only last 10 documents
    _recent_documents_context["recent_documents"] = _recent_documents_context["recent_documents"][:10]

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

async def list_recent_documents() -> Dict[str, Any]:
    """
    List recently created Google Documents from this session.
    
    Returns:
        Dictionary containing recent documents information
    """
    print("INFO: list_recent_documents called")
    
    return {
        "recent_documents": _recent_documents_context["recent_documents"],
        "last_document": _recent_documents_context["last_document"],
        "count": len(_recent_documents_context["recent_documents"]),
        "status": "success"
    }

async def find_document_by_title(title_search: str) -> Dict[str, Any]:
    """
    Find a document by searching its title.
    
    Args:
        title_search: Partial title to search for (case-insensitive)
    
    Returns:
        Dictionary containing matching documents
    """
    print(f"INFO: find_document_by_title called with search: {title_search}")
    
    matching_docs = [d for d in _recent_documents_context["recent_documents"] 
                     if title_search.lower() in d["title"].lower()]
    
    return {
        "matching_documents": matching_docs,
        "search_term": title_search,
        "count": len(matching_docs),
        "all_available_titles": [d["title"] for d in _recent_documents_context["recent_documents"]],
        "status": "success"
    }

# ======================
# GOOGLE DOCS TOOLS
# ======================

async def create_google_doc(
    title: str,
    content: Optional[str] = None,
    share_with: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a new Google Document.
    
    Args:
        title: Title of the new document (required)
        content: Initial content for the document (optional)
        share_with: List of email addresses to share with (optional)
    
    Returns:
        Dictionary containing the created document information
    """
    print(f"INFO: create_google_doc called with title: {title}")
    
    if not GOOGLE_APIS_AVAILABLE:
        return {
            "error": "Google API client libraries are not installed.",
            "status": "error"
        }
    
    try:
        docs_service = get_service('docs', 'v1')
        drive_service = get_service('drive', 'v3')
        
        if not docs_service:
            return {
                "error": "Failed to authenticate with Google Docs API.",
                "status": "error"
            }
        
        # Create the document
        document_body = {
            'title': title
        }
        
        document = docs_service.documents().create(body=document_body).execute()
        document_id = document.get('documentId')
        document_url = f"https://docs.google.com/document/d/{document_id}/edit"
        
        # Store context for future operations
        _store_document_context(document_id, title, document_url)
        
        result = {
            "document_id": document_id,
            "document_url": document_url,
            "title": title,
            "status": "success"
        }
        
        # Add content if provided
        if content:
            content_result = await insert_text_to_doc(document_id, content, 1)
            if content_result.get("status") == "success":
                result["content_added"] = True
            else:
                result["content_warning"] = "Failed to add initial content"
        
        # Share the document if email addresses provided
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
                        fileId=document_id,
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
            "error": f"Google Docs API error: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: create_google_doc failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def insert_text_to_doc(
    document_id: str,
    text: str,
    index: int = 1
) -> Dict[str, Any]:
    """
    Insert text into a Google Document at a specific position.
    
    Args:
        document_id: ID of the document (required)
        text: Text to insert (required)
        index: Position to insert text (default: 1, which is the beginning)
    
    Returns:
        Dictionary containing the operation results
    """
    print(f"INFO: insert_text_to_doc called for document {document_id}")
    
    if not GOOGLE_APIS_AVAILABLE:
        return {
            "error": "Google API client libraries are not installed.",
            "status": "error"
        }
    
    try:
        service = get_service('docs', 'v1')
        if not service:
            return {
                "error": "Failed to authenticate with Google Docs API.",
                "status": "error"
            }
        
        requests = [{
            'insertText': {
                'location': {
                    'index': index
                },
                'text': text
            }
        }]
        
        result = service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()
        
        return {
            "document_id": document_id,
            "text_inserted": text,
            "insertion_index": index,
            "revision_id": result.get('documentId'),
            "status": "success"
        }
        
    except HttpError as e:
        return {
            "error": f"Google Docs API error: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: insert_text_to_doc failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def read_google_doc(
    document_id: str
) -> Dict[str, Any]:
    """
    Read content from a Google Document.
    
    Args:
        document_id: ID of the document (required)
    
    Returns:
        Dictionary containing the document content and metadata
    """
    print(f"INFO: read_google_doc called for document {document_id}")
    
    if not GOOGLE_APIS_AVAILABLE:
        return {
            "error": "Google API client libraries are not installed.",
            "status": "error"
        }
    
    try:
        service = get_service('docs', 'v1')
        if not service:
            return {
                "error": "Failed to authenticate with Google Docs API.",
                "status": "error"
            }
        
        document = service.documents().get(documentId=document_id).execute()
        
        # Extract text content
        content = ""
        for element in document.get('body', {}).get('content', []):
            if 'paragraph' in element:
                for text_run in element['paragraph'].get('elements', []):
                    if 'textRun' in text_run:
                        content += text_run['textRun'].get('content', '')
        
        return {
            "document_id": document_id,
            "title": document.get('title', ''),
            "revision_id": document.get('revisionId', ''),
            "content": content,
            "character_count": len(content),
            "status": "success"
        }
        
    except HttpError as e:
        return {
            "error": f"Google Docs API error: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: read_google_doc failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def replace_entire_doc_content(
    document_id: str,
    new_content: str
) -> Dict[str, Any]:
    """
    Replace the entire content of a Google Document with new content.
    
    Args:
        document_id: ID of the document (required)
        new_content: New content to replace the entire document (required)
    
    Returns:
        Dictionary containing the operation results
    """
    print(f"INFO: replace_entire_doc_content called for document {document_id}")
    
    if not GOOGLE_APIS_AVAILABLE:
        return {
            "error": "Google API client libraries are not installed.",
            "status": "error"
        }
    
    try:
        service = get_service('docs', 'v1')
        if not service:
            return {
                "error": "Failed to authenticate with Google Docs API.",
                "status": "error"
            }
        
        # First, read the current document to get its structure
        try:
            document = service.documents().get(documentId=document_id).execute()
        except HttpError as e:
            if e.resp.status == 404:
                return {
                    "error": "Document not found. It may have been deleted or you may not have access.",
                    "status": "error"
                }
            elif e.resp.status == 403:
                return {
                    "error": "Access denied. You may not have permission to edit this document.",
                    "status": "error"
                }
            else:
                return {
                    "error": f"Failed to access document: {str(e)}",
                    "status": "error"
                }
        
        # Get the total content length more safely
        content_length = 1
        body_content = document.get('body', {}).get('content', [])
        
        for element in body_content:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for text_element in paragraph.get('elements', []):
                    if 'textRun' in text_element:
                        text_content = text_element['textRun'].get('content', '')
                        content_length += len(text_content)
        
        # Use a simpler approach: delete content range and insert new
        requests = []
        
        # Only delete if there's content beyond the initial character
        if content_length > 1:
            requests.append({
                'deleteContentRange': {
                    'range': {
                        'startIndex': 1,
                        'endIndex': content_length
                    }
                }
            })
        
        # Insert the new content
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': new_content
            }
        })
        
        # Execute the batch update
        result = service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()
        
        return {
            "document_id": document_id,
            "new_content_length": len(new_content),
            "original_content_length": content_length,
            "operation": "entire_document_replaced",
            "status": "success"
        }
        
    except HttpError as e:
        error_detail = f"HTTP {e.resp.status}: {str(e)}"
        if e.resp.status == 400:
            error_detail += " (Bad request - possibly invalid content or formatting)"
        elif e.resp.status == 403:
            error_detail += " (Permission denied - check document sharing settings)"
        elif e.resp.status == 404:
            error_detail += " (Document not found)"
        
        return {
            "error": f"Google Docs API error: {error_detail}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: replace_entire_doc_content failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

async def update_last_doc_with_content(
    new_content: str
) -> Dict[str, Any]:
    """
    Replace the entire content of the most recently created document with new content.
    This is the preferred method for "editing" or "adding to" a document.
    
    Args:
        new_content: New content to replace the entire document (required)
    
    Returns:
        Dictionary containing the operation results
    """
    print("INFO: update_last_doc_with_content called")
    
    if not _recent_documents_context["last_document"]:
        return {
            "error": "No recent document found. Please create a document first or use replace_entire_doc_content with a specific document ID.",
            "status": "error"
        }
    
    document_id = _recent_documents_context["last_document"]["id"]
    
    result = await replace_entire_doc_content(document_id, new_content)
    
    if result.get("status") == "success":
        result["updated_document"] = {
            "document_id": document_id,
            "title": _recent_documents_context["last_document"]["title"],
            "url": _recent_documents_context["last_document"]["url"]
        }
    
    return result

async def append_to_last_doc(
    text: str,
    add_line_break: bool = True
) -> Dict[str, Any]:
    """
    Append text to the most recently created document (fallback method).
    
    Args:
        text: Text to append (required)
        add_line_break: Whether to add a line break before the new text (default: True)
    
    Returns:
        Dictionary containing the operation results
    """
    print("INFO: append_to_last_doc called")
    
    if not _recent_documents_context["last_document"]:
        return {
            "error": "No recent document found. Please create a document first.",
            "status": "error"
        }
    
    document_id = _recent_documents_context["last_document"]["id"]
    
    try:
        # Read current document content
        doc_content = await read_google_doc(document_id)
        if doc_content.get("status") != "success":
            return {
                "error": "Failed to read document content.",
                "status": "error"
            }
        
        # Get current content and append new text
        current_content = doc_content.get("content", "")
        separator = "\n\n" if add_line_break and current_content.strip() else ""
        new_full_content = current_content + separator + text
        
        # Replace entire document with combined content
        return await replace_entire_doc_content(document_id, new_full_content)
        
    except Exception as e:
        return {
            "error": f"Failed to append to document: {str(e)}",
            "status": "error"
        }

def register(mcp_instance):
    """Register the Google Docs tools with the MCP server"""
    if GOOGLE_APIS_AVAILABLE:
        # Core Docs operations
        mcp_instance.tool()(create_google_doc)
        mcp_instance.tool()(insert_text_to_doc)
        mcp_instance.tool()(read_google_doc)
        mcp_instance.tool()(replace_entire_doc_content)
        
        # Context-aware operations (preferred for editing)
        mcp_instance.tool()(update_last_doc_with_content)
        mcp_instance.tool()(append_to_last_doc)  # Fallback method
        
        # Context query tools
        mcp_instance.tool()(list_recent_documents)
        mcp_instance.tool()(find_document_by_title)
        
        print("INFO: Google Docs tools registered successfully")
    else:
        print("WARNING: Google Docs tools were not registered because required libraries are not installed.")