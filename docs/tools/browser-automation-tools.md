# Browser Automation Tools Documentation

Tools for controlling web browsers using Playwright for interactive web automation.

## Overview

The Browser Automation tools provide AI agents with full browser control capabilities for interacting with websites, filling forms, clicking elements, and extracting content.

## Installation Requirements

```bash
pip install playwright
playwright install
```

## Environment Variables

None required. Playwright manages browser installations locally.

## Available Functions

### Browser Management

#### `launch_browser`
Launches a new browser instance with session management.

**What it does:**
- Creates browser contexts for isolated sessions
- Supports Chrome, Firefox, and Safari browsers
- Configures headless or visible browser modes
- Manages multiple concurrent browser sessions

**Parameters:**
- `browser_type` (optional) - "chromium", "firefox", "webkit" (default: "chromium")
- `headless` (optional) - Run without UI (default: true)
- `context_id` (optional) - Session identifier (default: "default")

#### `close_browser_context`
Closes browser sessions and cleans up resources.

#### `list_browser_contexts`
Lists all active browser sessions with status information.

### Navigation

#### `navigate_to_page`
Navigates to URLs with configurable loading conditions.

**What it does:**
- Loads web pages with timeout control
- Waits for different page load states
- Handles redirects and navigation events
- Returns page metadata and status codes

**Parameters:**
- `url` (required) - Web page URL
- `context_id` (optional) - Browser session (default: "default")
- `wait_for_load_state` (optional) - "load", "domcontentloaded", "networkidle" (default: "networkidle")
- `timeout` (optional) - Maximum wait time in milliseconds (default: 30000)

### Content Extraction

#### `get_page_content`
Extracts content from web pages in multiple formats.

**What it does:**
- Retrieves page text, HTML, or markdown content
- Takes screenshots as base64-encoded images
- Extracts content from specific page elements
- Handles dynamic content after page interactions

**Parameters:**
- `context_id` (optional) - Browser session (default: "default")
- `content_type` (optional) - "text", "html", "markdown", "screenshot" (default: "text")
- `selector` (optional) - CSS selector for specific elements

#### `get_accessibility_snapshot`
Provides LLM-friendly page structure analysis.

**What it does:**
- Generates accessibility tree representation
- Identifies interactive elements and landmarks
- Provides semantic page structure
- Optimized for AI understanding of page layout

### User Interactions

#### `click_element`
Clicks on web page elements using CSS selectors.

**What it does:**
- Locates elements by CSS selector
- Simulates mouse clicks and interactions
- Handles navigation triggered by clicks
- Waits for elements to become clickable

**Parameters:**
- `selector` (required) - CSS selector for target element
- `context_id` (optional) - Browser session (default: "default")
- `wait_for_navigation` (optional) - Wait for page navigation (default: false)
- `timeout` (optional) - Maximum wait time (default: 10000)

#### `fill_form_field`
Fills input fields with text content.

**What it does:**
- Locates form inputs by CSS selector
- Clears existing content before filling
- Simulates typing with proper events
- Handles different input types

**Parameters:**
- `selector` (required) - CSS selector for input field
- `value` (required) - Text to enter
- `context_id` (optional) - Browser session (default: "default")
- `clear_first` (optional) - Clear before filling (default: true)
- `timeout` (optional) - Maximum wait time (default: 10000)

#### `wait_for_element`
Waits for elements to reach specific states.

**What it does:**
- Monitors element visibility and attachment
- Waits for dynamic content to load
- Handles timing-dependent page changes
- Returns element status and content

**Parameters:**
- `selector` (required) - CSS selector for target element
- `context_id` (optional) - Browser session (default: "default")
- `state` (optional) - "attached", "detached", "visible", "hidden" (default: "visible")
- `timeout` (optional) - Maximum wait time (default: 10000)

### Advanced Features

#### `execute_javascript`
Runs custom JavaScript code in the browser context.

**What it does:**
- Executes arbitrary JavaScript in page context
- Returns JavaScript execution results
- Accesses page variables and functions
- Modifies page content and behavior

**Parameters:**
- `script` (required) - JavaScript code to execute
- `context_id` (optional) - Browser session (default: "default")

## Use Cases

- **Form Automation**: Login sequences, data entry, form submissions
- **Dynamic Content**: Interacting with SPAs and AJAX-heavy sites
- **E-commerce**: Product browsing, cart management, checkout processes
- **Testing**: Automated testing of web applications
- **Data Extraction**: Complex scraping requiring user interactions
- **Screenshots**: Visual documentation and monitoring
- **API Testing**: Browser-based API interaction and testing

## Browser Features

- **Multiple Browser Engines**: Chrome, Firefox, Safari support
- **Mobile Emulation**: Device and viewport simulation
- **Network Control**: Request/response interception
- **Cookie Management**: Session and authentication handling
- **File Handling**: Upload and download capabilities
- **Geolocation**: Location-based testing

## Session Management

- **Context Isolation**: Separate sessions for different tasks
- **Resource Cleanup**: Automatic memory management
- **Concurrent Sessions**: Multiple parallel browser instances
- **State Persistence**: Maintain session across operations

## Error Handling

- **Timeout Management**: Configurable timeouts for all operations
- **Element Detection**: Robust element finding and waiting
- **Network Issues**: Handling connectivity problems
- **JavaScript Errors**: Capturing and reporting script failures