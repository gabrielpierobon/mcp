import asyncio
import sys
import os

# Add the parent directory to the path so we can import the tools module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.crawl4ai_tool import crawl_webpage

async def test_mcp_crawler():
    print("Testing the MCP crawler tool functions...")
    
    # Test crawl_webpage function
    url = "https://example.com"
    print(f"Crawling {url}...")
    
    result = await crawl_webpage(
        url=url,
        output_format="markdown",
        include_links=True,
        headless=True,
        extract_main_content=True
    )
    
    # Print the result structure
    print("\nResult keys:")
    for key in result.keys():
        print(f"- {key}")
    
    # Check if it was successful
    if result.get("status") == "success":
        print("\nCrawl successful!")
        
        # Print markdown content if available
        if "markdown" in result:
            print(f"\nMarkdown content (first 200 chars): {result['markdown'][:200]}")
        
        # Print metadata if available
        if "metadata" in result:
            print(f"\nMetadata: {result['metadata']}")
        
        # Print title if available
        if "title" in result:
            print(f"\nTitle: {result['title']}")
    else:
        print(f"\nCrawl failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(test_mcp_crawler())