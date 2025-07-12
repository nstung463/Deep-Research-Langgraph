from ..config import DeepResearchState, NodeType
from .base import BaseNode
from loguru import logger
from langchain_core.tools import tool
from typing import Annotated
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command



class Coordinator(BaseNode):
    def __init__(self) -> None:
        super().__init__()
    
    @tool
    def handoff_to_planner(
        research_topic: Annotated[str, "The topic of the research task to be handed off."],
        locale: Annotated[str, "The user's detected language locale (e.g., en-US, zh-CN)."],
        ):
        """Handoff to planner agent to do plan."""
        # This tool is not returning anything: we're just using it
        # as a way for LLM to signal that it needs to hand off to planner agent
        return
    
    def invoke(self, state: DeepResearchState):
        logger.info("Coordinator invoke method called")
        messages = self.apply_prompt_template("coordinator", state)
        response = self.llm.bind_tools([self.handoff_to_planner]).invoke(messages)
        
        locale = state.locale
        research_topic = state.research_topic
        
        goto = NodeType.planner.name
        
        if response.tool_calls:
            logger.info(f"Tool calls detected: {response.tool_calls}")
            
            if state.enable_background_investigation:
                goto = NodeType.background_investigation.name

            for tool_call in response.tool_calls:
                if tool_call.get("name") == "handoff_to_planner":
                    # Extract parameters from the tool call
                    research_topic = tool_call.get("args").get("research_topic", research_topic)
                    locale = tool_call.get("args").get("locale", locale)
                    logger.info(f"Handoff to planner with topic: {research_topic} and locale: {locale}")
                    break
                else:
                    continue
        logger.info(f"Coordinator will go to: {goto} with topic: {research_topic} and locale: {locale}")
        return Command(
            update={
                    "locale": locale,
                    "research_topic": research_topic,
                    },
            goto=goto
        )
    
    async def ainvoke(self):
        pass