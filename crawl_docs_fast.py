import os
import re
import sys
import psutil
import asyncio
import requests
import argparse
from xml.etree import ElementTree

from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Crawl websites from a sitemap URL.')
    parser.add_argument('-w', '--website', 
                        required=True,
                        help='The sitemap URL to crawl (e.g., https://example.com/sitemap.xml)')
    parser.add_argument('-o', '--output', 
                        default='results',
                        help='The folder name to save markdown files (default: results)')
    parser.add_argument('-c', '--concurrent', 
                        type=int, 
                        default=10,
                        help='Maximum number of concurrent crawls (default: 10)')
    return parser.parse_args()

def setup_output_directory(output_folder):
    """Set up the output directory for storing results."""
    # Get the location of the script
    __location__ = os.path.dirname(os.path.abspath(__file__))
    # Create the full path for the output directory
    __output__ = os.path.join(__location__, output_folder)
    
    # Ensure output directory exists
    os.makedirs(__output__, exist_ok=True)
    
    return __output__

def setup_system_path():
    """Add parent directory to the system path."""
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(parent_dir)

async def crawl_parallel(urls: List[str], output_dir: str, max_concurrent: int = 3):
    print(f"\n=== Parallel Crawling with Browser Reuse + Memory Check (Max Concurrent: {max_concurrent}) ===")

    # We'll keep track of peak memory usage across all tasks
    peak_memory = 0
    process = psutil.Process(os.getpid())

    def log_memory(prefix: str = ""):
        nonlocal peak_memory
        current_mem = process.memory_info().rss  # in bytes
        if current_mem > peak_memory:
            peak_memory = current_mem
        print(f"{prefix} Current Memory: {current_mem // (1024 * 1024)} MB, Peak: {peak_memory // (1024 * 1024)} MB")

    # Minimal browser config
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )
    crawl_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    # Create the crawler instance
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        # We'll chunk the URLs in batches of 'max_concurrent'
        success_count = 0
        fail_count = 0
        for i in range(0, len(urls), max_concurrent):
            batch = urls[i : i + max_concurrent]
            tasks = []

            for j, url in enumerate(batch):
                # Unique session_id per concurrent sub-task
                session_id = f"parallel_session_{i + j}"
                task = crawler.arun(url=url, config=crawl_config, session_id=session_id)
                tasks.append(task)

            # Check memory usage prior to launching tasks
            log_memory(prefix=f"Before batch {i//max_concurrent + 1}: ")

            # Gather results
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Check memory usage after tasks complete
            log_memory(prefix=f"After batch {i//max_concurrent + 1}: ")

            # Evaluate results
            for url, result in zip(batch, results):
                if isinstance(result, Exception):
                    print(f"Error crawling {url}: {result}")
                    fail_count += 1
                elif result.success:
                    success_count += 1

                    print(f"Successfully crawled: {url}")
                    print(f"Markdown length: {len(result.markdown_v2.raw_markdown)}")
                    # Extract raw markdown
                    raw_markdown = result.markdown_v2.raw_markdown
                    
                    # Remove any line with a malformed link
                    filtered_markdown = remove_malformed_links(raw_markdown)

                    # Save content to markdown file
                    safe_filename = create_safe_filename(url)
                    filename = os.path.join(output_dir, f"{safe_filename}.md")
                    with open(filename, "w", encoding="utf-8") as file:
                        file.write(f"# Crawled Content from {url}\n\n")
                        file.write(filtered_markdown)

                else:
                    fail_count += 1

        print(f"\nSummary:")
        print(f"  - Successfully crawled: {success_count}")
        print(f"  - Failed: {fail_count}")

    finally:
        print("\nClosing crawler...")
        await crawler.close()
        # Final memory log
        log_memory(prefix="Final: ")
        print(f"\nPeak memory usage (MB): {peak_memory // (1024 * 1024)}")

def create_safe_filename(url: str) -> str:
    """
    Creates a safe filename from a URL by removing invalid characters.
    
    Args:
        url (str): The URL to convert
        
    Returns:
        str: A safe filename
    """
    # Remove protocol and common separators, then replace invalid characters
    safe_name = url.replace('https://', '').replace('http://', '').replace('www.', '')
    safe_name = re.sub(r'[\\/*?:"<>|]', '_', safe_name)
    # Replace multiple slashes and dots with single underscore
    safe_name = re.sub(r'[/\.]+', '_', safe_name)
    # Limit filename length
    if len(safe_name) > 200:
        safe_name = safe_name[:200]
    return safe_name

def remove_malformed_links(content: str) -> str:
    """
    Removes any malformed markdown links from the content.
    
    Args:
        content (str): The raw markdown content.
        
    Returns:
        str: The filtered content without malformed links.
    """
    # Regular expression to match and remove malformed links like:
    # * [ Instagram ](https://www.cloudsynapps.com/csa-ai-assistant-product/<https:/www.instagram.com/thecloudsynapps/>)
    # or
    # [](<https:/www.canva.com/...>)
    # Remove lines containing malformed links (those with <https:/...>)
    content = re.sub(r'.*<https:/[^>]*>.*\n', '', content)
    
    # Remove lines containing email addresses (simple pattern for emails)
    content = re.sub(r'.*\S+@\S+\.\S+.*\n', '', content)
    
    # Remove lines containing phone numbers (basic pattern for phone numbers)
    content = re.sub(r'.*\d{3}[\.\-]?\d{3}[\.\-]?\d{4}.*\n', '', content)
    
    # Remove empty lines or any lines that are irrelevant (optional)
    content = re.sub(r'^\s*\n', '', content)
    
    return content

def get_urls_from_sitemap(sitemap_url: str) -> List[str]:
    """
    Fetches all URLs from a sitemap.
    
    Args:
        sitemap_url (str): The URL of the sitemap
        
    Returns:
        List[str]: List of URLs
    """
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        
        # Parse the XML
        root = ElementTree.fromstring(response.content)
        
        # Extract all URLs from the sitemap
        # The namespace is usually defined in the root element
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:loc', namespace)]
        
        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return []

async def main():
    # Parse command line arguments
    args = parse_arguments()
    
    # Setup system path
    setup_system_path()
    
    # Setup output directory
    output_dir = setup_output_directory(args.output)
    
    # Get URLs from sitemap
    urls = get_urls_from_sitemap(args.website)
    
    if urls:
        print(f"Found {len(urls)} URLs to crawl")
        print(f"Output directory: {output_dir}")
        await crawl_parallel(urls, output_dir, max_concurrent=args.concurrent)
    else:
        print("No URLs found to crawl")

if __name__ == "__main__":
    asyncio.run(main())
