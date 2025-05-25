# Web Crawling Tools Documentation

Tools for extracting content from websites using Crawl4AI with LLM-friendly output formats.

## Overview

The Web Crawling tools enable AI agents to extract and process web content in various formats optimized for analysis and understanding.

## Installation Requirements

```bash
pip install crawl4ai playwright
playwright install
```

## Environment Variables

None required. Uses the Crawl4AI library directly.

## Available Functions

### `crawl_webpage`

Extracts content from a single webpage in multiple formats.

**What it does:**
- Crawls web pages with browser automation
- Extracts content in markdown, HTML, or plain text
- Filters main content vs. full page content
- Includes or excludes links and images as needed
- Handles dynamic content with configurable wait conditions
- Supports caching for improved performance

**Parameters:**
- `url` (required) - URL to crawl
- `output_format` (optional) - "markdown", "html", "text", or "all" (default: "markdown")
- `include_links` (optional) - Include links in output (default: true)
- `include_images` (optional) - Include images in output (default: true)
- `headless` (optional) - Run browser in headless mode (default: true)
- `extract_main_content` (optional) - Extract only main content (default: true)
- `cache_enabled` (optional) - Use caching if available (default: true)
- `wait_for_selector` (optional) - CSS selector to wait for before extraction

**Returns:**
- Extracted content in requested format(s)
- Page metadata (title, description)
- Links and images (if requested)
- Page coordinates and status information

### `crawl_multiple_webpages`

Crawls multiple webpages concurrently with controlled parallelism.

**What it does:**
- Processes multiple URLs simultaneously
- Controls concurrency to avoid overwhelming servers
- Aggregates results from all successful crawls
- Provides success/failure statistics
- Uses same extraction options as single page crawling

**Parameters:**
- `urls` (required) - List of URLs to crawl
- `output_format` (optional) - Format for all pages (default: "markdown")
- `include_links` (optional) - Include links (default: true)
- `include_images` (optional) - Include images (default: true)
- `headless` (optional) - Headless browser mode (default: true)
- `extract_main_content` (optional) - Main content only (default: true)
- `max_concurrent` (optional) - Maximum concurrent crawls (default: 5)

**Returns:**
- Results dictionary with URL keys and crawl results
- Success and failure counts
- Aggregated metadata from all crawls

### `extract_structured_data`

Extracts structured data using CSS selectors and schema definitions.

**What it does:**
- Uses CSS selectors to extract specific data fields
- Applies schema definitions for consistent data structure
- Handles repeated elements and data patterns
- Extracts text, attributes, and nested content
- Returns structured JSON data ready for analysis

**Parameters:**
- `url` (required) - URL to crawl for data extraction
- `schema` (required) - CSS selector schema definition
- `headless` (optional) - Headless browser mode (default: true)
- `wait_for_selector` (optional) - Wait for specific element

**Returns:**
- Structured data matching the provided schema
- Extraction statistics and metadata
- Error details if extraction fails

## Schema Format

For structured data extraction, schemas define:
- **Base selector**: Main container element
- **Field definitions**: Individual data fields to extract
- **Data types**: Text, attributes, or nested content
- **Extraction rules**: How to process each field

## Use Cases

- Content research and analysis
- Data mining from websites
- Competitive intelligence gathering
- News and article monitoring
- E-commerce product information extraction
- Documentation and knowledge base scraping

## Browser Features

- **JavaScript Execution**: Handles dynamic content
- **Multiple Formats**: Markdown, HTML, plain text output
- **Image Processing**: Optional image inclusion and metadata
- **Link Extraction**: Comprehensive link discovery and categorization
- **Responsive Design**: Works with mobile and desktop layouts

## Performance Features

- **Caching**: Reduces redundant requests
- **Concurrency Control**: Prevents server overload
- **Timeout Management**: Handles slow-loading pages
- **Error Recovery**: Graceful handling of failed crawls

## Limitations

- Requires Playwright browser installation
- May be blocked by anti-bot measures
- Performance depends on target website complexity
- Some dynamic content may require specific wait conditions