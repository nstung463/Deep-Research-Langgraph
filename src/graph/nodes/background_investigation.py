from ..config import DeepResearchState, Configuration
from .base import BaseNode
from src.tools.search import web_search_tool
from langchain_core.runnables.config import RunnableConfig
from loguru import logger

class BackgroundInvestigation(BaseNode):
    def __init__(self) -> None:
        super().__init__()
    
    
    def invoke(self, state: DeepResearchState, config: RunnableConfig):
        configurable = Configuration.from_runnable_config(config)
        
        max_search_results = configurable.max_search_results
        research_topic = state.research_topic
        logger.info(f"Background investigation invoked for topic: {research_topic} with max results: {max_search_results}")
        
        background_investigation_results = None
        
        search_results = web_search_tool(max_search_results=max_search_results, 
                                include_images=False, 
                                include_image_descriptions=False).invoke(research_topic)
        
        
        # Process the results as needed
        if isinstance(search_results, list):
            search_results = [
                f"## {result['title']}\n\n{result['content']}" for result in search_results
            ]
            background_investigation_results = "".join(search_results)
            return {
                "background_investigation_results": background_investigation_results,
            }
        
        return {
            "background_investigation_results": background_investigation_results
        }
    async def ainvoke(self, state: DeepResearchState):
        pass