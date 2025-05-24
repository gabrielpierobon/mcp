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
    "recent_documents": []
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
# SIMPLIFIED GOOGLE DOCS TOOLS
# ======================

async def create_google_doc(
    title: str,
    content: str,
    share_with: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a new Google Document with content.
    
    Args:
        title: Title of the new document (required)
        content: Content for the document (required)
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
        document_body = {'title': title}
        document = docs_service.documents().create(body=document_body).execute()
        document_id = document.get('documentId')
        document_url = f"https://docs.google.com/document/d/{document_id}/edit"
        
        # Add content using simple insert
        requests = [{
            'insertText': {
                'location': {'index': 1},
                'text': content
            }
        }]
        
        docs_service.documents().batchUpdate(
            documentId=document_id,
            body={'requests': requests}
        ).execute()
        
        # Store context for future operations
        _store_document_context(document_id, title, document_url)
        
        result = {
            "document_id": document_id,
            "document_url": document_url,
            "title": title,
            "content_length": len(content),
            "status": "success"
        }
        
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

async def rewrite_last_doc(
    new_content: str
) -> Dict[str, Any]:
    """
    Completely rewrite the most recently created document with entirely new content.
    This is the main function for editing documents.
    
    Args:
        new_content: Complete new content to replace the entire document (required)
    
    Returns:
        Dictionary containing the operation results
    """
    print("INFO: rewrite_last_doc called")
    
    if not _recent_documents_context["last_document"]:
        return {
            "error": "No recent document found. Please create a document first.",
            "status": "error"
        }
    
    document_id = _recent_documents_context["last_document"]["id"]
    
    # Use the simple rewrite function
    result = await rewrite_document(document_id, new_content)
    
    if result.get("status") == "success":
        result["updated_document"] = {
            "document_id": document_id,
            "title": _recent_documents_context["last_document"]["title"],
            "url": _recent_documents_context["last_document"]["url"]
        }
    
    return result

async def rewrite_document(
    document_id: str,
    new_content: str
) -> Dict[str, Any]:
    """
    Completely rewrite a Google Document with entirely new content.
    Uses a simple but reliable approach.
    
    Args:
        document_id: ID of the document (required)
        new_content: Complete new content to replace the entire document (required)
    
    Returns:
        Dictionary containing the operation results
    """
    print(f"INFO: rewrite_document called for document {document_id}")
    
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
        
        # Step 1: Get the document to find all content
        document = service.documents().get(documentId=document_id).execute()
        
        # Step 2: Build requests to delete all text and insert new content
        requests = []
        
        # Find all text content and delete it
        content_elements = document.get('body', {}).get('content', [])
        text_ranges = []
        
        for element in content_elements:
            if 'paragraph' in element:
                paragraph = element['paragraph']
                for text_element in paragraph.get('elements', []):
                    if 'textRun' in text_element:
                        start_index = text_element.get('startIndex')
                        end_index = text_element.get('endIndex')
                        if start_index is not None and end_index is not None:
                            text_ranges.append((start_index, end_index))
        
        # Delete text ranges in reverse order (from end to beginning)
        text_ranges.sort(reverse=True)
        for start_index, end_index in text_ranges:
            # Skip the very last character to avoid newline issues
            if end_index > start_index + 1:
                requests.append({
                    'deleteContentRange': {
                        'range': {
                            'startIndex': start_index,
                            'endIndex': end_index - 1  # Avoid the trailing newline
                        }
                    }
                })
        
        # Insert new content at the beginning
        requests.append({
            'insertText': {
                'location': {'index': 1},
                'text': new_content
            }
        })
        
        # Execute all requests
        if requests:
            service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
        
        return {
            "document_id": document_id,
            "new_content_length": len(new_content),
            "operation": "document_rewritten",
            "status": "success"
        }
        
    except HttpError as e:
        return {
            "error": f"Google Docs API error: {str(e)}",
            "status": "error"
        }
    except Exception as e:
        print(f"ERROR: rewrite_document failed: {str(e)}")
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

def register(mcp_instance):
    """Register the Google Docs tools with the MCP server"""
    if GOOGLE_APIS_AVAILABLE:
        # Core operations (simplified)
        mcp_instance.tool()(create_google_doc)
        mcp_instance.tool()(rewrite_last_doc)
        mcp_instance.tool()(rewrite_document)
        mcp_instance.tool()(read_google_doc)
        mcp_instance.tool()(list_recent_documents)
        
        print("INFO: Google Docs tools registered successfully")
    else:
        print("WARNING: Google Docs tools were not registered because required libraries are not installed.")