from ..config import DeepResearchState
from .base import BaseNode
from langchain_core.runnables.config import RunnableConfig


class Reporter(BaseNode):
    def __init__(self) -> None:
        super().__init__()

    def invoke(self, state: DeepResearchState, config: RunnableConfig):
        pass
    
    async def ainvoke(self):
        pass