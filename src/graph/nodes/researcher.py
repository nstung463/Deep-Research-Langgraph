from ..config import DeepResearchState
from .base import BaseNode
from langchain_core.runnables.config import RunnableConfig
from langgraph.types import Command
from loguru import logger
from src.tools.search import web_search_tool
from src.tools.crawl import crawl_tool


class Researcher(BaseNode):
    def __init__(self) -> None:
        super().__init__()
        self.llm = self.set_llm("gemini")
        self.tools = [web_search_tool(max_search_results), crawl_tool]
        self.agent = create_react_agent(name="researcher", model=self.llm, tools=self.tools, prompt=prompt[0])


    def invoke(self, state: DeepResearchState, config: RunnableConfig):
        logger.info("Researcher invoke method called")
        configurable = Configuration.from_runnable_config(config)

        max_search_results = configurable.max_search_results
        tools = [web_search_tool(max_search_results), crawl_tool]
        return 
        pass
    
    async def ainvoke(self):
        pass