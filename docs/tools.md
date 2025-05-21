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

---

To add a new tool or update an existing one, please refer to the `docs/server_and_tool_development.md` guide.