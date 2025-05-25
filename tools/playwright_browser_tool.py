# tools/playwright_browser_tool.py
from typing import Dict, Any, Optional, List
import asyncio
import os
import importlib.util
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

# Check if Playwright is installed
PLAYWRIGHT_AVAILABLE = importlib.util.find_spec("playwright") is not None

if PLAYWRIGHT_AVAILABLE:
    try:
        from playwright.async_api import async_playwright, Browser, Page, BrowserContext
        print("INFO: Playwright successfully imported")
    except ImportError as e:
        print(f"WARNING: Error importing Playwright: {str(e)}")
        PLAYWRIGHT_AVAILABLE = False
else:
    print("WARNING: Playwright is not installed. Browser automation tools will not be available.")
    print("To install it, run: pip install playwright && playwright install")

# Browser context storage for session management
_browser_contexts = {}
_active_pages = {}

async def launch_browser(
    browser_type: str = "chromium",
    headless: bool = True,
    context_id: str = "default"
) -> Dict[str, Any]:
    """
    Launch a new browser instance with a context.
    
    Args:
        browser_type: Browser type - "chromium", "firefox", "webkit" (default: "chromium")
        headless: Whether to run in headless mode (default: True)
        context_id: Unique identifier for this browser context (default: "default")
    
    Returns:
        Dictionary containing browser launch status and context information
    """
    print(f"INFO: launch_browser called with type: {browser_type}, headless: {headless}")
    
    if not PLAYWRIGHT_AVAILABLE:
        return {
            "error": "Playwright is not installed. Please install it with 'pip install playwright && playwright install'.",
            "status": "error"
        }
    
    try:
        if context_id in _browser_contexts:
            return {
                "message": f"Browser context '{context_id}' already exists",
                "context_id": context_id,
                "status": "success"
            }
        
        playwright = await async_playwright().start()
        
        # Choose browser type
        if browser_type == "firefox":
            browser = await playwright.firefox.launch(headless=headless)
        elif browser_type == "webkit":
            browser = await playwright.webkit.launch(headless=headless)
        else:  # Default to chromium
            browser = await playwright.chromium.launch(headless=headless)
        
        # Create browser context
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Store context for later use
        _browser_contexts[context_id] = {
            "playwright": playwright,
            "browser": browser,
            "context": context
        }
        
        return {
            "context_id": context_id,
            "browser_type": browser_type,
            "headless": headless,
            "message": "Browser launched successfully",
            "status": "success"
        }
        
    except Exception as e:
        print(f"ERROR: launch_browser failed: {str(e)}")
        return {
            "error": f"Failed to launch browser: {str(e)}",
            "status": "error"
        }

async def navigate_to_page(
    url: str,
    context_id: str = "default",
    wait_for_load_state: str = "networkidle",
    timeout: int = 30000
) -> Dict[str, Any]:
    """
    Navigate to a URL in the browser context.
    
    Args:
        url: URL to navigate to (required)
        context_id: Browser context identifier (default: "default")
        wait_for_load_state: Load state to wait for - "load", "domcontentloaded", "networkidle" (default: "networkidle")
        timeout: Timeout in milliseconds (default: 30000)
    
    Returns:
        Dictionary containing navigation results and page information
    """
    print(f"INFO: navigate_to_page called with URL: {url}")
    
    if not PLAYWRIGHT_AVAILABLE:
        return {
            "error": "Playwright is not installed.",
            "status": "error"
        }
    
    try:
        if context_id not in _browser_contexts:
            # Auto-launch browser if not exists
            launch_result = await launch_browser(context_id=context_id)
            if launch_result.get("status") != "success":
                return launch_result
        
        context = _browser_contexts[context_id]["context"]
        
        # Create new page or reuse existing
        if context_id in _active_pages:
            page = _active_pages[context_id]
        else:
            page = await context.new_page()
            _active_pages[context_id] = page
        
        # Navigate to URL
        response = await page.goto(url, timeout=timeout, wait_until=wait_for_load_state)
        
        # Get page information
        title = await page.title()
        current_url = page.url
        
        return {
            "url": current_url,
            "title": title,
            "status_code": response.status if response else None,
            "context_id": context_id,
            "wait_for_load_state": wait_for_load_state,
            "status": "success"
        }
        
    except Exception as e:
        print(f"ERROR: navigate_to_page failed: {str(e)}")
        return {
            "error": f"Navigation failed: {str(e)}",
            "status": "error"
        }

async def get_page_content(
    context_id: str = "default",
    content_type: str = "text",
    selector: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get content from the current page.
    
    Args:
        context_id: Browser context identifier (default: "default")
        content_type: Type of content - "text", "html", "markdown", "screenshot" (default: "text")
        selector: CSS selector to get content from specific element (optional)
    
    Returns:
        Dictionary containing page content
    """
    print(f"INFO: get_page_content called with type: {content_type}")
    
    if not PLAYWRIGHT_AVAILABLE:
        return {
            "error": "Playwright is not installed.",
            "status": "error"
        }
    
    try:
        if context_id not in _active_pages:
            return {
                "error": f"No active page in context '{context_id}'. Please navigate to a page first.",
                "status": "error"
            }
        
        page = _active_pages[context_id]
        
        if content_type == "screenshot":
            # Take screenshot
            screenshot_bytes = await page.screenshot(
                type="png",
                full_page=True if not selector else False
            )
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode()
            
            return {
                "content_type": "screenshot",
                "screenshot_base64": screenshot_base64,
                "url": page.url,
                "status": "success"
            }
        
        # Get element or page content
        if selector:
            element = await page.wait_for_selector(selector, timeout=10000)
            if content_type == "text":
                content = await element.text_content()
            else:  # html
                content = await element.inner_html()
        else:
            if content_type == "text":
                content = await page.text_content("body")
            elif content_type == "html":
                content = await page.content()
            elif content_type == "markdown":
                # Convert to markdown using simple heuristics
                text_content = await page.text_content("body")
                title = await page.title()
                content = f"# {title}\n\n{text_content}"
            else:
                content = await page.content()
        
        return {
            "content": content,
            "content_type": content_type,
            "selector": selector,
            "url": page.url,
            "title": await page.title(),
            "status": "success"
        }
        
    except Exception as e:
        print(f"ERROR: get_page_content failed: {str(e)}")
        return {
            "error": f"Failed to get page content: {str(e)}",
            "status": "error"
        }

async def click_element(
    selector: str,
    context_id: str = "default",
    wait_for_navigation: bool = False,
    timeout: int = 10000
) -> Dict[str, Any]:
    """
    Click on an element in the page.
    
    Args:
        selector: CSS selector for the element to click (required)
        context_id: Browser context identifier (default: "default")
        wait_for_navigation: Whether to wait for navigation after click (default: False)
        timeout: Timeout in milliseconds (default: 10000)
    
    Returns:
        Dictionary containing click operation results
    """
    print(f"INFO: click_element called with selector: {selector}")
    
    if not PLAYWRIGHT_AVAILABLE:
        return {
            "error": "Playwright is not installed.",
            "status": "error"
        }
    
    try:
        if context_id not in _active_pages:
            return {
                "error": f"No active page in context '{context_id}'. Please navigate to a page first.",
                "status": "error"
            }
        
        page = _active_pages[context_id]
        
        # Wait for element and click
        if wait_for_navigation:
            async with page.expect_navigation(timeout=timeout):
                await page.click(selector, timeout=timeout)
        else:
            await page.click(selector, timeout=timeout)
        
        return {
            "selector": selector,
            "context_id": context_id,
            "url": page.url,
            "title": await page.title(),
            "wait_for_navigation": wait_for_navigation,
            "status": "success"
        }
        
    except Exception as e:
        print(f"ERROR: click_element failed: {str(e)}")
        return {
            "error": f"Failed to click element: {str(e)}",
            "status": "error"
        }

async def fill_form_field(
    selector: str,
    value: str,
    context_id: str = "default",
    clear_first: bool = True,
    timeout: int = 10000
) -> Dict[str, Any]:
    """
    Fill a form field with text.
    
    Args:
        selector: CSS selector for the input element (required)
        value: Text value to fill (required)
        context_id: Browser context identifier (default: "default")
        clear_first: Whether to clear the field before filling (default: True)
        timeout: Timeout in milliseconds (default: 10000)
    
    Returns:
        Dictionary containing fill operation results
    """
    print(f"INFO: fill_form_field called with selector: {selector}")
    
    if not PLAYWRIGHT_AVAILABLE:
        return {
            "error": "Playwright is not installed.",
            "status": "error"
        }
    
    try:
        if context_id not in _active_pages:
            return {
                "error": f"No active page in context '{context_id}'. Please navigate to a page first.",
                "status": "error"
            }
        
        page = _active_pages[context_id]
        
        # Wait for element
        await page.wait_for_selector(selector, timeout=timeout)
        
        if clear_first:
            await page.fill(selector, "")  # Clear first
        
        # Fill the field
        await page.fill(selector, value)
        
        return {
            "selector": selector,
            "value": value,
            "context_id": context_id,
            "clear_first": clear_first,
            "url": page.url,
            "status": "success"
        }
        
    except Exception as e:
        print(f"ERROR: fill_form_field failed: {str(e)}")
        return {
            "error": f"Failed to fill form field: {str(e)}",
            "status": "error"
        }

async def wait_for_element(
    selector: str,
    context_id: str = "default",
    state: str = "visible",
    timeout: int = 10000
) -> Dict[str, Any]:
    """
    Wait for an element to appear or reach a specific state.
    
    Args:
        selector: CSS selector for the element (required)
        context_id: Browser context identifier (default: "default")
        state: Element state to wait for - "attached", "detached", "visible", "hidden" (default: "visible")
        timeout: Timeout in milliseconds (default: 10000)
    
    Returns:
        Dictionary containing wait operation results
    """
    print(f"INFO: wait_for_element called with selector: {selector}, state: {state}")
    
    if not PLAYWRIGHT_AVAILABLE:
        return {
            "error": "Playwright is not installed.",
            "status": "error"
        }
    
    try:
        if context_id not in _active_pages:
            return {
                "error": f"No active page in context '{context_id}'. Please navigate to a page first.",
                "status": "error"
            }
        
        page = _active_pages[context_id]
        
        # Wait for element state
        await page.wait_for_selector(selector, state=state, timeout=timeout)
        
        # Get element info
        element = await page.query_selector(selector)
        element_text = await element.text_content() if element else None
        
        return {
            "selector": selector,
            "state": state,
            "element_text": element_text,
            "context_id": context_id,
            "url": page.url,
            "status": "success"
        }
        
    except Exception as e:
        print(f"ERROR: wait_for_element failed: {str(e)}")
        return {
            "error": f"Failed to wait for element: {str(e)}",
            "status": "error"
        }

async def execute_javascript(
    script: str,
    context_id: str = "default"
) -> Dict[str, Any]:
    """
    Execute JavaScript code in the browser page.
    
    Args:
        script: JavaScript code to execute (required)
        context_id: Browser context identifier (default: "default")
    
    Returns:
        Dictionary containing script execution results
    """
    print(f"INFO: execute_javascript called")
    
    if not PLAYWRIGHT_AVAILABLE:
        return {
            "error": "Playwright is not installed.",
            "status": "error"
        }
    
    try:
        if context_id not in _active_pages:
            return {
                "error": f"No active page in context '{context_id}'. Please navigate to a page first.",
                "status": "error"
            }
        
        page = _active_pages[context_id]
        
        # Execute JavaScript
        result = await page.evaluate(script)
        
        return {
            "script": script,
            "result": result,
            "context_id": context_id,
            "url": page.url,
            "status": "success"
        }
        
    except Exception as e:
        print(f"ERROR: execute_javascript failed: {str(e)}")
        return {
            "error": f"Failed to execute JavaScript: {str(e)}",
            "status": "error"
        }

async def get_accessibility_snapshot(
    context_id: str = "default",
    interesting_only: bool = True
) -> Dict[str, Any]:
    """
    Get accessibility tree snapshot of the current page.
    This provides a structured view of the page that's LLM-friendly.
    
    Args:
        context_id: Browser context identifier (default: "default")
        interesting_only: Whether to include only interesting elements (default: True)
    
    Returns:
        Dictionary containing accessibility tree data
    """
    print(f"INFO: get_accessibility_snapshot called")
    
    if not PLAYWRIGHT_AVAILABLE:
        return {
            "error": "Playwright is not installed.",
            "status": "error"
        }
    
    try:
        if context_id not in _active_pages:
            return {
                "error": f"No active page in context '{context_id}'. Please navigate to a page first.",
                "status": "error"
            }
        
        page = _active_pages[context_id]
        
        # Get accessibility snapshot
        snapshot = await page.accessibility.snapshot(interesting_only=interesting_only)
        
        return {
            "accessibility_tree": snapshot,
            "context_id": context_id,
            "url": page.url,
            "title": await page.title(),
            "interesting_only": interesting_only,
            "status": "success"
        }
        
    except Exception as e:
        print(f"ERROR: get_accessibility_snapshot failed: {str(e)}")
        return {
            "error": f"Failed to get accessibility snapshot: {str(e)}",
            "status": "error"
        }

async def close_browser_context(
    context_id: str = "default"
) -> Dict[str, Any]:
    """
    Close a browser context and clean up resources.
    
    Args:
        context_id: Browser context identifier to close (default: "default")
    
    Returns:
        Dictionary containing cleanup results
    """
    print(f"INFO: close_browser_context called for context: {context_id}")
    
    if not PLAYWRIGHT_AVAILABLE:
        return {
            "error": "Playwright is not installed.",
            "status": "error"
        }
    
    try:
        if context_id not in _browser_contexts:
            return {
                "message": f"Browser context '{context_id}' not found or already closed",
                "status": "success"
            }
        
        # Clean up active page
        if context_id in _active_pages:
            del _active_pages[context_id]
        
        # Close browser and context
        browser_data = _browser_contexts[context_id]
        await browser_data["context"].close()
        await browser_data["browser"].close()
        await browser_data["playwright"].stop()
        
        # Remove from storage
        del _browser_contexts[context_id]
        
        return {
            "context_id": context_id,
            "message": "Browser context closed successfully",
            "status": "success"
        }
        
    except Exception as e:
        print(f"ERROR: close_browser_context failed: {str(e)}")
        return {
            "error": f"Failed to close browser context: {str(e)}",
            "status": "error"
        }

async def list_browser_contexts() -> Dict[str, Any]:
    """
    List all active browser contexts.
    
    Returns:
        Dictionary containing list of active contexts
    """
    print("INFO: list_browser_contexts called")
    
    contexts = []
    for context_id in _browser_contexts.keys():
        has_active_page = context_id in _active_pages
        current_url = None
        current_title = None
        
        if has_active_page:
            try:
                page = _active_pages[context_id]
                current_url = page.url
                current_title = await page.title()
            except:
                pass
        
        contexts.append({
            "context_id": context_id,
            "has_active_page": has_active_page,
            "current_url": current_url,
            "current_title": current_title
        })
    
    return {
        "active_contexts": contexts,
        "total_contexts": len(contexts),
        "status": "success"
    }

def register(mcp_instance):
    """Register the Playwright browser tools with the MCP server"""
    if PLAYWRIGHT_AVAILABLE:
        # Core browser operations
        mcp_instance.tool()(launch_browser)
        mcp_instance.tool()(navigate_to_page)
        mcp_instance.tool()(get_page_content)
        mcp_instance.tool()(close_browser_context)
        
        # Interaction tools
        mcp_instance.tool()(click_element)
        mcp_instance.tool()(fill_form_field)
        mcp_instance.tool()(wait_for_element)
        
        # Advanced features
        mcp_instance.tool()(execute_javascript)
        mcp_instance.tool()(get_accessibility_snapshot)
        
        # Utility functions
        mcp_instance.tool()(list_browser_contexts)
        
        print("INFO: Playwright browser tools registered successfully")
    else:
        print("WARNING: Playwright browser tools were not registered because Playwright is not installed.")