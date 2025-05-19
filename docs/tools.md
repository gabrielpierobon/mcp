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

---

To add a new tool or update an existing one, please refer to the `docs/server_and_tool_development.md` guide. 