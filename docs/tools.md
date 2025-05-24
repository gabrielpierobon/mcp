# Available MCP Server Tools

This document provides an overview of the tools currently available in this MCP server.

## 1. Brave Search Tools

These tools leverage the Brave Search API to perform web and local searches. Requires the `BRAVE_API_KEY` environment variable to be set.

### 1.1. `brave_web_search`

*   **Description:** Executes web searches using the Brave Search API, including results from web pages, news, and videos. Supports pagination.
*   **Arguments:**
    *   `query` (str, required): The search terms.
    *   `count` (Optional[int], optional, default: 10): Number of results per page (max 20).
    *   `offset` (Optional[int], optional, default: 0): Pagination offset (max 9, meaning up to 10 pages if count is 10, as offset is 0-indexed).
*   **Returns:** (Dict[str, Any])
    *   `query`: The original search query.
    *   `results`: A list combining web, news, and video results. Each result is a dictionary with details like title, URL, description, etc.
    *   `total_count`: Estimated total web results available.
    *   `news_count`: Number of news results returned in this batch.
    *   `videos_count`: Number of video results returned in this batch.
    *   `web_count`: Number of web results returned in this batch.
    *   `mixed`: Mixed results object from Brave API.
    *   `search_info`: Contains `available_sections` (list of result types found, e.g., `web`, `news`).
    *   `status`: "success" or "error".
    *   `error` (if status is "error"): Description of the error.
    *   `details` (if status is "error" and API error): Raw error text from API.
*   **Environment Variables:**
    *   `BRAVE_API_KEY`: Your Brave Search API subscription token.

### 1.2. `brave_local_search`

*   **Description:** Searches for local businesses and services using the Brave Search API. If no local results are found for the query, it automatically falls back to performing a `brave_web_search` with the same query and count.
*   **Arguments:**
    *   `query` (str, required): The local search terms (e.g., "pizza near me", "coffee shops in downtown").
    *   `count` (Optional[int], optional, default: 10): Number of results to return (max 20).
*   **Returns:** (Dict[str, Any])
    *   If local results are found:
        *   `query`: The original search query.
        *   `places`: A list of local place results. Each place is a dictionary with details like name, address, phone, website, etc.
        *   `total_count`: Number of local places returned.
        *   `status`: "success".
    *   If no local results are found (fallback to `brave_web_search`):
        *   The same structure as returned by `brave_web_search`.
    *   If an error occurs:
        *   `error`: Description of the error.
        *   `details` (if API error): Raw error text from API.
        *   `status`: "error".
*   **Environment Variables:**
    *   `BRAVE_API_KEY`: Your Brave Search API subscription token.

## 2. `get_weather`

*   **Description:** Fetches the current and forecast weather for any location in the world using the Open-Meteo API.
*   **Arguments:**
    *   `location` (str, optional, default: "Madrid, Spain"): City name or address (e.g., "New York", "Tokyo, Japan", "Paris, France").
*   **Returns:** (Dict[str, Any])
    *   `location`: The resolved location name (e.g., "Madrid, Spain").
    *   `coordinates`: Dictionary with `latitude` and `longitude`.
    *   `current_weather`: Dictionary with:
        *   `temperature` (float)
        *   `condition` (str): Textual description of weather (e.g., "Clear sky").
        *   `wind_speed` (float)
        *   `units`: Dictionary with `temperature` unit (e.g., "°C") and `wind_speed` unit (e.g., "km/h").
    *   `forecast`: A list of dictionaries for upcoming weather, typically in 6-hour intervals for the next 48 hours. Each entry contains:
        *   `time` (str): Forecast time in "YYYY-MM-DD HH:MM ±HHMM" format (includes UTC offset).
        *   `temperature` (float)
        *   `condition` (str)
    *   `source`: "Open-Meteo API".
    *   `status`: "success" or "error".
    *   `error` (if status is "error"): Description of the error.
*   **Environment Variables:** None directly, but relies on public Open-Meteo APIs.

## 3. `calculator`

*   **Description:** Performs basic arithmetic operations.
*   **Arguments:**
    *   `operation` (str, required): The operation to perform. Accepts "add", "+", "subtract", "-", "multiply", "*", "divide", "/". Case-insensitive.
    *   `num1` (float, required): The first number.
    *   `num2` (float, required): The second number.
*   **Returns:** (Dict[str, Any])
    *   `result` (float, if successful): The result of the calculation.
    *   `description` (str, if successful): A string describing the operation performed (e.g., "10 + 5 = 15").
    *   `status`: "success" or "error".
    *   `error` (if status is "error"): Description of the error (e.g., "Division by zero is not allowed", "Unknown operation: ...").
*   **Environment Variables:** None.

## 4. Web Crawler Tools

These tools leverage Crawl4AI, an open-source LLM-friendly web crawler to extract content from websites. Requires `crawl4ai` to be installed.

### 4.1. `crawl_webpage`

*   **Description:** Crawls a single webpage and extracts its content in various formats (markdown, HTML, or plain text).
*   **Arguments:**
    *   `url` (str, required): URL of the webpage to crawl.
    *   `output_format` (str, optional, default: "markdown"): Format of the output - "markdown", "html", "text", or "all".
    *   `include_links` (bool, optional, default: True): Whether to include links in the output.
    *   `include_images` (bool, optional, default: True): Whether to include images in the output.
    *   `headless` (bool, optional, default: True): Whether to run the browser in headless mode.
    *   `extract_main_content` (bool, optional, default: True): Whether to extract only the main content or the entire page.
    *   `cache_enabled` (bool, optional, default: True): Whether to use cache if available.
    *   `wait_for_selector` (str, optional): CSS selector to wait for before extracting content.
    *   `wait_time` (int, optional): Additional time in milliseconds to wait after page load.
*   **Returns:** (Dict[str, Any])
    *   `url`: The URL that was crawled.
    *   `status_code`: HTTP status code of the response.
    *   `title`: Title of the webpage.
    *   `markdown`: Extracted content in Markdown format (if requested).
    *   `html`: Extracted content in HTML format (if requested).
    *   `text`: Extracted content in plain text format (if requested).
    *   `links`: Dictionary of internal and external links (if include_links is True).
    *   `images`: List of images found on the page (if include_images is True).
    *   `status`: "success" or "error".
    *   `error` (if status is "error"): Description of the error.
*   **Environment Variables:** None directly, uses Crawl4AI library.

### 4.2. `crawl_multiple_webpages`

*   **Description:** Crawls multiple webpages in parallel and extracts their content.
*   **Arguments:**
    *   `urls` (List[str], required): List of URLs to crawl.
    *   `output_format` (str, optional, default: "markdown"): Format of the output - "markdown", "html", "text", or "all".
    *   `include_links` (bool, optional, default: True): Whether to include links in the output.
    *   `include_images` (bool, optional, default: True): Whether to include images in the output.
    *   `headless` (bool, optional, default: True): Whether to run the browser in headless mode.
    *   `extract_main_content` (bool, optional, default: True): Whether to extract only the main content or the entire page.
    *   `max_concurrent` (int, optional, default: 5): Maximum number of concurrent crawls.
*   **Returns:** (Dict[str, Any])
    *   `results`: Dictionary with URLs as keys and their respective crawl results as values.
    *   `count`: Total number of URLs processed.
    *   `successful`: Number of successful crawls.
    *   `failed`: Number of failed crawls.
    *   `status`: "success" or "error".
    *   `error` (if status is "error"): Description of the error.
*   **Environment Variables:** None directly, uses Crawl4AI library.

### 4.3. `extract_structured_data`

*   **Description:** Extracts structured data from a webpage using CSS selectors.
*   **Arguments:**
    *   `url` (str, required): URL of the webpage to crawl.
    *   `schema` (Dict[str, Any], required): Schema defining the CSS selectors for data extraction.
    *   `headless` (bool, optional, default: True): Whether to run the browser in headless mode.
    *   `wait_for_selector` (str, optional): CSS selector to wait for before extracting data.
*   **Returns:** (Dict[str, Any])
    *   `url`: The URL that was crawled.
    *   `data`: The extracted structured data.
    *   `status`: "success" or "error".
    *   `error` (if status is "error"): Description of the error.
*   **Environment Variables:** None directly, uses Crawl4AI library.
*   **Schema Example:**
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

## 5. Airtable MCP Tools

These tools enable AI agents to interact with Airtable bases, tables, and records. Requires the `AIRTABLE_PERSONAL_ACCESS_TOKEN` environment variable to be set.

### 5.1. Base Management Tools

#### 5.1.1. `list_airtable_bases`

*   **Description:** Lists all Airtable bases accessible with your Personal Access Token.
*   **Arguments:** None.
*   **Returns:** (Dict[str, Any])
    *   `bases`: List of base objects with `id`, `name`, and `permissionLevel`.
    *   `offset`: Pagination offset (if applicable).
    *   `status`: "success" or "error".
*   **Environment Variables:**
    *   `AIRTABLE_PERSONAL_ACCESS_TOKEN`: Your Airtable Personal Access Token.

#### 5.1.2. `get_base_schema`

*   **Description:** Gets the schema (tables and fields) of an Airtable base.
*   **Arguments:**
    *   `base_id` (str, required): ID of the base to get schema for.
*   **Returns:** (Dict[str, Any])
    *   `base_id`: The base ID.
    *   `tables`: List of table objects with fields, views, and metadata.
    *   `status`: "success" or "error".

#### 5.1.3. `get_base_by_name`

*   **Description:** Get base information by name instead of requiring the base ID. Useful for user-friendly queries.
*   **Arguments:**
    *   `base_name` (str, required): Name of the base (e.g., "Storyteller").
*   **Returns:** (Dict[str, Any])
    *   `base_name`: The base name.
    *   `base_id`: The base ID.
    *   `permission_level`: User's permission level on this base.
    *   `status`: "success" or "error".
    *   `available_bases`: List of available base names (if base not found).

#### 5.1.4. `validate_base_and_table`

*   **Description:** Validates that a base exists and contains the specified table. Helpful for error prevention.
*   **Arguments:**
    *   `base_name` (str, required): Name of the base.
    *   `table_name` (str, required): Name of the table.
*   **Returns:** (Dict[str, Any])
    *   `base_name`: The base name.
    *   `base_id`: The base ID.
    *   `table_name`: The table name.
    *   `table_id`: The table ID.
    *   `table_fields`: List of field names in the table.
    *   `available_tables`: List of available table names (if table not found).
    *   `validation`: "success" or error details.
    *   `status`: "success" or "error".

### 5.2. Record Querying Tools

#### 5.2.1. `list_records`

*   **Description:** General-purpose tool to list records from a specific table with advanced filtering, sorting, and field selection.
*   **Arguments:**
    *   `base_id` (str, required): ID of the base.
    *   `table_name` (str, required): Name of the table.
    *   `fields` (Optional[List[str]]): List of field names to return (returns all if not specified).
    *   `filter_formula` (Optional[str]): Airtable formula to filter records (e.g., `{Status} = 'Active'`).
    *   `max_records` (Optional[int], default: 100): Maximum number of records to return (max: 100).
    *   `sort` (Optional[List[Dict[str, str]]]): Sort objects `[{"field": "FieldName", "direction": "asc"}]`.
    *   `view` (Optional[str]): Name of the view to use.
*   **Returns:** (Dict[str, Any])
    *   `base_id`: The base ID.
    *   `table_name`: The table name.
    *   `records`: List of record objects with `id`, `fields`, and `createdTime`.
    *   `count`: Number of records returned.
    *   `filter_used`: The filter formula applied (if any).
    *   `status`: "success" or "error".

#### 5.2.2. `list_records_by_base_name`

*   **Description:** User-friendly version of `list_records` that accepts base name instead of base ID.
*   **Arguments:**
    *   `base_name` (str, required): Name of the base (e.g., "Storyteller").
    *   `table_name` (str, required): Name of the table.
    *   `fields` (Optional[List[str]]): List of field names to return.
    *   `filter_formula` (Optional[str]): Airtable formula to filter records.
    *   `max_records` (Optional[int], default: 100): Maximum number of records to return.
    *   `sort` (Optional[List[Dict[str, str]]]): Sort objects.
    *   `view` (Optional[str]): Name of the view to use.
*   **Returns:** Same as `list_records`.
*   **Example Usage:**
    ```
    "Show me all Spanish stories from my Storyteller base"
    "List themes from the Themes table in Storyteller"
    ```

#### 5.2.3. `search_records`

*   **Description:** Search for records by a specific field value with flexible matching options.
*   **Arguments:**
    *   `base_id` (str, required): ID of the base.
    *   `table_name` (str, required): Name of the table.
    *   `search_field` (str, required): Name of the field to search in.
    *   `search_value` (str, required): Value to search for.
    *   `additional_fields` (Optional[List[str]]): Additional fields to return in results.
    *   `match_type` (Optional[str], default: "exact"): Type of match - "exact", "contains", "starts_with".
*   **Returns:** (Dict[str, Any])
    *   Same structure as `list_records` but filtered to matching records.

#### 5.2.4. `search_records_by_base_name`

*   **Description:** User-friendly version of `search_records` that accepts base name instead of base ID.
*   **Arguments:**
    *   `base_name` (str, required): Name of the base.
    *   `table_name` (str, required): Name of the table.
    *   `search_field` (str, required): Name of the field to search in.
    *   `search_value` (str, required): Value to search for.
    *   `additional_fields` (Optional[List[str]]): Additional fields to return.
    *   `match_type` (Optional[str], default: "exact"): Type of match.
*   **Returns:** Same as `search_records`.
*   **Example Usage:**
    ```
    "Find all users with Spanish language preference in Storyteller"
    "Search for stories with 'adventure' theme in my PublicStories table"
    ```

#### 5.2.5. `get_record_by_id`

*   **Description:** Get a specific record by its Airtable record ID.
*   **Arguments:**
    *   `base_id` (str, required): ID of the base.
    *   `table_name` (str, required): Name of the table.
    *   `record_id` (str, required): ID of the record to retrieve.
*   **Returns:** (Dict[str, Any])
    *   `base_id`: The base ID.
    *   `table_name`: The table name.
    *   `record`: Record object with `id`, `fields`, and `createdTime`.
    *   `status`: "success" or "error".

#### 5.2.6. `count_records`

*   **Description:** Count records in a table, optionally with a filter.
*   **Arguments:**
    *   `base_id` (str, required): ID of the base.
    *   `table_name` (str, required): Name of the table.
    *   `filter_formula` (Optional[str]): Airtable formula to filter records.
*   **Returns:** (Dict[str, Any])
    *   `base_id`: The base ID.
    *   `table_name`: The table name.
    *   `count`: Number of records (based on first 100 if table is larger).
    *   `filter_used`: The filter formula applied (if any).
    *   `status`: "success" or "error".

### 5.3. Base and Table Creation Tools

**Note:** These tools may be limited on Free Plan accounts. Table and base creation typically requires Team Plan or higher.

#### 5.3.1. `create_airtable_base`

*   **Description:** Create a new Airtable base with optional initial tables.
*   **Arguments:**
    *   `name` (str, required): Name of the new base.
    *   `workspace_id` (Optional[str]): ID of the workspace to create the base in.
    *   `tables` (Optional[List[Dict[str, Any]]]): List of table configurations to create initially.
*   **Returns:** (Dict[str, Any])
    *   `base_id`: ID of the created base.
    *   `name`: Name of the base.
    *   `permission_level`: User's permission level.
    *   `tables`: List of created tables.
    *   `status`: "success" or "error".

#### 5.3.2. `create_airtable_table`

*   **Description:** Create a new table in an existing Airtable base.
*   **Arguments:**
    *   `base_id` (str, required): ID of the base to create the table in.
    *   `table_name` (str, required): Name of the new table.
    *   `description` (Optional[str]): Description of the table.
    *   `fields` (Optional[List[Dict[str, Any]]]): List of field configurations.
*   **Returns:** (Dict[str, Any])
    *   `table_id`: ID of the created table.
    *   `name`: Name of the table.
    *   `description`: Description of the table.
    *   `fields`: List of created fields.
    *   `status`: "success" or "error".

#### 5.3.3. `create_base_with_template`

*   **Description:** Create a new Airtable base using a predefined template.
*   **Arguments:**
    *   `name` (str, required): Name of the new base.
    *   `template` (str, required): Template type - "project_management", "crm", "inventory", "event_planning", "content_calendar".
    *   `workspace_id` (Optional[str]): ID of the workspace to create the base in.
*   **Returns:** Same as `create_airtable_base`.

## 6. Google Workspace Tools

These tools enable AI agents to create and edit Google Sheets, Docs, and Slides. Requires Google API authentication setup.

### 6.1. Google Sheets Tools

#### 6.1.1. `create_google_sheet`

*   **Description:** Create a new Google Spreadsheet with optional multiple sheets and sharing.
*   **Arguments:**
    *   `title` (str, required): Title of the new spreadsheet.
    *   `sheet_names` (Optional[List[str]]): List of sheet names to create (defaults to ["Sheet1"]).
    *   `share_with` (Optional[List[str]]): List of email addresses to share with.
*   **Returns:** (Dict[str, Any])
    *   `spreadsheet_id`: ID of the created spreadsheet.
    *   `spreadsheet_url`: URL to access the spreadsheet.
    *   `title`: Title of the spreadsheet.
    *   `sheets`: List of created sheet names.
    *   `shared_with`: List of emails shared with (if applicable).
    *   `status`: "success" or "error".
*   **Environment Variables:**
    *   `GOOGLE_CREDENTIALS_FILE`: Path to Google OAuth2 credentials JSON file.
    *   `GOOGLE_TOKEN_FILE`: Path to store OAuth2 token (auto-created).

#### 6.1.2. `write_to_sheet`

*   **Description:** Write data to a Google Sheet.
*   **Arguments:**
    *   `spreadsheet_id` (str, required): ID of the spreadsheet.
    *   `range_name` (str, required): A1 notation range (e.g., "Sheet1!A1:C3", "A1:B10").
    *   `values` (List[List[Any]], required): 2D array of values to write.
    *   `value_input_option` (str, optional): How values should be interpreted ("RAW" or "USER_ENTERED").
*   **Returns:** (Dict[str, Any])
    *   `spreadsheet_id`: ID of the spreadsheet.
    *   `updated_range`: Range that was updated.
    *   `updated_rows`: Number of rows updated.
    *   `updated_columns`: Number of columns updated.
    *   `updated_cells`: Number of cells updated.
    *   `status`: "success" or "error".

#### 6.1.3. `read_from_sheet`

*   **Description:** Read data from a Google Sheet.
*   **Arguments:**
    *   `spreadsheet_id` (str, required): ID of the spreadsheet.
    *   `range_name` (str, required): A1 notation range to read.
*   **Returns:** (Dict[str, Any])
    *   `spreadsheet_id`: ID of the spreadsheet.
    *   `range`: Range that was read.
    *   `values`: 2D array of values from the sheet.
    *   `row_count`: Number of rows returned.
    *   `column_count`: Number of columns in the first row.
    *   `status`: "success" or "error".

### 6.2. Google Docs Tools

#### 6.2.1. `create_google_doc`

*   **Description:** Create a new Google Document.
*   **Arguments:**
    *   `title` (str, required): Title of the new document.
    *   `content` (Optional[str]): Initial content for the document.
    *   `share_with` (Optional[List[str]]): List of email addresses to share with.
*   **Returns:** (Dict[str, Any])
    *   `document_id`: ID of the created document.
    *   `document_url`: URL to access the document.
    *   `title`: Title of the document.
    *   `content_added`: Boolean indicating if initial content was added.
    *   `shared_with`: List of emails shared with (if applicable).
    *   `status`: "success" or "error".

#### 6.2.2. `insert_text_to_doc`

*   **Description:** Insert text into a Google Document at a specific position.
*   **Arguments:**
    *   `document_id` (str, required): ID of the document.
    *   `text` (str, required): Text to insert.
    *   `index` (int, optional): Position to insert text (default: 1, which is the beginning).
*   **Returns:** (Dict[str, Any])
    *   `document_id`: ID of the document.
    *   `text_inserted`: Text that was inserted.
    *   `insertion_index`: Position where text was inserted.
    *   `revision_id`: Document revision ID.
    *   `status`: "success" or "error".

#### 6.2.3. `read_google_doc`

*   **Description:** Read content from a Google Document.
*   **Arguments:**
    *   `document_id` (str, required): ID of the document.
*   **Returns:** (Dict[str, Any])
    *   `document_id`: ID of the document.
    *   `title`: Title of the document.
    *   `revision_id`: Document revision ID.
    *   `content`: Full text content of the document.
    *   `character_count`: Number of characters in the content.
    *   `status`: "success" or "error".

### 6.3. Google Slides Tools

#### 6.3.1. `create_google_slides`

*   **Description:** Create a new Google Slides presentation.
*   **Arguments:**
    *   `title` (str, required): Title of the new presentation.
    *   `template_id` (Optional[str]): ID of a template presentation to copy from.
    *   `share_with` (Optional[List[str]]): List of email addresses to share with.
*   **Returns:** (Dict[str, Any])
    *   `presentation_id`: ID of the created presentation.
    *   `presentation_url`: URL to access the presentation.
    *   `title`: Title of the presentation.
    *   `created_from_template`: Template ID used (if applicable).
    *   `shared_with`: List of emails shared with (if applicable).
    *   `status`: "success" or "error".

#### 6.3.2. `add_slide`

*   **Description:** Add a new slide to a Google Slides presentation.
*   **Arguments:**
    *   `presentation_id` (str, required): ID of the presentation.
    *   `slide_layout` (str, optional): Layout for the new slide ("BLANK", "TITLE_AND_BODY", "TITLE_ONLY", etc.).
    *   `title` (Optional[str]): Title for the slide.
*   **Returns:** (Dict[str, Any])
    *   `presentation_id`: ID of the presentation.
    *   `slide_id`: ID of the new slide.
    *   `slide_layout`: Layout used for the slide.
    *   `title`: Title of the slide (if applicable).
    *   `status`: "success" or "error".

#### 6.3.3. `add_text_to_slide`

*   **Description:** Add a text box to a specific slide in a Google Slides presentation.
*   **Arguments:**
    *   `presentation_id` (str, required): ID of the presentation.
    *   `slide_id` (str, required): ID of the slide.
    *   `text` (str, required): Text content to add.
    *   `x` (float, optional): X coordinate of the text box in points (default: 100).
    *   `y` (float, optional): Y coordinate of the text box in points (default: 100).
    *   `width` (float, optional): Width of the text box in points (default: 400).
    *   `height` (float, optional): Height of the text box in points (default: 100).
*   **Returns:** (Dict[str, Any])
    *   `presentation_id`: ID of the presentation.
    *   `slide_id`: ID of the slide.
    *   `text_box_id`: ID of the created text box.
    *   `text`: Text that was added.
    *   `position`: Dictionary with x and y coordinates.
    *   `size`: Dictionary with width and height.
    *   `status`: "success" or "error".

### 6.4. Environment Variables

*   **`GOOGLE_CREDENTIALS_FILE`**: Path to your Google OAuth2 credentials JSON file (default: "credentials.json").
*   **`GOOGLE_TOKEN_FILE`**: Path to store OAuth2 token (default: "token.json", auto-created after first auth).

### 6.5. Required Google API Scopes

The Google Workspace tools require the following OAuth2 scopes:
*   `https://www.googleapis.com/auth/spreadsheets` - Create and edit Google Sheets
*   `https://www.googleapis.com/auth/documents` - Create and edit Google Docs
*   `https://www.googleapis.com/auth/presentations` - Create and edit Google Slides
*   `https://www.googleapis.com/auth/drive` - Share and manage files

### 6.6. Setup Requirements

1. **Google Cloud Console Setup:**
   - Create a Google Cloud project
   - Enable Google Sheets, Docs, Slides, and Drive APIs
   - Create OAuth2 credentials (Desktop application type)
   - Download credentials.json file

2. **Install Dependencies:**
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

3. **First-Time Authentication:**
   - On first use, the system will open a browser for OAuth consent
   - Sign in and grant permissions
   - Token will be saved for future use

### 6.7. Usage Examples

```python
# Create a new spreadsheet with data
sheet_result = await create_google_sheet(
    title="Sales Report Q1 2024",
    sheet_names=["January", "February", "March"],
    share_with=["manager@company.com"]
)

# Add data to the spreadsheet
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

# Create a document with content
doc_result = await create_google_doc(
    title="Meeting Notes - 2024-01-15",
    content="# Meeting Notes\n\nDate: January 15, 2024\nAttendees: John, Jane, Bob\n\n",
    share_with=["team@company.com"]
)

# Create a presentation
slides_result = await create_google_slides(
    title="Q1 Results Presentation",
    share_with=["stakeholders@company.com"]
)

# Add slides and content
slide_result = await add_slide(
    presentation_id=slides_result["presentation_id"],
    slide_layout="TITLE_AND_BODY",
    title="Q1 Sales Results"
)

await add_text_to_slide(
    presentation_id=slides_result["presentation_id"],
    slide_id=slide_result["slide_id"],
    text="• 15% increase in revenue\n• 23% more customers\n• Expanded to 3 new markets",
    x=100,
    y=250,
    width=500,
    height=200
)
```

### 6.8. Best Practices

1. **Authentication:** Ensure credentials.json is kept secure and not committed to version control
2. **Sharing:** Only share documents with necessary recipients
3. **Error Handling:** Always check the status field in responses
4. **Batch Operations:** For multiple operations, consider grouping them to improve performance
5. **Permissions:** Use appropriate Google API scopes - only request what you need

### 6.9. Troubleshooting

- **Authentication errors:** Delete token.json and re-authenticate
- **Permission denied:** Ensure all required APIs are enabled in Google Cloud Console
- **File not found:** Use the correct file ID from the Google Drive URL
- **Quota exceeded:** Google APIs have daily quotas; wait 24 hours or request increase

---

To add a new tool or update an existing one, please refer to the `docs/server_and_tool_development.md` guide.