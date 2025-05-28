from typing import Dict, Any, Optional, List
import asyncio
import os
import sys
import importlib.util
import json
import re
import unicodedata
import contextlib
from io import StringIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Critical: Set environment variables BEFORE importing anything else
# This prevents Playwright/Crawl4AI from sending debug output to stdout
os.environ['DEBUG'] = ''
os.environ['CRAWL4AI_VERBOSE'] = '0'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Force Playwright to use the correct browser path
# Override the browser path to the actual location
import glob

# First, try to find where browsers are actually installed
user_browser_path = os.path.expanduser(r'~\AppData\Local\ms-playwright')
alt_browser_path = r'C:\Users\usuario\AppData\Local\ms-playwright'

browser_base_path = None
if os.path.exists(user_browser_path):
    browser_base_path = user_browser_path
elif os.path.exists(alt_browser_path):
    browser_base_path = alt_browser_path

if browser_base_path:
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browser_base_path
    print(f"INFO: Set PLAYWRIGHT_BROWSERS_PATH to: {browser_base_path}", file=sys.stderr)
    
    # Also set other environment variables that Playwright might check
    os.environ['PLAYWRIGHT_DRIVER_PATH'] = browser_base_path
    
    # Find and log the specific chromium executable
    chromium_pattern = os.path.join(browser_base_path, 'chromium-*', 'chrome-win', 'chrome.exe')
    chromium_matches = glob.glob(chromium_pattern)
    if chromium_matches:
        chromium_path = chromium_matches[0]
        print(f"INFO: Found Chromium at: {chromium_path}", file=sys.stderr)
        # Set the specific executable path
        os.environ['PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH'] = chromium_path
    else:
        print("WARNING: Chromium executable not found in expected location", file=sys.stderr)
else:
    print("WARNING: No Playwright browser directory found", file=sys.stderr)
    # Set a fallback - don't override if already set
    if not os.environ.get('PLAYWRIGHT_BROWSERS_PATH'):
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '0'

# Browser automation settings from environment variables
PLAYWRIGHT_HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
PLAYWRIGHT_TIMEOUT = int(os.getenv("PLAYWRIGHT_TIMEOUT", "60000"))  # Increased default to 60 seconds
PLAYWRIGHT_DEFAULT_BROWSER = os.getenv("PLAYWRIGHT_DEFAULT_BROWSER", "chromium").lower()

# Check if Crawl4AI is available
CRAWL4AI_AVAILABLE = importlib.util.find_spec("crawl4ai") is not None

# Context manager to completely suppress stdout during library operations
@contextlib.contextmanager
def silence_stdout():
    """Completely silence stdout to prevent protocol contamination."""
    old_stdout = sys.stdout
    try:
        sys.stdout = StringIO()
        yield
    finally:
        sys.stdout = old_stdout

# Import Crawl4AI with stdout suppressed
if CRAWL4AI_AVAILABLE:
    try:
        with silence_stdout():
            from crawl4ai import AsyncWebCrawler
            from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
        print("INFO: Crawl4AI successfully imported", file=sys.stderr)
    except ImportError as e:
        print(f"WARNING: Error importing Crawl4AI: {str(e)}", file=sys.stderr)
        CRAWL4AI_AVAILABLE = False
else:
    print("WARNING: Crawl4AI not installed. Install with: pip install crawl4ai playwright && playwright install", file=sys.stderr)

def _normalize_unicode(text: str) -> str:
    """Normalize Unicode text for safe JSON serialization."""
    if not isinstance(text, str):
        return str(text)
    
    text = unicodedata.normalize('NFKD', text)
    
    # Replace problematic Unicode characters
    replacements = {
        '\u2193': '↓', '\u2191': '↑', '\u2192': '→', '\u2190': '←',
        '\u201c': '"', '\u201d': '"', '\u2018': "'", '\u2019': "'",
        '\u2013': '-', '\u2014': '--', '\u2026': '...',
        '\u00a0': ' ', '\u2022': '•', '\u00b7': '·',
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def _clean_text_for_json(text: str) -> str:
    """Clean text for safe JSON serialization."""
    if not isinstance(text, str):
        return str(text)
    
    text = _normalize_unicode(text)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    try:
        text.encode('utf-8').decode('utf-8')
    except UnicodeError:
        text = text.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
    
    return text

def _clean_dict_for_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively clean dictionary for JSON serialization."""
    cleaned = {}
    for key, value in data.items():
        try:
            if isinstance(value, str):
                cleaned[key] = _clean_text_for_json(value)
            elif isinstance(value, dict):
                cleaned[key] = _clean_dict_for_json(value)
            elif isinstance(value, list):
                cleaned_list = []
                for item in value:
                    if isinstance(item, str):
                        cleaned_list.append(_clean_text_for_json(item))
                    elif isinstance(item, dict):
                        cleaned_list.append(_clean_dict_for_json(item))
                    else:
                        cleaned_list.append(item)
                cleaned[key] = cleaned_list
            else:
                cleaned[key] = value
        except Exception:
            cleaned[key] = str(value)
    return cleaned

def _get_browser_config(headless: Optional[bool] = None, timeout: Optional[int] = None) -> 'BrowserConfig':
    """Get browser configuration using environment variables as defaults."""
    if not CRAWL4AI_AVAILABLE:
        return None
    
    # Use parameter values if provided, otherwise use environment defaults
    use_headless = headless if headless is not None else PLAYWRIGHT_HEADLESS
    use_timeout = timeout if timeout is not None else PLAYWRIGHT_TIMEOUT
    
    browser_args = [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-web-security',
        '--disable-features=VizDisplayCompositor',
        '--disable-background-timer-throttling',
        '--disable-backgrounding-occluded-windows',
        '--disable-renderer-backgrounding',
        f'--timeout={use_timeout}',
    ]
    
    # Force set browser path using environment variable approach
    import os
    import glob
    
    # Try to find the actual browser executable and set environment
    possible_browser_paths = [
        os.path.expanduser(r'~\AppData\Local\ms-playwright\chromium-*\chrome-win\chrome.exe'),
        r'C:\Users\usuario\AppData\Local\ms-playwright\chromium-*\chrome-win\chrome.exe',
        os.path.join(os.environ.get('LOCALAPPDATA', ''), r'ms-playwright\chromium-*\chrome-win\chrome.exe'),
    ]
    
    browser_executable = None
    for pattern in possible_browser_paths:
        matches = glob.glob(pattern)
        if matches:
            browser_executable = matches[0]  # Use the first match
            # Set the browser directory (parent of chrome-win)
            browser_dir = os.path.dirname(os.path.dirname(browser_executable))
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = os.path.dirname(browser_dir)
            print(f"INFO: Found browser executable at: {browser_executable}", file=sys.stderr)
            print(f"INFO: Set PLAYWRIGHT_BROWSERS_PATH to: {os.environ['PLAYWRIGHT_BROWSERS_PATH']}", file=sys.stderr)
            break
    
    if not browser_executable:
        print("WARNING: Could not find browser executable, using environment path", file=sys.stderr)
    
    # Use only supported BrowserConfig parameters
    config_params = {
        'headless': use_headless,
        'verbose': False,
        'browser_type': PLAYWRIGHT_DEFAULT_BROWSER,
        'extra_args': browser_args,
    }
    
    # Don't add timeout or executable_path - they're not supported by BrowserConfig
    print(f"INFO: Browser config - headless: {use_headless}, browser: {PLAYWRIGHT_DEFAULT_BROWSER}", file=sys.stderr)
    
    return BrowserConfig(**config_params)

async def crawl_webpage(
    url: str,
    output_format: str = "markdown",
    include_links: Optional[bool] = True,
    include_images: Optional[bool] = True,
    headless: Optional[bool] = None,  # Now uses env var as default
    extract_main_content: Optional[bool] = True,
    cache_enabled: Optional[bool] = True,
    wait_for_selector: Optional[str] = None,
    timeout: Optional[int] = None,  # New parameter using env var
    wait_time: Optional[int] = None,  # Deprecated
) -> Dict[str, Any]:
    """
    Crawl a webpage and extract its content in various formats.
    Uses environment variables for browser configuration.
    
    Args:
        url: URL of the webpage to crawl (required)
        output_format: Format: "markdown", "html", "text", or "all" (default: "markdown")
        include_links: Include links in output (default: True)
        include_images: Include images in output (default: True)
        headless: Run browser in headless mode (default: from PLAYWRIGHT_HEADLESS env var)
        extract_main_content: Extract only main content (default: True)
        cache_enabled: Use cache if available (default: True)
        wait_for_selector: CSS selector to wait for (optional)
        timeout: Request timeout in milliseconds (default: from PLAYWRIGHT_TIMEOUT env var)
        wait_time: [DEPRECATED] Not supported (optional)
    
    Returns:
        Dictionary containing extracted content and metadata
    """
    print(f"INFO: crawl_webpage called with URL: {url}", file=sys.stderr)
    print(f"INFO: Using browser: {PLAYWRIGHT_DEFAULT_BROWSER}, headless: {headless if headless is not None else PLAYWRIGHT_HEADLESS}, timeout: {timeout if timeout is not None else PLAYWRIGHT_TIMEOUT}ms", file=sys.stderr)
    
    if not CRAWL4AI_AVAILABLE:
        return {
            "error": "Crawl4AI is not installed. Please install it with 'pip install crawl4ai'.",
            "status": "error"
        }
    
    if wait_time is not None:
        print("WARNING: 'wait_time' parameter is deprecated and will be ignored.", file=sys.stderr)
    
    try:
        # Get browser configuration using environment variables
        browser_config = _get_browser_config(headless=headless, timeout=timeout)
        
        # Configure crawler settings
        crawler_config_params = {
            "cache_mode": CacheMode.ENABLED if cache_enabled else CacheMode.BYPASS,
            "word_count_threshold": 10 if extract_main_content else 0,
            "exclude_external_links": not include_links,
            "remove_overlay_elements": True,
            "process_iframes": False,  # Disable to reduce complexity
        }
        
        # Add wait configuration if specified
        if wait_for_selector:
            crawler_config_params["wait_for"] = wait_for_selector
        
        # Add timeout configuration
        use_timeout = timeout if timeout is not None else PLAYWRIGHT_TIMEOUT
        try:
            # Timeout should be in milliseconds for Crawl4AI
            crawler_config_params["page_timeout"] = use_timeout  # Keep in milliseconds
            print(f"INFO: Set page timeout to {use_timeout}ms", file=sys.stderr)
        except Exception as e:
            print(f"INFO: Using default timeout settings: {str(e)}", file=sys.stderr)
            
        run_config = CrawlerRunConfig(**crawler_config_params)
        
        # Execute crawling with stdout completely suppressed
        with silence_stdout():
            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(url=url, config=run_config)
        
        if not result.success:
            error_msg = getattr(result, 'error_message', 'Crawl failed')
            return {
                "error": f"Crawl failed: {_clean_text_for_json(str(error_msg))}",
                "status_code": getattr(result, 'status_code', None),
                "browser_config": {
                    "browser": PLAYWRIGHT_DEFAULT_BROWSER,
                    "headless": headless if headless is not None else PLAYWRIGHT_HEADLESS,
                    "timeout": use_timeout
                },
                "status": "error"
            }
        
        # Build response
        response = {
            "url": _clean_text_for_json(url),
            "status_code": getattr(result, 'status_code', 200),
            "browser_config": {
                "browser": PLAYWRIGHT_DEFAULT_BROWSER,
                "headless": headless if headless is not None else PLAYWRIGHT_HEADLESS,
                "timeout": use_timeout
            },
            "status": "success"
        }
        
        # Add metadata safely
        if hasattr(result, 'metadata') and result.metadata:
            try:
                cleaned_metadata = _clean_dict_for_json(result.metadata)
                response["metadata"] = cleaned_metadata
                if 'title' in cleaned_metadata:
                    response["title"] = cleaned_metadata['title']
            except Exception as e:
                print(f"WARNING: Metadata processing error: {str(e)}", file=sys.stderr)
        
        # Add content based on format
        try:
            if output_format == "markdown" or output_format == "all":
                if hasattr(result, 'markdown') and result.markdown:
                    # Try to get the cleanest markdown version
                    if hasattr(result.markdown, 'fit_markdown') and result.markdown.fit_markdown:
                        response["markdown"] = _clean_text_for_json(result.markdown.fit_markdown)
                    elif hasattr(result.markdown, 'raw_markdown') and result.markdown.raw_markdown:
                        response["markdown"] = _clean_text_for_json(result.markdown.raw_markdown)
                    else:
                        response["markdown"] = _clean_text_for_json(str(result.markdown))
            
            if output_format == "html" or output_format == "all":
                if extract_main_content and hasattr(result, 'cleaned_html') and result.cleaned_html:
                    response["html"] = _clean_text_for_json(result.cleaned_html)
                elif hasattr(result, 'html') and result.html:
                    response["html"] = _clean_text_for_json(result.html)
            
            if output_format == "text" or output_format == "all":
                if hasattr(result, 'text') and result.text:
                    response["text"] = _clean_text_for_json(result.text)
                elif response.get("markdown"):
                    response["text"] = response["markdown"]  # Use markdown as fallback
            
            # Add links if requested
            if include_links and hasattr(result, 'links') and result.links:
                try:
                    cleaned_links = []
                    for link in result.links[:20]:  # Limit to prevent oversized responses
                        if isinstance(link, dict):
                            cleaned_links.append(_clean_dict_for_json(link))
                        else:
                            cleaned_links.append(_clean_text_for_json(str(link)))
                    response["links"] = cleaned_links
                except Exception as e:
                    print(f"WARNING: Links processing error: {str(e)}", file=sys.stderr)
            
            # Add images if requested
            if include_images and hasattr(result, 'media') and result.media:
                try:
                    if 'images' in result.media:
                        images = result.media['images'][:10]  # Limit to prevent oversized responses
                        cleaned_images = []
                        for img in images:
                            if isinstance(img, dict):
                                cleaned_images.append(_clean_dict_for_json(img))
                            else:
                                cleaned_images.append(_clean_text_for_json(str(img)))
                        response["images"] = cleaned_images
                except Exception as e:
                    print(f"WARNING: Images processing error: {str(e)}", file=sys.stderr)
        
        except Exception as e:
            print(f"WARNING: Content processing error: {str(e)}", file=sys.stderr)
            response["content_warning"] = "Some content could not be processed"
        
        # Validate JSON serialization
        try:
            json.dumps(response, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            print(f"WARNING: JSON serialization failed: {str(e)}", file=sys.stderr)
            # Return minimal safe response
            return {
                "url": _clean_text_for_json(url),
                "status": "success",
                "warning": "Content required sanitization for JSON compatibility",
                "title": response.get("title", ""),
                "content_preview": str(response.get("markdown", response.get("text", "")))[:200],
                "browser_config": response.get("browser_config", {})
            }
        
        return response
        
    except Exception as e:
        error_msg = f"Crawl execution failed: {str(e)}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return {
            "error": _clean_text_for_json(error_msg),
            "browser_config": {
                "browser": PLAYWRIGHT_DEFAULT_BROWSER,
                "headless": headless if headless is not None else PLAYWRIGHT_HEADLESS,
                "timeout": timeout if timeout is not None else PLAYWRIGHT_TIMEOUT
            },
            "status": "error"
        }

async def crawl_multiple_webpages(
    urls: List[str],
    output_format: str = "markdown",
    include_links: Optional[bool] = True,
    include_images: Optional[bool] = True,
    headless: Optional[bool] = None,  # Now uses env var as default
    extract_main_content: Optional[bool] = True,
    max_concurrent: Optional[int] = 3,  # Reduced for stability
    timeout: Optional[int] = None  # New parameter using env var
) -> Dict[str, Any]:
    """
    Crawl multiple webpages with environment variable configuration.
    
    Args:
        urls: List of URLs to crawl (required)
        output_format: Output format (default: "markdown")
        include_links: Include links (default: True)
        include_images: Include images (default: True)  
        headless: Headless mode (default: from PLAYWRIGHT_HEADLESS env var)
        extract_main_content: Extract main content only (default: True)
        max_concurrent: Max concurrent crawls (default: 3)
        timeout: Request timeout in milliseconds (default: from PLAYWRIGHT_TIMEOUT env var)
    
    Returns:
        Dictionary with results for each URL
    """
    print(f"INFO: crawl_multiple_webpages called with {len(urls)} URLs", file=sys.stderr)
    print(f"INFO: Using browser: {PLAYWRIGHT_DEFAULT_BROWSER}, max_concurrent: {max_concurrent}, timeout: {timeout if timeout is not None else PLAYWRIGHT_TIMEOUT}ms", file=sys.stderr)
    
    if not CRAWL4AI_AVAILABLE:
        return {
            "error": "Crawl4AI is not installed.",
            "status": "error"
        }
    
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def _crawl_with_semaphore(url):
        async with semaphore:
            return await crawl_webpage(
                url=url,
                output_format=output_format,
                include_links=include_links,
                include_images=include_images,
                headless=headless,
                extract_main_content=extract_main_content,
                timeout=timeout
            )
    
    try:
        tasks = [_crawl_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = {}
        successful = 0
        failed = 0
        
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                processed_results[_clean_text_for_json(url)] = {
                    "error": f"Exception: {str(result)}",
                    "status": "error"
                }
                failed += 1
            else:
                processed_results[_clean_text_for_json(url)] = result
                if result.get("status") == "success":
                    successful += 1
                else:
                    failed += 1
        
        response = {
            "results": processed_results,
            "count": len(urls),
            "successful": successful,
            "failed": failed,
            "browser_config": {
                "browser": PLAYWRIGHT_DEFAULT_BROWSER,
                "headless": headless if headless is not None else PLAYWRIGHT_HEADLESS,
                "timeout": timeout if timeout is not None else PLAYWRIGHT_TIMEOUT,
                "max_concurrent": max_concurrent
            },
            "status": "success"
        }
        
        return response
        
    except Exception as e:
        error_msg = f"Multiple crawl failed: {str(e)}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return {
            "error": _clean_text_for_json(error_msg),
            "status": "error"
        }

async def extract_structured_data(
    url: str,
    schema: Dict[str, Any],
    headless: Optional[bool] = None,  # Now uses env var as default
    wait_for_selector: Optional[str] = None,
    timeout: Optional[int] = None  # New parameter using env var
) -> Dict[str, Any]:
    """
    Extract structured data with environment variable configuration.
    
    Args:
        url: URL to crawl (required)
        schema: CSS extraction schema (required)
        headless: Headless mode (default: from PLAYWRIGHT_HEADLESS env var)
        wait_for_selector: CSS selector to wait for (optional)
        timeout: Request timeout in milliseconds (default: from PLAYWRIGHT_TIMEOUT env var)
    
    Returns:
        Dictionary with extracted structured data
    """
    print(f"INFO: extract_structured_data called with URL: {url}", file=sys.stderr)
    print(f"INFO: Using browser: {PLAYWRIGHT_DEFAULT_BROWSER}, headless: {headless if headless is not None else PLAYWRIGHT_HEADLESS}, timeout: {timeout if timeout is not None else PLAYWRIGHT_TIMEOUT}ms", file=sys.stderr)
    
    if not CRAWL4AI_AVAILABLE:
        return {
            "error": "Crawl4AI is not installed.",
            "status": "error"
        }
    
    try:
        with silence_stdout():
            from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
        
        browser_config = _get_browser_config(headless=headless, timeout=timeout)
        extraction_strategy = JsonCssExtractionStrategy(schema)
        
        crawler_config_params = {
            "extraction_strategy": extraction_strategy,
            "cache_mode": CacheMode.ENABLED
        }
        
        if wait_for_selector:
            crawler_config_params["wait_for"] = wait_for_selector
        
        # Add timeout configuration
        use_timeout = timeout if timeout is not None else PLAYWRIGHT_TIMEOUT
        try:
            crawler_config_params["page_timeout"] = use_timeout
        except Exception:
            pass  # Some versions might not support this parameter
            
        run_config = CrawlerRunConfig(**crawler_config_params)
        
        with silence_stdout():
            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(url=url, config=run_config)
        
        if not result.success:
            error_msg = getattr(result, 'error_message', 'Extraction failed')
            return {
                "error": f"Extraction failed: {_clean_text_for_json(str(error_msg))}",
                "browser_config": {
                    "browser": PLAYWRIGHT_DEFAULT_BROWSER,
                    "headless": headless if headless is not None else PLAYWRIGHT_HEADLESS,
                    "timeout": use_timeout
                },
                "status": "error"
            }
        
        # Extract data
        extracted_data = None
        if hasattr(result, 'extracted_content') and result.extracted_content:
            extracted_data = result.extracted_content
        elif hasattr(result, 'extraction_result') and result.extraction_result:
            extracted_data = result.extraction_result
        
        if extracted_data:
            response = {
                "url": _clean_text_for_json(url),
                "data": _clean_dict_for_json(extracted_data) if isinstance(extracted_data, dict) else extracted_data,
                "browser_config": {
                    "browser": PLAYWRIGHT_DEFAULT_BROWSER,
                    "headless": headless if headless is not None else PLAYWRIGHT_HEADLESS,
                    "timeout": use_timeout
                },
                "status": "success"
            }
            
            # Validate JSON
            try:
                json.dumps(response, ensure_ascii=False)
            except (TypeError, ValueError) as e:
                print(f"WARNING: Structured data JSON serialization failed: {str(e)}", file=sys.stderr)
                return {
                    "url": _clean_text_for_json(url),
                    "warning": "Extracted data required sanitization",
                    "data_type": str(type(extracted_data)),
                    "browser_config": response.get("browser_config", {}),
                    "status": "success"
                }
            
            return response
        else:
            return {
                "url": _clean_text_for_json(url),
                "error": "No structured data extracted with provided schema",
                "browser_config": {
                    "browser": PLAYWRIGHT_DEFAULT_BROWSER,
                    "headless": headless if headless is not None else PLAYWRIGHT_HEADLESS,
                    "timeout": use_timeout
                },
                "status": "error"
            }
            
    except Exception as e:
        error_msg = f"Structured extraction failed: {str(e)}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return {
            "error": _clean_text_for_json(error_msg),
            "status": "error"
        }

def register(mcp_instance):
    """Register Crawl4AI tools with MCP server using environment variable configuration."""
    if CRAWL4AI_AVAILABLE:
        mcp_instance.tool()(crawl_webpage)
        mcp_instance.tool()(crawl_multiple_webpages)
        mcp_instance.tool()(extract_structured_data)
        print("INFO: Crawl4AI tools registered with environment variable configuration", file=sys.stderr)
        print(f"INFO: Default browser: {PLAYWRIGHT_DEFAULT_BROWSER}, headless: {PLAYWRIGHT_HEADLESS}, timeout: {PLAYWRIGHT_TIMEOUT}ms", file=sys.stderr)
    else:
        print("WARNING: Crawl4AI tools not registered - Crawl4AI not installed", file=sys.stderr)