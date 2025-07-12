import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from markdownify import markdownify as md


@dataclass
class CrawlResult:
    """Kết quả crawl từ một URL"""
    url: str
    title: str
    content: str
    links: List[str]
    images: List[str]
    metadata: Dict[str, str]
    status_code: int
    crawl_time: float
    raw_content: str

    def to_markdown(self) -> str:
        markdown = ""
        markdown += f"# {self.title}\n\n"
        markdown += md(self.raw_content)
        return markdown

class OptimizedWebCrawler:
    def __init__(self, max_workers: int = 10, delay: float = 1.0):
        """
        Khởi tạo web crawler tối ưu
        
        Args:
            max_workers: Số lượng thread đồng thời
            delay: Độ trễ giữa các request (giây)
        """
        self.max_workers = max_workers
        self.delay = delay
        self.session = self._create_session()
        self.visited_urls: Set[str] = set()
        
    def _create_session(self) -> requests.Session:
        """Tạo session với retry strategy và connection pooling"""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=100, pool_maxsize=100)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Headers để tránh bị block
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        return session
    
    def _clean_text(self, text: str) -> str:
        """Làm sạch text content"""
        if not text:
            return ""
        
        # Loại bỏ script và style tags
        text = re.sub(r'<script[^>]*?>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*?>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Loại bỏ HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text



    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Trích xuất nội dung chính từ trang web"""
        # Thử các selector phổ biến cho nội dung chính
        main_content_selectors = [
            # HTML5 semantic tags
            'article', 'main', 'section', '[role="main"]', '[role="article"]',
            
            # Common content class names
            '.content', '#content', '.main-content', '#main-content',
            '.post-content', '.entry-content', '.article-content',
            '.page-content', '.story-content', '.news-content',
            
            # Blog and CMS specific
            '.post', '.entry', '.article', '.story', '.news',
            '.blog-post', '.single-post', '.post-body', '.entry-body',
            '.article-body', '.story-body', '.news-body',
            
            # Popular CMS patterns
            '.content-area', '.site-content', '.primary-content',
            '.main-area', '.content-wrapper', '.page-wrapper',
            '.container .content', '.wrapper .content',
            
            # WordPress specific
            '.hentry', '.post-entry', '.entry-summary', '.entry-header',
            '.wp-content', '.post-wrap', '.content-wrap',
            
            # News sites
            '.article-wrap', '.story-wrap', '.news-wrap',
            '.article-text', '.story-text', '.news-text',
            '.article-paragraph', '.story-paragraph',
            
            # E-commerce and product pages
            '.product-description', '.product-details', '.product-content',
            '.description', '.details', '.specifications',
            
            # Documentation and technical sites
            '.documentation', '.docs', '.guide', '.tutorial',
            '.readme', '.markdown-body', '.wiki-content',
            
            # Forum and discussion
            '.forum-post', '.discussion', '.comment-content',
            '.message-content', '.thread-content',
            
            # Social media and user content
            '.user-content', '.user-post', '.timeline-content',
            '.feed-content', '.social-content',
            
            # Generic content patterns
            '.text', '.body', '.main', '.primary', '.central',
            '.core', '.inner', '.wrapper', '.container',
            
            # ID-based selectors
            '#main', '#primary', '#content-main', '#page-content',
            '#article', '#post', '#story', '#text', '#body',
            
            # Data attributes
            '[data-content]', '[data-article]', '[data-post]',
            '[data-main]', '[data-primary]',
            
            # Specific site patterns
            '.post-text', '.article-full', '.full-content',
            '.content-full', '.text-content', '.rich-text',
            '.formatted-text', '.editor-content', '.wysiwyg'
        ]
        
        content = ""
        raw_content = ""
        # Tìm nội dung chính
        for selector in main_content_selectors:
            elements = soup.select(selector)
            if elements:
                content = ' '.join([self._clean_text(elem.get_text()) for elem in elements])
                raw_content = ' '.join([elem.get_text() for elem in elements])
                break
        
        # Nếu không tìm thấy, lấy toàn bộ body
        if not content:
            body = soup.find('body')
            if body:
                # Loại bỏ nav, header, footer, sidebar
                for tag in body.find_all(['nav', 'header', 'footer', 'aside', '.sidebar', '.navigation']):
                    tag.decompose()
                content = self._clean_text(body.get_text())
        
        return content, raw_content
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Trích xuất metadata từ trang web"""
        metadata = {}
        
        # Meta tags
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            name = tag.get('name') or tag.get('property') or tag.get('itemprop')
            content = tag.get('content')
            if name and content:
                metadata[name] = content
        
        # Open Graph tags
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        for tag in og_tags:
            prop = tag.get('property')
            content = tag.get('content')
            if prop and content:
                metadata[prop] = content
        
        return metadata
    
    def crawl_url(self, url: str, timeout: int = 30) -> Optional[CrawlResult]:
        """Crawl một URL duy nhất"""
        start_time = time.time()
        
        try:
            if url in self.visited_urls:
                return None
            
            self.visited_urls.add(url)
            
            # Gửi request
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Trích xuất thông tin
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            content, raw_content = self._extract_content(soup)
            
            # Trích xuất links
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(url, href)
                if self._is_valid_url(absolute_url):
                    links.append(absolute_url)
            
            # Trích xuất images
            images = []
            for img in soup.find_all('img', src=True):
                src = img['src']
                absolute_url = urljoin(url, src)
                images.append(absolute_url)
            
            # Trích xuất metadata
            metadata = self._extract_metadata(soup)
            
            crawl_time = time.time() - start_time
            
            result = CrawlResult(
                url=url,
                title=title_text,
                content=content,
                links=links,
                images=images,
                metadata=metadata,
                status_code=response.status_code,
                crawl_time=crawl_time,
                raw_content=raw_content
            )
            
            logger.info(f"Crawled {url} - {len(content)} chars - {crawl_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            return None
    
    def _is_valid_url(self, url: str) -> bool:
        """Kiểm tra URL hợp lệ"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def crawl_multiple_urls(self, urls: List[str], timeout: int = 30) -> List[CrawlResult]:
        """Crawl nhiều URL đồng thời"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit tất cả tasks
            future_to_url = {
                executor.submit(self.crawl_url, url, timeout): url 
                for url in urls
            }
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.error(f"Error processing {url}: {str(e)}")
                
                # Delay giữa các request
                time.sleep(self.delay)
        
        return results


# if __name__ == "__main__":
#     crawler = OptimizedWebCrawler(max_workers=5, delay=1.0)
#     urls = [
#         "https://python.langchain.com/api_reference/langchain/agents/langchain.agents.self_ask_with_search.base.create_self_ask_with_search_agent.html",
#         "https://jina.ai/reader/",
#         "https://python.langchain.com/api_reference/langchain/agents/langchain.agents.self_ask_with_search.base.create_self_ask_with_search_agent.html",
#     ]
#     results = crawler.crawl_multiple_urls(urls)
