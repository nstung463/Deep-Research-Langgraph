from .crawler import Crawler, OptimizedWebCrawler

from langchain_core.tools import tool

# crawler = OptimizedWebCrawler(max_workers=5, delay=0.5)
crawler = Crawler()

@tool
def crawl_tool(
    url: str,
) -> dict:
    """Use this to crawl a url and get a readable content in markdown format."""
    article = crawler.crawl(url)
    return {"url": url, "crawled_content": article.to_markdown()[:1000]}
