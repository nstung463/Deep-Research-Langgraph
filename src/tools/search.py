from src.config import SearchEngine
from src.tools.tavily_search.tavily_search_results_with_images import TavilySearchResultsWithImages

def web_search_tool(max_search_results: int, **kwargs) -> list:
    """
    Perform a web search using the configured search engine.

    Args:
        query (str): The search query.
        locale (str): The user's locale for the search.

    Returns:
        list: A list of search results.
    """
    include_raw_content = kwargs.get("include_raw_content", True)
    include_images = kwargs.get("include_images", True)
    include_image_descriptions = kwargs.get("include_image_descriptions", True)
    return TavilySearchResultsWithImages(
        max_results=max_search_results,
        include_raw_content=include_raw_content,
        include_images=include_images,
        include_image_descriptions=include_image_descriptions,
    )