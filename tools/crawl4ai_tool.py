from typing import Dict, Any, Optional, List, Union
import asyncio
import os
import importlib.util
from dotenv import load_dotenv

# Try to load environment variables from .env file
load_dotenv()

# Check if Crawl4AI is installed using importlib.util.find_spec
CRAWL4AI_AVAILABLE = importlib.util.find_spec("crawl4ai") is not None

if CRAWL4AI_AVAILABLE:
    try:
        # Import Crawl4AI components
        from crawl4ai import AsyncWebCrawler
        from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
        print("INFO: Crawl4AI successfully imported")
    except ImportError as e:
        print(f"WARNING: Error importing Crawl4AI components: {str(e)}")
        CRAWL4AI_AVAILABLE = False
else:
    print("WARNING: Crawl4AI is not installed. The web crawler tool will not be available.")
    print("To install it, run: pip install crawl4ai playwright && playwright install")

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
    print(f"INFO: crawl_webpage called with URL: {url}, format: {output_format}")
    
    if wait_time is not None:
        print("WARNING: 'wait_time' parameter is not supported in the current Crawl4AI version and will be ignored.")
    
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
                return {
                    "error": f"Crawl failed: {result.error_message if hasattr(result, 'error_message') else 'Unknown error'}",
                    "status_code": result.status_code if hasattr(result, 'status_code') else None,
                    "status": "error"
                }
            
            # Prepare response based on requested format
            response = {
                "url": url,
                "status_code": result.status_code if hasattr(result, 'status_code') else None,
                "status": "success"
            }
            
            # Add page metadata if available
            if hasattr(result, 'metadata'):
                response["metadata"] = result.metadata
                # Add title from metadata if available
                if result.metadata and 'title' in result.metadata:
                    response["title"] = result.metadata['title']
            
            # Add content based on requested format
            if output_format == "markdown" or output_format == "all":
                if hasattr(result, 'markdown'):
                    response["markdown"] = str(result.markdown)
            
            if output_format == "html" or output_format == "all":
                if extract_main_content and hasattr(result, 'cleaned_html'):
                    response["html"] = result.cleaned_html
                elif hasattr(result, 'html'):
                    response["html"] = result.html
            
            if output_format == "text" or output_format == "all":
                if hasattr(result, 'text'):
                    response["text"] = result.text
                elif hasattr(result, 'markdown'):
                    # If no plain text is available, use the markdown as a fallback
                    response["text"] = str(result.markdown)
            
            # Include links if requested
            if include_links and hasattr(result, 'links'):
                response["links"] = result.links
                
            # Include images if requested
            if include_images and hasattr(result, 'media') and 'images' in result.media:
                response["images"] = result.media.get('images', [])
            
            return response
    except Exception as e:
        print(f"ERROR: crawl_webpage failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
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
    print(f"INFO: crawl_multiple_webpages called with {len(urls)} URLs")
    
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
        
        return {
            "results": {url: result for url, result in zip(urls, results)},
            "count": len(results),
            "successful": sum(1 for r in results if r.get("status") == "success"),
            "failed": sum(1 for r in results if r.get("status") == "error"),
            "status": "success"
        }
    except Exception as e:
        print(f"ERROR: crawl_multiple_webpages failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
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
    print(f"INFO: extract_structured_data called with URL: {url}")
    
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
                return {
                    "error": f"Crawl failed: {result.error_message if hasattr(result, 'error_message') else 'Unknown error'}",
                    "status_code": result.status_code if hasattr(result, 'status_code') else None,
                    "status": "error"
                }
            
            # Extract structured data from result
            if hasattr(result, 'extracted_content') and result.extracted_content:
                return {
                    "url": url,
                    "data": result.extracted_content,
                    "status": "success"
                }
            else:
                # Try to look for extraction_result if extracted_content is not available
                if hasattr(result, 'extraction_result') and result.extraction_result:
                    return {
                        "url": url,
                        "data": result.extraction_result,
                        "status": "success"
                    }
                else:
                    return {
                        "url": url,
                        "error": "No structured data could be extracted with the provided schema",
                        "status": "error"
                    }
    except Exception as e:
        print(f"ERROR: extract_structured_data failed: {str(e)}")
        return {
            "error": f"Tool execution failed: {str(e)}",
            "status": "error"
        }

def register(mcp_instance):
    """Register the Crawl4AI tools with the MCP server"""
    if CRAWL4AI_AVAILABLE:
        mcp_instance.tool()(crawl_webpage)
        mcp_instance.tool()(crawl_multiple_webpages)
        mcp_instance.tool()(extract_structured_data)
    else:
        print("WARNING: Crawl4AI tools were not registered because Crawl4AI is not installed.")