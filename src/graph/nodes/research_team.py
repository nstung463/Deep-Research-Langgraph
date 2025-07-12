from ..config import DeepResearchState
from .base import BaseNode
from loguru import logger


class ResearchTeam(BaseNode):
    def __init__(self) -> None:
        super().__init__()

    def invoke(self, state: DeepResearchState):
        logger.info("ResearchTeam invoke method called")
        pass
    
    async def ainvoke(self):
        pass