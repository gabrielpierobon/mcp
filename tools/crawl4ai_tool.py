from typing import Dict, Any, Optional, List, Union
import asyncio
import os
import importlib.util
import json
import re
from dotenv import load_dotenv
import logging
import sys

# Try to load environment variables from .env file
load_dotenv()

# Configure logging to stderr instead of stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Important: use stderr, not stdout
)
logger = logging.getLogger(__name__)

# Check if Crawl4AI is installed using importlib.util.find_spec
CRAWL4AI_AVAILABLE = importlib.util.find_spec("crawl4ai") is not None

if CRAWL4AI_AVAILABLE:
    try:
        # Import Crawl4AI components
        from crawl4ai import AsyncWebCrawler
        from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
        logger.info("Crawl4AI successfully imported")
    except ImportError as e:
        logger.warning(f"Error importing Crawl4AI components: {str(e)}")
        CRAWL4AI_AVAILABLE = False
else:
    logger.warning("Crawl4AI is not installed. The web crawler tool will not be available.")
    logger.warning("To install it, run: pip install crawl4ai playwright && playwright install")

def _clean_text_for_json(text: str) -> str:
    """Clean text to ensure it's safe for JSON serialization."""
    if not isinstance(text, str):
        return str(text)
    
    # Remove or replace problematic characters
    # Remove null bytes and other control characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    # Replace smart quotes and other unicode characters that might cause issues
    replacements = {
        '\u201c': '"',  # Left double quotation mark
        '\u201d': '"',  # Right double quotation mark
        '\u2018': "'",  # Left single quotation mark
        '\u2019': "'",  # Right single quotation mark
        '\u2013': '-',  # En dash
        '\u2014': '--', # Em dash
        '\u2026': '...', # Horizontal ellipsis
        '\u00a0': ' ',  # Non-breaking space
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Ensure the text is valid UTF-8
    try:
        text.encode('utf-8')
    except UnicodeEncodeError:
        # If encoding fails, replace problematic characters
        text = text.encode('utf-8', errors='replace').decode('utf-8')
    
    return text

def _clean_dict_for_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively clean a dictionary to ensure JSON serialization works."""
    cleaned = {}
    for key, value in data.items():
        if isinstance(value, str):
            cleaned[key] = _clean_text_for_json(value)
        elif isinstance(value, dict):
            cleaned[key] = _clean_dict_for_json(value)
        elif isinstance(value, list):
            cleaned[key] = [_clean_text_for_json(item) if isinstance(item, str) else item for item in value]
        else:
            cleaned[key] = value
    return cleaned

async def crawl_webpage(
    url: str,
    output_format: str = "markdown",
    include_links: Optional[bool] = True,
    include_images: Optional[bool] = True,
    headless: Optional[bool] = True,
    extract_main_content: Optional[bool] = True,
    cache_enabled: Optional[bool] = True,
    wait_for_selector: Optional[str] = None,
    wait_time: Optional[int] = None,  # Deprecated - not supported in current Crawl4AI version
) -> Dict[str, Any]:
    """
    Crawl a webpage and extract its content in various formats.
    
    Args:
        url: URL of the webpage to crawl (required)
        output_format: Format of the output: "markdown", "html", "text", or "all" (default: "markdown")
        include_links: Whether to include links in the output (default: True)
        include_images: Whether to include images in the output (default: True)
        headless: Whether to run the browser in headless mode (default: True)
        extract_main_content: Whether to extract only the main content or the entire page (default: True)
        cache_enabled: Whether to use cache if available (default: True)
        wait_for_selector: CSS selector to wait for before extracting content (optional)
        wait_time: [DEPRECATED] Additional time in milliseconds to wait after page load (not supported in current version)
        
    Returns:
        Dictionary containing the extracted content and metadata
    """
    logger.info(f"crawl_webpage called with URL: {url}, format: {output_format}")
    
    if wait_time is not None:
        logger.warning("'wait_time' parameter is not supported in the current Crawl4AI version and will be ignored.")
    
    if not CRAWL4AI_AVAILABLE:
        return {
            "error": "Crawl4AI is not installed. Please install it with 'pip install crawl4ai'.",
            "status": "error"
        }
    
    try:
        # Configure browser settings
        browser_config = BrowserConfig(
            headless=headless,
            verbose=True
        )
        
        # Configure crawler settings
        cache_mode = CacheMode.ENABLED if cache_enabled else CacheMode.BYPASS
        
        crawler_config_params = {
            "cache_mode": cache_mode,
            "word_count_threshold": 10 if extract_main_content else 0,  # Filter out small text blocks if extracting main content
            "exclude_external_links": not include_links,
            "remove_overlay_elements": True,  # Remove popups and overlays
            "process_iframes": True,  # Process iframe content
        }
        
        # Add wait_for_selector if provided
        if wait_for_selector:
            crawler_config_params["wait_for"] = wait_for_selector
            
        run_config = CrawlerRunConfig(**crawler_config_params)
        
        # Initialize and run the crawler
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            
            if not result.success:
                error_msg = getattr(result, 'error_message', 'Unknown error')
                return {
                    "error": f"Crawl failed: {_clean_text_for_json(str(error_msg))}",
                    "status_code": getattr(result, 'status_code', None),
                    "status": "error"
                }
            
            # Prepare response based on requested format
            response = {
                "url": _clean_text_for_json(url),
                "status_code": getattr(result, 'status_code', None),
                "status": "success"
            }
            
            # Add page metadata if available
            if hasattr(result, 'metadata') and result.metadata:
                # Clean metadata for JSON serialization
                cleaned_metadata = _clean_dict_for_json(result.metadata)
                response["metadata"] = cleaned_metadata
                # Add title from metadata if available
                if 'title' in cleaned_metadata:
                    response["title"] = cleaned_metadata['title']
            
            # Add content based on requested format
            if output_format == "markdown" or output_format == "all":
                if hasattr(result, 'markdown') and result.markdown:
                    response["markdown"] = _clean_text_for_json(str(result.markdown))
            
            if output_format == "html" or output_format == "all":
                if extract_main_content and hasattr(result, 'cleaned_html') and result.cleaned_html:
                    response["html"] = _clean_text_for_json(result.cleaned_html)
                elif hasattr(result, 'html') and result.html:
                    response["html"] = _clean_text_for_json(result.html)
            
            if output_format == "text" or output_format == "all":
                if hasattr(result, 'text') and result.text:
                    response["text"] = _clean_text_for_json(result.text)
                elif hasattr(result, 'markdown') and result.markdown:
                    # If no plain text is available, use the markdown as a fallback
                    response["text"] = _clean_text_for_json(str(result.markdown))
            
            # Include links if requested and available
            if include_links and hasattr(result, 'links') and result.links:
                # Clean links for JSON serialization
                cleaned_links = []
                for link in result.links:
                    if isinstance(link, dict):
                        cleaned_links.append(_clean_dict_for_json(link))
                    else:
                        cleaned_links.append(_clean_text_for_json(str(link)))
                response["links"] = cleaned_links
                
            # Include images if requested and available
            if include_images and hasattr(result, 'media') and result.media and 'images' in result.media:
                images = result.media.get('images', [])
                cleaned_images = []
                for img in images:
                    if isinstance(img, dict):
                        cleaned_images.append(_clean_dict_for_json(img))
                    else:
                        cleaned_images.append(_clean_text_for_json(str(img)))
                response["images"] = cleaned_images
            
            # Test JSON serialization before returning
            try:
                json.dumps(response, ensure_ascii=False)
            except (TypeError, ValueError) as e:
                logger.warning(f"JSON serialization test failed: {str(e)}")
                # Return a simplified response if full response can't be serialized
                return {
                    "url": _clean_text_for_json(url),
                    "status": "success",
                    "warning": "Content contained characters that could not be properly serialized. Simplified response returned.",
                    "title": response.get("title", ""),
                    "content_length": len(str(response.get("markdown", response.get("text", ""))))
                }
            
            return response
            
    except Exception as e:
        error_msg = f"Tool execution failed: {str(e)}"
        logger.error(f"crawl_webpage failed: {error_msg}")
        return {
            "error": _clean_text_for_json(error_msg),
            "status": "error"
        }

async def crawl_multiple_webpages(
    urls: List[str],
    output_format: str = "markdown",
    include_links: Optional[bool] = True,
    include_images: Optional[bool] = True,
    headless: Optional[bool] = True,
    extract_main_content: Optional[bool] = True,
    max_concurrent: Optional[int] = 5
) -> Dict[str, Any]:
    """
    Crawl multiple webpages in parallel and extract their content.
    
    Args:
        urls: List of URLs to crawl (required)
        output_format: Format of the output: "markdown", "html", "text", or "all" (default: "markdown")
        include_links: Whether to include links in the output (default: True)
        include_images: Whether to include images in the output (default: True)
        headless: Whether to run the browser in headless mode (default: True)
        extract_main_content: Whether to extract only the main content or the entire page (default: True)
        max_concurrent: Maximum number of concurrent crawls (default: 5)
        
    Returns:
        Dictionary containing the results for each URL
    """
    logger.info(f"crawl_multiple_webpages called with {len(urls)} URLs")
    
    if not CRAWL4AI_AVAILABLE:
        return {
            "error": "Crawl4AI is not installed. Please install it with 'pip install crawl4ai'.",
            "status": "error"
        }
    
    # Create a semaphore to limit concurrent runs
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def _crawl_with_semaphore(url):
        async with semaphore:
            return await crawl_webpage(
                url=url,
                output_format=output_format,
                include_links=include_links,
                include_images=include_images,
                headless=headless,
                extract_main_content=extract_main_content
            )
    
    try:
        # Run crawls concurrently but limited by semaphore
        tasks = [_crawl_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        response = {
            "results": {_clean_text_for_json(url): result for url, result in zip(urls, results)},
            "count": len(results),
            "successful": sum(1 for r in results if r.get("status") == "success"),
            "failed": sum(1 for r in results if r.get("status") == "error"),
            "status": "success"
        }
        
        # Test JSON serialization
        try:
            json.dumps(response, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            logger.warning(f"JSON serialization test failed for multiple pages: {str(e)}")
            # Return simplified response
            return {
                "count": len(results),
                "successful": sum(1 for r in results if r.get("status") == "success"),
                "failed": sum(1 for r in results if r.get("status") == "error"),
                "warning": "Some content contained characters that could not be properly serialized.",
                "status": "success"
            }
        
        return response
        
    except Exception as e:
        error_msg = f"Tool execution failed: {str(e)}"
        logger.error(f"crawl_multiple_webpages failed: {error_msg}")
        return {
            "error": _clean_text_for_json(error_msg),
            "status": "error"
        }

async def extract_structured_data(
    url: str,
    schema: Dict[str, Any],
    headless: Optional[bool] = True,
    wait_for_selector: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extract structured data from a webpage using CSS selectors.
    
    Args:
        url: URL of the webpage to crawl (required)
        schema: Schema defining the CSS selectors for data extraction (required)
                Format example: {
                    "name": "Products",
                    "baseSelector": ".product-item",
                    "fields": [
                        {"name": "title", "selector": "h2", "type": "text"},
                        {"name": "price", "selector": ".price", "type": "text"},
                        {"name": "url", "selector": "a", "type": "attribute", "attribute": "href"}
                    ]
                }
        headless: Whether to run the browser in headless mode (default: True)
        wait_for_selector: CSS selector to wait for before extracting data (optional)
        
    Returns:
        Dictionary containing the extracted structured data
    """
    logger.info(f"extract_structured_data called with URL: {url}")
    
    if not CRAWL4AI_AVAILABLE:
        return {
            "error": "Crawl4AI is not installed. Please install it with 'pip install crawl4ai'.",
            "status": "error"
        }
    
    try:
        # Import here to avoid issues if Crawl4AI is not installed
        from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
        
        # Configure browser settings
        browser_config = BrowserConfig(
            headless=headless,
            verbose=True
        )
        
        # Create CSS extraction strategy
        extraction_strategy = JsonCssExtractionStrategy(schema)
        
        # Configure crawler settings
        run_config = CrawlerRunConfig(
            extraction_strategy=extraction_strategy,
            wait_for=wait_for_selector,
            cache_mode=CacheMode.ENABLED
        )
        
        # Initialize and run the crawler
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            
            if not result.success:
                error_msg = getattr(result, 'error_message', 'Unknown error')
                return {
                    "error": f"Crawl failed: {_clean_text_for_json(str(error_msg))}",
                    "status_code": getattr(result, 'status_code', None),
                    "status": "error"
                }
            
            # Extract structured data from result
            extracted_data = None
            if hasattr(result, 'extracted_content') and result.extracted_content:
                extracted_data = result.extracted_content
            elif hasattr(result, 'extraction_result') and result.extraction_result:
                extracted_data = result.extraction_result
            
            if extracted_data:
                response = {
                    "url": _clean_text_for_json(url),
                    "data": _clean_dict_for_json(extracted_data) if isinstance(extracted_data, dict) else extracted_data,
                    "status": "success"
                }
                
                # Test JSON serialization
                try:
                    json.dumps(response, ensure_ascii=False)
                except (TypeError, ValueError) as e:
                    logger.warning(f"JSON serialization test failed for structured data: {str(e)}")
                    return {
                        "url": _clean_text_for_json(url),
                        "warning": "Extracted data contained characters that could not be properly serialized.",
                        "data_type": str(type(extracted_data)),
                        "status": "success"
                    }
                
                return response
            else:
                return {
                    "url": _clean_text_for_json(url),
                    "error": "No structured data could be extracted with the provided schema",
                    "status": "error"
                }
                
    except Exception as e:
        error_msg = f"Tool execution failed: {str(e)}"
        logger.error(f"extract_structured_data failed: {error_msg}")
        return {
            "error": _clean_text_for_json(error_msg),
            "status": "error"
        }

def register(mcp_instance):
    """Register the Crawl4AI tools with the MCP server"""
    if CRAWL4AI_AVAILABLE:
        mcp_instance.tool()(crawl_webpage)
        mcp_instance.tool()(crawl_multiple_webpages)
        mcp_instance.tool()(extract_structured_data)
        logger.info("Crawl4AI tools registered successfully with improved JSON handling")
    else:
        logger.warning("Crawl4AI tools were not registered because Crawl4AI is not installed.")
