# MCP Server Tools Documentation

This document provides comprehensive documentation for all tools available in the MCP server. Each tool is organized by category with detailed parameter descriptions, return values, and usage examples.

## Table of Contents

1. [Web Search Tools](#1-web-search-tools)
2. [Weather Tools](#2-weather-tools) 
3. [Calculator Tools](#3-calculator-tools)
4. [Web Crawling Tools](#4-web-crawling-tools)
5. [Airtable Tools](#5-airtable-tools)
6. [Google Workspace Tools](#6-google-workspace-tools)

---

## 1. Web Search Tools

These tools leverage the Brave Search API to perform web and local searches. Requires the `BRAVE_API_KEY` environment variable.

### 1.1. `brave_web_search`

**Description:** Execute web searches using Brave Search API with pagination and filtering.

**Arguments:**
- `query` (str, required): Search terms
- `count` (Optional[int], default: 10): Results per page (max 20)
- `offset` (Optional[int], default: 0): Pagination offset (max 9)

**Returns:** (Dict[str, Any])
- `query`: Original search query
- `results`: Combined web, news, and video results
- `total_count`: Estimated total web results available
- `news_count`: Number of news results in batch
- `videos_count`: Number of video results in batch
- `web_count`: Number of web results in batch
- `mixed`: Mixed results object from Brave API
- `search_info`: Available result sections
- `status`: "success" or "error"

**Environment Variables:**
- `BRAVE_API_KEY`: Brave Search API subscription token

### 1.2. `brave_local_search`

**Description:** Search for local businesses and services. Automatically falls back to web search if no local results found.

**Arguments:**
- `query` (str, required): Local search terms
- `count` (Optional[int], default: 10): Number of results (max 20)

**Returns:** (Dict[str, Any])
- If local results found:
  - `query`: Original search query
  - `places`: List of local place results
  - `total_count`: Number of local places returned
- If fallback to web search: Same structure as `brave_web_search`
- If error: `error` and `status` fields

**Environment Variables:**
- `BRAVE_API_KEY`: Brave Search API subscription token

---

## 2. Weather Tools

### 2.1. `get_weather`

**Description:** Fetch current and forecast weather for any location worldwide using Open-Meteo API.

**Arguments:**
- `location` (str, optional, default: "Madrid, Spain"): City name or address

**Returns:** (Dict[str, Any])
- `location`: Resolved location name
- `coordinates`: Dictionary with `latitude` and `longitude`
- `current_weather`: Dictionary with:
  - `temperature` (float)
  - `condition` (str): Weather description
  - `wind_speed` (float)
  - `units`: Temperature and wind speed units
- `forecast`: List of upcoming weather (6-hour intervals, 48 hours)
- `source`: "Open-Meteo API"
- `status`: "success" or "error"

**Environment Variables:** None (uses public APIs)

---

## 3. Calculator Tools

### 3.1. `calculator`

**Description:** Perform basic arithmetic operations with error handling.

**Arguments:**
- `operation` (str, required): Operation type ("add", "+", "subtract", "-", "multiply", "*", "divide", "/")
- `num1` (float, required): First number
- `num2` (float, required): Second number

**Returns:** (Dict[str, Any])
- `result` (float): Calculation result
- `description` (str): Operation description
- `status`: "success" or "error"
- `error` (if error): Error description

**Environment Variables:** None

---

## 4. Web Crawling Tools

These tools use Crawl4AI for LLM-friendly web content extraction. Requires `crawl4ai` installation.

### 4.1. `crawl_webpage`

**Description:** Crawl a single webpage and extract content in various formats.

**Arguments:**
- `url` (str, required): URL to crawl
- `output_format` (str, default: "markdown"): "markdown", "html", "text", or "all"
- `include_links` (bool, default: True): Include links in output
- `include_images` (bool, default: True): Include images in output
- `headless` (bool, default: True): Run browser in headless mode
- `extract_main_content` (bool, default: True): Extract main content only
- `cache_enabled` (bool, default: True): Use cache if available
- `wait_for_selector` (str, optional): CSS selector to wait for
- `wait_time` (int, optional): **DEPRECATED** - Additional wait time

**Returns:** (Dict[str, Any])
- `url`: Crawled URL
- `status_code`: HTTP status code
- `title`: Page title
- `markdown`: Content in Markdown (if requested)
- `html`: Content in HTML (if requested)
- `text`: Content in plain text (if requested)
- `links`: Dictionary of links (if include_links)
- `images`: List of images (if include_images)
- `metadata`: Page metadata
- `status`: "success" or "error"

### 4.2. `crawl_multiple_webpages`

**Description:** Crawl multiple webpages in parallel with concurrency control.

**Arguments:**
- `urls` (List[str], required): List of URLs to crawl
- `output_format` (str, default: "markdown"): Format for all pages
- `include_links` (bool, default: True): Include links
- `include_images` (bool, default: True): Include images  
- `headless` (bool, default: True): Headless browser mode
- `extract_main_content` (bool, default: True): Main content only
- `max_concurrent` (int, default: 5): Maximum concurrent crawls

**Returns:** (Dict[str, Any])
- `results`: Dictionary with URLs as keys, crawl results as values
- `count`: Total URLs processed
- `successful`: Number of successful crawls
- `failed`: Number of failed crawls
- `status`: "success" or "error"

### 4.3. `extract_structured_data`

**Description:** Extract structured data using CSS selectors.

**Arguments:**
- `url` (str, required): URL to crawl
- `schema` (Dict[str, Any], required): CSS selector schema
- `headless` (bool, default: True): Headless browser mode
- `wait_for_selector` (str, optional): Wait for selector

**Schema Example:**
```json
{
    "name": "Products",
    "baseSelector": ".product-item",
    "fields": [
        {"name": "title", "selector": "h2", "type": "text"},
        {"name": "price", "selector": ".price", "type": "text"},
        {"name": "url", "selector": "a", "type": "attribute", "attribute": "href"}
    ]
}
```

**Returns:** (Dict[str, Any])
- `url`: Crawled URL
- `data`: Extracted structured data
- `status`: "success" or "error"

**Environment Variables:** None (uses Crawl4AI library)

---

## 5. Airtable Tools

Comprehensive Airtable integration requiring `AIRTABLE_PERSONAL_ACCESS_TOKEN` environment variable.

### 5.1. Base Management Tools

#### 5.1.1. `list_airtable_bases`

**Description:** List all accessible Airtable bases.

**Arguments:** None

**Returns:** (Dict[str, Any])
- `bases`: List of base objects with `id`, `name`, `permissionLevel`
- `offset`: Pagination offset
- `status`: "success" or "error"

#### 5.1.2. `get_base_schema`

**Description:** Get schema (tables and fields) of an Airtable base.

**Arguments:**
- `base_id` (str, required): Base ID

**Returns:** (Dict[str, Any])
- `base_id`: The base ID
- `tables`: List of table objects with fields and metadata
- `status`: "success" or "error"

#### 5.1.3. `get_base_by_name`

**Description:** Get base information by name instead of ID.

**Arguments:**
- `base_name` (str, required): Base name (e.g., "Storyteller")

**Returns:** (Dict[str, Any])
- `base_name`: The base name
- `base_id`: The base ID
- `permission_level`: User's permission level
- `available_bases`: List of available names (if not found)
- `status`: "success" or "error"

#### 5.1.4. `validate_base_and_table`

**Description:** Validate base and table existence.

**Arguments:**
- `base_name` (str, required): Base name
- `table_name` (str, required): Table name

**Returns:** (Dict[str, Any])
- `base_name`, `base_id`, `table_name`, `table_id`
- `table_fields`: List of field names
- `available_tables`: Available table names (if error)
- `validation`: "success" or error details
- `status`: "success" or "error"

### 5.2. Record Operations

#### 5.2.1. `list_records`

**Description:** List records with advanced filtering and sorting.

**Arguments:**
- `base_id` (str, required): Base ID
- `table_name` (str, required): Table name
- `fields` (Optional[List[str]]): Field names to return
- `filter_formula` (Optional[str]): Airtable filter formula
- `max_records` (Optional[int], default: 100): Maximum records (max 100)
- `sort` (Optional[List[Dict[str, str]]]): Sort objects
- `view` (Optional[str]): View name to use

**Returns:** (Dict[str, Any])
- `base_id`, `table_name`: Identifiers
- `records`: List of record objects with `id`, `fields`, `createdTime`
- `count`: Number of records returned
- `filter_used`: Applied filter formula
- `status`: "success" or "error"

#### 5.2.2. `list_records_by_base_name`

**Description:** User-friendly version accepting base name instead of ID.

**Arguments:** Same as `list_records` but uses `base_name` instead of `base_id`

**Returns:** Same as `list_records`

**Example Usage:**
- "Show me all Spanish stories from my Storyteller base"
- "List themes from the Themes table in Storyteller"

#### 5.2.3. `search_records`

**Description:** Search records by field value with flexible matching.

**Arguments:**
- `base_id` (str, required): Base ID
- `table_name` (str, required): Table name
- `search_field` (str, required): Field to search in
- `search_value` (str, required): Value to search for
- `additional_fields` (Optional[List[str]]): Additional fields to return
- `match_type` (Optional[str], default: "exact"): "exact", "contains", "starts_with"

**Returns:** Same structure as `list_records` but filtered

#### 5.2.4. `search_records_by_base_name`

**Description:** User-friendly search accepting base name.

**Arguments:** Same as `search_records` but uses `base_name`

**Example Usage:**
- "Find all users with Spanish language preference in Storyteller"
- "Search for stories with 'adventure' theme in PublicStories table"

#### 5.2.5. `get_record_by_id`

**Description:** Get specific record by ID.

**Arguments:**
- `base_id` (str, required): Base ID
- `table_name` (str, required): Table name
- `record_id` (str, required): Record ID

**Returns:** (Dict[str, Any])
- `base_id`, `table_name`: Identifiers
- `record`: Record object with `id`, `fields`, `createdTime`
- `status`: "success" or "error"

#### 5.2.6. `count_records`

**Description:** Count records with optional filtering.

**Arguments:**
- `base_id` (str, required): Base ID
- `table_name` (str, required): Table name
- `filter_formula` (Optional[str]): Filter formula

**Returns:** (Dict[str, Any])
- `base_id`, `table_name`: Identifiers
- `count`: Number of records
- `filter_used`: Applied filter
- `note`: Count limitation note
- `status`: "success" or "error"

### 5.3. Base Creation Tools

**Note:** May require Team Plan or higher for base/table creation.

#### 5.3.1. `create_airtable_base`

**Description:** Create new Airtable base with optional initial tables.

**Arguments:**
- `name` (str, required): Base name
- `workspace_id` (Optional[str]): Workspace ID
- `tables` (Optional[List[Dict[str, Any]]]): Initial table configurations

**Returns:** (Dict[str, Any])
- `base_id`: Created base ID
- `name`: Base name
- `permission_level`: User's permission level
- `tables`: Created tables
- `status`: "success" or "error"

#### 5.3.2. `create_airtable_table`

**Description:** Create new table in existing base.

**Arguments:**
- `base_id` (str, required): Base ID
- `table_name` (str, required): Table name
- `description` (Optional[str]): Table description
- `fields` (Optional[List[Dict[str, Any]]]): Field configurations

**Returns:** (Dict[str, Any])
- `table_id`: Created table ID
- `name`, `description`: Table details
- `fields`: Created fields
- `views`: Table views
- `status`: "success" or "error"

#### 5.3.3. `create_base_with_template`

**Description:** Create base using predefined template.

**Arguments:**
- `name` (str, required): Base name
- `template` (str, required): Template type
- `workspace_id` (Optional[str]): Workspace ID

**Available Templates:**
- `"project_management"`: Projects and tasks with status tracking
- `"crm"`: Contacts, deals, and sales pipeline
- `"inventory"`: Product tracking with stock levels
- `"event_planning"`: Events and task management
- `"content_calendar"`: Content planning and scheduling

**Returns:** Same as `create_airtable_base`

**Environment Variables:**
- `AIRTABLE_PERSONAL_ACCESS_TOKEN`: Airtable Personal Access Token

---

## 6. Google Workspace Tools

Comprehensive Google Workspace integration with OAuth2 authentication.

### 6.1. Authentication Setup

**Required Environment Variables:**
- `GOOGLE_CREDENTIALS_FILE` (default: "credentials.json"): OAuth2 credentials
- `GOOGLE_TOKEN_FILE` (default: "token.json"): Stored token (auto-created)

**Required Scopes:**
- `https://www.googleapis.com/auth/spreadsheets`
- `https://www.googleapis.com/auth/documents`
- `https://www.googleapis.com/auth/presentations`
- `https://www.googleapis.com/auth/drive`

### 6.2. Google Sheets Tools

#### 6.2.1. `create_google_sheet`

**Description:** Create new Google Spreadsheet with multiple sheets and sharing.

**Arguments:**
- `title` (str, required): Spreadsheet title
- `sheet_names` (Optional[List[str]], default: ["Sheet1"]): Sheet names to create
- `share_with` (Optional[List[str]]): Email addresses to share with

**Returns:** (Dict[str, Any])
- `spreadsheet_id`: Created spreadsheet ID
- `spreadsheet_url`: Access URL
- `title`: Spreadsheet title
- `sheets`: Created sheet names
- `shared_with`: Successfully shared emails
- `status`: "success" or "error"

#### 6.2.2. `write_to_sheet`

**Description:** Write data to Google Sheet.

**Arguments:**
- `spreadsheet_id` (str, required): Spreadsheet ID
- `range_name` (str, required): A1 notation range (e.g., "Sheet1!A1:C3")
- `values` (List[List[str]], required): 2D array of values
- `value_input_option` (str, default: "USER_ENTERED"): "RAW" or "USER_ENTERED"

**Returns:** (Dict[str, Any])
- `spreadsheet_id`: Spreadsheet ID
- `updated_range`: Range that was updated
- `updated_rows`, `updated_columns`, `updated_cells`: Update counts
- `status`: "success" or "error"

#### 6.2.3. `read_from_sheet`

**Description:** Read data from Google Sheet.

**Arguments:**
- `spreadsheet_id` (str, required): Spreadsheet ID
- `range_name` (str, required): A1 notation range

**Returns:** (Dict[str, Any])
- `spreadsheet_id`: Spreadsheet ID
- `range`: Range that was read
- `values`: 2D array of values
- `row_count`, `column_count`: Data dimensions
- `status`: "success" or "error"

#### 6.2.4. `append_to_last_sheet`

**Description:** Append data to most recently created spreadsheet.

**Arguments:**
- `values` (List[List[str]], required): Values to append
- `start_row` (Optional[int]): Starting row (auto-calculated if not provided)
- `sheet_name` (Optional[str]): Target sheet (uses default if not provided)

**Returns:** Same as `write_to_sheet` plus `appended_to` context information

#### 6.2.5. `append_to_sheet_by_title`

**Description:** Append data to spreadsheet found by title search.

**Arguments:**
- `title_search` (str, required): Partial title to search for
- `values` (List[List[str]], required): Values to append
- `start_row` (Optional[int]): Starting row
- `sheet_name` (Optional[str]): Target sheet

**Returns:** Same as `append_to_last_sheet`

#### 6.2.6. Context Tools

- `list_recent_spreadsheets`: List recently created spreadsheets
- `find_spreadsheet_by_title`: Find spreadsheet by title search
- `clear_sheet_range`: Clear data from sheet range

### 6.3. Google Docs Tools

#### 6.3.1. `create_google_doc`

**Description:** Create new Google Document with content.

**Arguments:**
- `title` (str, required): Document title
- `content` (str, required): Document content
- `share_with` (Optional[List[str]]): Email addresses to share with

**Returns:** (Dict[str, Any])
- `document_id`: Created document ID
- `document_url`: Access URL
- `title`: Document title
- `content_length`: Length of added content
- `shared_with`: Successfully shared emails
- `status`: "success" or "error"

#### 6.3.2. `rewrite_last_doc`

**Description:** Completely rewrite most recently created document.

**Arguments:**
- `new_content` (str, required): New content to replace entire document

**Returns:** (Dict[str, Any])
- `document_id`: Document ID
- `new_content_length`: Length of new content
- `operation`: "document_rewritten"
- `updated_document`: Context information
- `status`: "success" or "error"

#### 6.3.3. `rewrite_document`

**Description:** Completely rewrite specific document.

**Arguments:**
- `document_id` (str, required): Document ID
- `new_content` (str, required): New content

**Returns:** Same as `rewrite_last_doc` without context info

#### 6.3.4. `read_google_doc`

**Description:** Read content from Google Document.

**Arguments:**
- `document_id` (str, required): Document ID

**Returns:** (Dict[str, Any])
- `document_id`: Document ID
- `title`: Document title
- `content`: Full text content
- `character_count`: Number of characters
- `status`: "success" or "error"

#### 6.3.5. `list_recent_documents`

**Description:** List recently created documents from session.

**Returns:** Context information about recent documents

### 6.4. Google Slides Tools

#### 6.4.1. `create_google_slides`

**Description:** Create new Google Slides presentation.

**Arguments:**
- `title` (str, required): Presentation title
- `template_id` (Optional[str]): Template presentation ID to copy
- `share_with` (Optional[List[str]]): Email addresses to share with

**Returns:** (Dict[str, Any])
- `presentation_id`: Created presentation ID
- `presentation_url`: Access URL
- `title`: Presentation title
- `created_from_template`: Template ID (if used)
- `shared_with`: Successfully shared emails
- `status`: "success" or "error"

#### 6.4.2. `create_slide_with_content` (Preferred Method)

**Description:** Create slide and populate placeholders in one operation.

**Arguments:**
- `presentation_id` (str, required): Presentation ID
- `slide_layout` (str, default: "TITLE_AND_BODY"): Slide layout
- `title` (Optional[str]): Title for slide
- `body_content` (Optional[str]): Body content for slide
- `insert_index` (Optional[int]): Position to insert slide

**Available Layouts:**
- `"BLANK"`: Empty slide
- `"TITLE_AND_BODY"`: Title with body content
- `"TITLE_ONLY"`: Title only
- `"SECTION_HEADER"`: Section header
- `"TWO_COLUMNS_TEXT"`: Two text columns
- `"MAIN_POINT"`: Main point layout

**Returns:** (Dict[str, Any])
- `presentation_id`: Presentation ID
- `slide_id`: Created slide ID
- `slide_layout`: Layout used
- `title`: Slide title
- `content_added`: Whether content was successfully added
- `title_filled`, `body_filled`: Which placeholders were filled
- `available_placeholders`: Available placeholder types
- `status`: "success" or "error"

#### 6.4.3. `add_slide_to_last_presentation` (Preferred Method)

**Description:** Add slide with content to most recently created presentation.

**Arguments:**
- `slide_layout` (str, default: "TITLE_AND_BODY"): Slide layout
- `title` (Optional[str]): Title for slide
- `body_content` (Optional[str]): Body content for slide

**Returns:** Same as `create_slide_with_content` plus `added_to` context information

#### 6.4.4. `add_slide`

**Description:** Add new slide to presentation (without content).

**Arguments:**
- `presentation_id` (str, required): Presentation ID
- `slide_layout` (str, default: "BLANK"): Slide layout
- `title` (Optional[str]): Title for slide
- `insert_index` (Optional[int]): Position to insert

**Returns:** (Dict[str, Any])
- `presentation_id`: Presentation ID
- `slide_id`: Created slide ID
- `slide_layout`: Layout used
- `title`: Slide title
- `status`: "success" or "error"

#### 6.4.5. `add_content_to_slide_placeholders`

**Description:** Add content to existing placeholders in a slide.

**Arguments:**
- `presentation_id` (str, required): Presentation ID
- `slide_id` (str, required): Slide ID
- `title_text` (Optional[str]): Text for title placeholder
- `body_text` (Optional[str]): Text for body placeholder

**Returns:** (Dict[str, Any])
- `presentation_id`: Presentation ID
- `slide_id`: Slide ID
- `title_placeholder`, `body_placeholder`: Placeholder object IDs
- `available_placeholders`: Available placeholder types
- `title_added`, `body_added`: Success flags
- `status`: "success" or "error"

#### 6.4.6. `add_text_to_slide`

**Description:** Add custom text box to slide (legacy method).

**Arguments:**
- `presentation_id` (str, required): Presentation ID
- `slide_id` (str, required): Slide ID
- `text` (str, required): Text content
- `x` (float, default: 100): X coordinate in points
- `y` (float, default: 100): Y coordinate in points
- `width` (float, default: 400): Width in points
- `height` (float, default: 100): Height in points

**Returns:** (Dict[str, Any])
- `presentation_id`: Presentation ID
- `slide_id`: Slide ID
- `text_box_id`: Created text box ID
- `text`: Added text
- `position`: Dictionary with x, y coordinates
- `size`: Dictionary with width, height
- `status`: "success" or "error"

#### 6.4.7. Utility Tools

- `get_slide_info`: Get slide structure and placeholder information
- `list_recent_presentations`: List recently created presentations
- `find_presentation_by_title`: Find presentation by title search

### 6.5. Google Workspace Setup Guide

#### 6.5.1. Google Cloud Console Setup

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing one

2. **Enable APIs**
   - Enable Google Sheets API
   - Enable Google Docs API
   - Enable Google Slides API
   - Enable Google Drive API

3. **Create OAuth2 Credentials**
   - Go to "Credentials" in API & Services
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Desktop application" type
   - Download credentials.json file

#### 6.5.2. Installation Requirements

```bash
# Install Google API client libraries
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

#### 6.5.3. First-Time Authentication

On first use, the system will:
1. Open browser for OAuth consent
2. Prompt to sign in and grant permissions
3. Save token for future use

#### 6.5.4. Usage Examples

```python
# Create spreadsheet with data
sheet_result = await create_google_sheet(
    title="Sales Report Q1 2024",
    sheet_names=["January", "February", "March"],
    share_with=["manager@company.com"]
)

# Add data to spreadsheet
await write_to_sheet(
    spreadsheet_id=sheet_result["spreadsheet_id"],
    range_name="January!A1:D4",
    values=[
        ["Date", "Product", "Sales", "Revenue"],
        ["2024-01-01", "Product A", 10, 1000],
        ["2024-01-02", "Product B", 15, 1500],
        ["2024-01-03", "Product A", 8, 800]
    ]
)

# Create document with content
doc_result = await create_google_doc(
    title="Meeting Notes - 2024-01-15",
    content="# Meeting Notes\n\nDate: January 15, 2024\nAttendees: John, Jane, Bob\n\n",
    share_with=["team@company.com"]
)

# Create presentation with slides
slides_result = await create_google_slides(
    title="Q1 Results Presentation",
    share_with=["stakeholders@company.com"]
)

# Add slide with content (preferred method)
await add_slide_to_last_presentation(
    slide_layout="TITLE_AND_BODY",
    title="Q1 Sales Results", 
    body_content="• 15% increase in revenue\n• 23% more customers\n• Expanded to 3 new markets"
)
```

### 6.6. Best Practices

1. **Authentication**: Keep credentials.json secure and exclude from version control
2. **Sharing**: Only share documents with necessary recipients
3. **Error Handling**: Always check status field in responses
4. **Batch Operations**: Group multiple operations for better performance
5. **Context Awareness**: Use "last created" functions for workflow efficiency

### 6.7. Troubleshooting

- **Authentication errors**: Delete token.json and re-authenticate
- **Permission denied**: Ensure APIs are enabled in Google Cloud Console
- **File not found**: Use correct file ID from Google Drive URL
- **Quota exceeded**: Wait 24 hours or request quota increase

---

## Environment Variables Summary

| Tool Category | Environment Variable | Description | Required |
|---------------|---------------------|-------------|----------|
| Brave Search | `BRAVE_API_KEY` | Brave Search API subscription token | Yes |
| Airtable | `AIRTABLE_PERSONAL_ACCESS_TOKEN` | Airtable Personal Access Token | Yes |
| Google Workspace | `GOOGLE_CREDENTIALS_FILE` | Path to OAuth2 credentials JSON | Yes |
| Google Workspace | `GOOGLE_TOKEN_FILE` | Path to store OAuth2 token | No (auto-created) |
| Web Crawling | None | Uses Crawl4AI library | No |
| Weather | None | Uses public Open-Meteo API | No |
| Calculator | None | Built-in functionality | No |

---

## Tool Status and Availability

| Tool | Status | Dependencies | Notes |
|------|--------|--------------|--------|
| Brave Search | ✅ Available | `httpx`, API key | Requires paid API subscription |
| Weather | ✅ Available | `httpx` | Free public API |
| Calculator | ✅ Available | Built-in | No external dependencies |
| Web Crawling | ⚠️ Optional | `crawl4ai`, `playwright` | Install separately if needed |
| Airtable | ✅ Available | `httpx`, API token | Free tier available |
| Google Sheets | ⚠️ Optional | Google API libs, OAuth2 | Install separately if needed |
| Google Docs | ⚠️ Optional | Google API libs, OAuth2 | Install separately if needed |
| Google Slides | ⚠️ Optional | Google API libs, OAuth2 | Install separately if needed |

---

## Adding New Tools

To add new tools to the MCP server:

1. **Create Tool File**: Add new tool module in `tools/` directory
2. **Implement Functions**: Create async functions with proper type hints and docstrings
3. **Add Registration**: Include `register(mcp_instance)` function
4. **Update Server**: Import and register in `run.py`
5. **Update Documentation**: Add tool documentation to this file

**Example Tool Structure:**
```python
# tools/my_new_tool.py
from typing import Dict, Any, Optional

async def my_tool_function(
    param1: str,
    param2: Optional[int] = None
) -> Dict[str, Any]:
    """
    Description of what this tool does.
    
    Args:
        param1: Description of required parameter
        param2: Description of optional parameter
        
    Returns:
        Dictionary containing results and status
    """
    try:
        # Tool implementation
        result = f"Processed: {param1}"
        return {
            "result": result,
            "param2_used": param2,
            "status": "success"
        }
    except Exception as e:
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

def register(mcp_instance):
    """Register tool with MCP server"""
    mcp_instance.tool()(my_tool_function)
```

For detailed development guidance, see `docs/server_and_tool_development.md`.

---

## Support and Documentation

- **Development Guide**: `docs/server_and_tool_development.md`
- **MCP Protocol**: `docs/mcp.md`
- **System Prompts**: `docs/prompt_guide.md`
- **FastMCP Documentation**: [gofastmcp.com](https://gofastmcp.com)
- **GitHub Issues**: Report bugs and feature requests

---

*Last updated: January 2025*