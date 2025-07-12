from ..config import DeepResearchState
from loguru import logger
from langchain_core.runnables.config import RunnableConfig
from .base import BaseNode


class Coder(BaseNode):
    def __init__(self) -> None:
        super().__init__()
        
    def invoke(self, state: DeepResearchState, config: RunnableConfig):
        logger.info("Coder invoke method called")
        pass
    
    async def ainvoke(self):
        pass