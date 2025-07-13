from ..config import DeepResearchState, Configuration, NodeType
from .base import BaseNode
from loguru import logger
from langchain_core.messages import HumanMessage, SystemMessage
from ..models import Plan
from langchain_core.runnables.config import RunnableConfig
from langgraph.types import Command


class Planner(BaseNode):
    def __init__(self) -> None:
        super().__init__()
        self.llm_structured_output = self.llm.with_structured_output(Plan)

    def invoke(self, state: DeepResearchState, config: RunnableConfig):
        logger.info("Planner invoke method called")
        configurable = Configuration.from_runnable_config(config)
        plan_iterations = state.plan_iterations
        
        logger.info(f"Plan iterations: {plan_iterations}, Max plan iterations: {configurable.max_plan_iterations}")

        if plan_iterations >= configurable.max_plan_iterations:
            return Command(
                goto=NodeType.reporter.name,
            )

        messages = self.apply_prompt_template("planner", state, configurable)
        
        if state.background_investigation_results:
            messages.append(
                HumanMessage(
                    content=(
                            "background investigation results of user query:\n"
                            + state.background_investigation_results
                            + "\n"
                        )
                        )
            )
        
        if configurable.enable_deep_thinking:
            response_text = ""
            self.llm = self.set_llm("reasoning")
            response = self.llm.stream(messages)
            for chunk in response:
                response_text +=  chunk.content
        else:
            current_plan: Plan = self.llm_structured_output.invoke(messages)

        return Command(
            update={
                "current_plan": current_plan,
            },
            goto=NodeType.human_feedback.name,
        )
    
    async def ainvoke(self):
        pass