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

### 5.4. Environment Variables

*   **`AIRTABLE_PERSONAL_ACCESS_TOKEN`**: Your Airtable Personal Access Token with appropriate scopes:
    *   `data.records:read` - Read records from tables
    *   `data.records:write` - Create, update, delete records (for future tools)
    *   `schema.bases:read` - Read base schemas
    *   `schema.bases:write` - Create and modify bases/tables
    *   `user.email:read` - (optional) Read user email

### 5.5. Usage Examples

```bash
# List all available bases
"What Airtable bases do I have?"

# Get base structure
"Show me the structure of my Storyteller base"

# Query records with natural language
"Show me all Spanish stories for preschoolers from my PublicStories table"

# Search for specific records
"Find all users with Spanish language preference"

# Count records with filters
"How many themes do I have in my Themes table?"

# Validate before querying
"Check if my Storyteller base has a Users table"
```

### 5.6. Best Practices

1. **Use base names instead of IDs** - Tools like `list_records_by_base_name` are more reliable and user-friendly.
2. **Validate first** - Use `validate_base_and_table` to prevent errors.
3. **Start with simple queries** - List bases and get schemas before complex filtering.
4. **Handle Free Plan limitations** - Base/table creation may be restricted; focus on data querying.

### 5.7. Troubleshooting

- **403 Forbidden errors**: Check Personal Access Token permissions and ensure you're using the correct base ID.
- **Base not found**: Use `list_airtable_bases` to see available bases and their exact names.
- **Table not found**: Use `get_base_schema` to see available tables in a base.
- **Filter errors**: Check Airtable formula syntax in filter expressions.

---

To add a new tool or update an existing one, please refer to the `docs/server_and_tool_development.md` guide.