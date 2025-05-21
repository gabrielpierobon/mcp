import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig

async def test_crawl():
    print("Testing Crawl4AI installation...")
    
    # Create a simple configuration
    browser_config = BrowserConfig(
        headless=True,
        verbose=True
    )
    
    # Initialize and run the crawler
    async with AsyncWebCrawler(config=browser_config) as crawler:
        url = "https://example.com"
        print(f"Crawling {url}...")
        
        result = await crawler.arun(url=url)
        
        if result.success:
            print("Crawl successful!")
            
            # Print available attributes
            print("\nAvailable attributes:")
            for attr in dir(result):
                if not attr.startswith('_'):
                    print(f"- {attr}")
            
            # Print markdown content
            if hasattr(result, 'markdown'):
                print(f"\nMarkdown content (first 200 chars): {str(result.markdown)[:200]}")
            
            # Try to access page metadata
            if hasattr(result, 'metadata'):
                print(f"\nMetadata: {result.metadata}")
            
            # Print HTML content length
            if hasattr(result, 'html'):
                print(f"\nHTML content length: {len(str(result.html))}")
            
            if hasattr(result, 'cleaned_html'):
                print(f"\nCleaned HTML content length: {len(str(result.cleaned_html))}")
        else:
            print(f"Crawl failed: {result.error_message if hasattr(result, 'error_message') else 'Unknown error'}")

if __name__ == "__main__":
    asyncio.run(test_crawl())