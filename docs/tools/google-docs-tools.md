# Google Docs Tools Documentation

Tools for creating, editing, and managing Google Documents using the Google Docs API with OAuth2 authentication.

## Overview

The Google Docs tools provide document creation and editing capabilities with support for content management and collaborative features.

## Installation Requirements

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Environment Variables

- `GOOGLE_CREDENTIALS_FILE` (optional) - Path to OAuth2 credentials JSON file (default: "credentials.json")
- `GOOGLE_TOKEN_FILE` (optional) - Path to store OAuth2 token (default: "token.json")

## Authentication Setup

1. **Google Cloud Console**: Create project and enable Google Docs API
2. **OAuth2 Credentials**: Download credentials.json file
3. **First-time Setup**: Tools will open browser for permission grant
4. **Token Storage**: Subsequent uses are automatic

## Available Functions

### Document Creation

#### `create_google_doc`
Creates new Google Documents with initial content and sharing options.

**What it does:**
- Creates documents with custom titles
- Adds initial content during creation
- Automatically shares with specified email addresses
- Returns document URLs and access information

**Parameters:**
- `title` (required) - Document title
- `content` (required) - Initial document content
- `share_with` (optional) - Email addresses for sharing

### Content Management

#### `rewrite_last_doc`
Completely rewrites the most recently created document.

**What it does:**
- Uses session memory to identify recent documents
- Replaces entire document content
- Preserves document title and sharing settings
- Provides reliable content replacement

**Parameters:**
- `new_content` (required) - Complete new content for the document

#### `rewrite_document`
Completely rewrites a specific document by ID.

**What it does:**
- Clears all existing content from document
- Inserts new content as complete replacement
- Handles complex document structures safely
- Returns operation confirmation

**Parameters:**
- `document_id` (required) - Target document ID
- `new_content` (required) - New content to insert

#### `read_google_doc`
Reads content from existing Google Documents.

**What it does:**
- Extracts all text content from documents
- Returns plain text without formatting
- Provides document metadata and statistics
- Handles various document structures

**Parameters:**
- `document_id` (required) - Source document ID

### Context Management

#### `list_recent_documents`
Lists recently created documents from current session.

**What it does:**
- Shows documents created during current session
- Provides titles, IDs, and URLs
- Helps identify available documents for operations

## Session Context Features

The Google Docs tools maintain session memory for:
- **Recent Documents**: Track created documents
- **Quick Operations**: Enable "last created" functionality
- **Context Information**: Store titles and URLs for reference

## Document Features

- **Plain Text Content**: Primary focus on text content management
- **Title Management**: Document titles and metadata
- **Sharing Control**: Collaborative access management
- **Content Replacement**: Complete document rewriting capabilities

## Content Handling

- **Text Insertion**: Plain text content addition
- **Content Clearing**: Safe removal of existing content
- **Formatting Preservation**: Maintains document structure
- **Character Encoding**: Proper UTF-8 text handling

## Sharing and Permissions

- **Email Sharing**: Automatic sharing during creation
- **Permission Levels**: Reader, commenter, editor access
- **Notification Control**: Optional email notifications
- **Collaborative Editing**: Multiple user access

## Use Cases

- **Document Creation**: Generate reports, letters, and documentation
- **Content Management**: Update and maintain document content
- **Collaborative Writing**: Shared document creation and editing
- **Template Processing**: Create documents from templates
- **Report Generation**: Automated report creation from data
- **Meeting Notes**: Create and update meeting documentation
- **Project Documentation**: Maintain project-related documents

## Integration Patterns

- **With Web Search**: Create research documents from search results
- **With Airtable**: Generate reports from database content
- **With Web Crawling**: Document website analysis results
- **With Weather Data**: Create weather reports and briefings
- **With Google Sheets**: Reference data from spreadsheets

## Content Formatting

Currently supports:
- **Plain Text**: Primary content type
- **Line Breaks**: Paragraph separation
- **Basic Structure**: Document organization
- **Unicode Text**: International character support

## Error Handling

- **Authentication Failures**: OAuth2 token refresh and re-authorization
- **Permission Errors**: Insufficient access to documents
- **Content Errors**: Invalid content formatting or size limits
- **Network Issues**: Connection timeouts and API failures
- **Document Errors**: Missing or inaccessible documents

## API Quotas

- **Read Requests**: 100 requests per 100 seconds per user
- **Write Requests**: 100 requests per 100 seconds per user
- **Daily Limit**: 50,000 requests per day per project
- **Document Size**: Limited by Google Docs size restrictions

## Best Practices

- **Content Preparation**: Format content before insertion
- **Session Efficiency**: Use context features for workflow optimization
- **Error Recovery**: Implement retry logic for network issues
- **Permission Management**: Verify access before operations
- **Content Backup**: Maintain content copies for important documents