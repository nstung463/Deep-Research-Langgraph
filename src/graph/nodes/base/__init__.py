# base_node.py

import dataclasses
from datetime import datetime
from src.graph.config import DeepResearchState, Configuration
from jinja2 import Environment, FileSystemLoader, select_autoescape
from langchain_core.messages import SystemMessage
from src.llms.llm import get_llm_by_type  

# Set up Jinja2 environment
env = Environment(
    loader=FileSystemLoader("src/graph/prompts"),
    autoescape=select_autoescape(),
)



class BaseNode:
    def __init__(self) -> None:
        self.llm = get_llm_by_type("basic")  # Default LLM type, can be overridden

    def set_llm(self, llm_type: str):
        """
        Set the LLM type for this node. 
        Args:
            llm_type: Type of LLM to use (e.g., "basic", "reasoning", "simple_tasks")
        """
        if llm_type == "basic":
            return get_llm_by_type("basic")
        elif llm_type == "reasoning":
            return get_llm_by_type("reasoning")
        elif llm_type == "simple_tasks":
            return get_llm_by_type("simple_tasks")
        elif llm_type == "gemini":
            return get_llm_by_type("gemini")
        else:
            raise ValueError(f"Unknown LLM type: {llm_type}")
    def apply_prompt_template(
        self, prompt_name: str, state: DeepResearchState, configurable: Configuration = None
    ) -> list:
        """
        Apply template variables to a prompt template and return formatted messages.

        Args:
            prompt_name: Name of the prompt template to use
            state: Current agent state containing variables to substitute

        Returns:
            List of messages with the system prompt as the first message
        """
        # Convert state to dict for template rendering
        state_vars = {
            "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
            **state.dict(),
        }

        if configurable:
            state_vars.update(dataclasses.asdict(configurable))
            
        try:
            template = env.get_template(f"{prompt_name}.md")
            system_prompt = template.render(**state_vars)
            return [SystemMessage(content=system_prompt)] + state.messages
        except Exception as e:
            raise ValueError(f"Error applying template {prompt_name}: {e}")


    def invoke(self, state, *args, **kwargs):
        raise NotImplementedError("You must implement `invoke()` in the subclass")

    async def ainvoke(self, state, *args, **kwargs):
        raise NotImplementedError("You must implement `ainvoke()` in the subclass")