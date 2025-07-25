"""Util that calls Tavily Search API.

In order to set this up, follow instructions at:
https://docs.tavily.com/docs/tavily-api/introduction
"""

import json
from typing import Any, Dict, List, Optional

import aiohttp
import requests
from langchain_core.utils import get_from_dict_or_env
from pydantic import BaseModel, ConfigDict, SecretStr, model_validator

TAVILY_API_URL = "https://api.tavily.com"
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper


class EnhancedTavilySearchAPIWrapper(TavilySearchAPIWrapper):
    def raw_results(
        self,
        query: str,
        max_results: Optional[int] = 5,
        search_depth: Optional[str] = "advanced",
        include_domains: Optional[List[str]] = [],
        exclude_domains: Optional[List[str]] = [],
        include_answer: Optional[bool] = False,
        include_raw_content: Optional[bool] = False,
        include_images: Optional[bool] = False,
        include_image_descriptions: Optional[bool] = False,
    ) -> Dict:
        params = {
            "api_key": self.tavily_api_key.get_secret_value(),
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_domains": include_domains,
            "exclude_domains": exclude_domains,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "include_images": include_images,
            "include_image_descriptions": include_image_descriptions,
        }
        response = requests.post(
            f"{TAVILY_API_URL}/search",
            json=params,
        )
        response.raise_for_status()
        return response.json()

    def results(
        self,
        query: str,
        max_results: Optional[int] = 5,
        search_depth: Optional[str] = "advanced",
        include_domains: Optional[List[str]] = [],
        exclude_domains: Optional[List[str]] = [],
        include_answer: Optional[bool] = False,
        include_raw_content: Optional[bool] = False,
        include_images: Optional[bool] = False,
        include_image_descriptions: Optional[bool] = False,
    ) -> List[Dict]:
        """Run query through Tavily Search and return metadata.

        Args:
            query: The query to search for.
            max_results: The maximum number of results to return.
            search_depth: The depth of the search. Can be "basic" or "advanced".
            include_domains: A list of domains to include in the search.
            exclude_domains: A list of domains to exclude from the search.
            include_answer: Whether to include the answer in the results.
            include_raw_content: Whether to include the raw content in the results.
            include_images: Whether to include images in the results.
        Returns:
            query: The query that was searched for.
            follow_up_questions: A list of follow up questions.
            response_time: The response time of the query.
            answer: The answer to the query.
            images: A list of images.
            results: A list of dictionaries containing the results:
                title: The title of the result.
                url: The url of the result.
                content: The content of the result.
                score: The score of the result.
                raw_content: The raw content of the result.
        """
        raw_search_results = self.raw_results(
            query,
            max_results=max_results,
            search_depth=search_depth,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            include_answer=include_answer,
            include_raw_content=include_raw_content,
            include_images=include_images,
            include_image_descriptions=include_image_descriptions,
        )
        return self.clean_results(raw_search_results["results"])

    async def raw_results_async(
        self,
        query: str,
        max_results: Optional[int] = 5,
        search_depth: Optional[str] = "advanced",
        include_domains: Optional[List[str]] = [],
        exclude_domains: Optional[List[str]] = [],
        include_answer: Optional[bool] = False,
        include_raw_content: Optional[bool] = False,
        include_images: Optional[bool] = False,
        include_image_descriptions: Optional[bool] = False,
    ) -> Dict:
        """Get results from the Tavily Search API asynchronously."""

        # Function to perform the API call
        async def fetch() -> str:
            params = {
                "api_key": self.tavily_api_key.get_secret_value(),
                "query": query,
                "max_results": max_results,
                "search_depth": search_depth,
                "include_domains": include_domains,
                "exclude_domains": exclude_domains,
                "include_answer": include_answer,
                "include_raw_content": include_raw_content,
                "include_images": include_images,
                "include_image_descriptions": include_image_descriptions,
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{TAVILY_API_URL}/search", json=params) as res:
                    if res.status == 200:
                        data = await res.text()
                        return data
                    else:
                        raise Exception(f"Error {res.status}: {res.reason}")

        results_json_str = await fetch()
        return json.loads(results_json_str)

    async def results_async(
        self,
        query: str,
        max_results: Optional[int] = 5,
        search_depth: Optional[str] = "advanced",
        include_domains: Optional[List[str]] = [],
        exclude_domains: Optional[List[str]] = [],
        include_answer: Optional[bool] = False,
        include_raw_content: Optional[bool] = False,
        include_images: Optional[bool] = False,
        include_image_descriptions: Optional[bool] = False,
    ) -> List[Dict]:
        results_json = await self.raw_results_async(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
            include_answer=include_answer,
            include_raw_content=include_raw_content,
            include_images=include_images,
            include_image_descriptions=include_image_descriptions,
        )
        return self.clean_results(results_json["results"])

    def clean_results(self, raw_results: Dict[str, List[Dict]]) -> List[Dict]:
        """Clean results from Tavily Search API."""
        results = raw_results["results"]
        clean_results = []
        for result in results:
            clean_result = {
                "type": "page",
                "title": result["title"],
                "url": result["url"],
                "content": result["content"],
                "score": result["score"],
            }
            if raw_content := result.get("raw_content"):
                clean_result["raw_content"] = raw_content
            clean_results.append(clean_result)
        images = raw_results.get("images", [])
        for image in images:
            clean_result = {
                "type": "image",
                "image_url": image["url"],
                "image_description": image.get("description", ""),
            }
            clean_results.append(clean_result)
        return clean_results
