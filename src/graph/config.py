import operator
from enum import Enum, auto
from typing import Annotated, Any, List, Optional, Sequence
from pydantic import BaseModel
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from langchain_core.runnables.config import RunnableConfig
import os
from .models import Plan
from dataclasses import fields, dataclass
from langchain_core.messages import (
    AIMessage,
    AnyMessage,
    BaseMessage,
    SystemMessage,
    ToolMessage,
)



class DeepResearchState(BaseModel):
    """Represents the state of a graph node.
    Contains the current state of the node, a message, and a response. 
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    message: str | None = ""
    response: Optional[str] = None
    locale: str = "en-US"
    research_topic: str = ""
    enable_background_investigation: bool = True
    max_search_results: int = 2
    background_investigation_results: Optional[str] = None
    plan_iterations: int = 0
    current_plan: Plan | str = None
    auto_accepted_plan: bool = True

class NodeType(str, Enum):
    """Enum representing different types of nodes in the graph."""
    planner = auto()
    researcher = auto()
    coder = auto()
    reporter = auto()
    research_team = auto()
    background_investigation = auto()
    human_feedback = auto()
    coordinator = auto()
    
@dataclass
class Configuration:
    """The configurable fields."""
    max_plan_iterations: int = 1  # Maximum number of plan iterations
    max_step_num: int = 3  # Maximum number of steps in a plan
    max_search_results: int = 3  # Maximum number of search results
    mcp_settings: dict = None  # MCP settings, including dynamic loaded tools
    enable_deep_thinking: bool = False  # Whether to enable deep thinking

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})