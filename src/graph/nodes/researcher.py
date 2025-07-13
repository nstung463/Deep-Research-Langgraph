from ..config import DeepResearchState, NodeType, Configuration
from .base import BaseNode
from langchain_core.runnables.config import RunnableConfig
from langgraph.types import Command
from loguru import logger
from src.tools.search import web_search_tool
from src.tools.crawl import crawl_tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage


class Researcher(BaseNode):
    def __init__(self) -> None:
        super().__init__()
        self.llm = self.set_llm("basic")


    async def ainvoke(self, state: DeepResearchState, config: RunnableConfig):
        logger.info("Researcher invoke method called")
        # configurable = Configuration.from_runnable_config(config)

        current_plan = state.current_plan
        max_search_results = state.max_search_results


        tools = [web_search_tool(max_search_results), crawl_tool]

        agent = create_react_agent(
            name="researcher",
            model=self.llm,
            tools=tools,
            prompt=self.apply_prompt_template(
                prompt_name=NodeType.researcher.name, state=state
            )[0],
        )

        agent_input = {
            "messages": []
        }

        completed_steps = []
        for step in current_plan.steps:
            if not step.execution_res:
                current_step = step
                break
            else:
                completed_steps.append(step)

        complete_step_info = ""
        for idx, completed_step in enumerate(completed_steps):
            complete_step_info += f"## Summary of Step {idx + 1}: {completed_step.title}\n\n"
            complete_step_info += f"<result>\n{completed_step.execution_res}\n</result>\n\n"

        paraphrased_task = (
            f"{complete_step_info}"
            f"# Upcoming Task\n\n"
            f"## Task Title\n\n{current_step.title}\n\n"
            f"## Task Overview\n\n{current_step.description}\n\n"
            f"## Language/Locale\n\n{state.locale}"
        )


        agent_input["messages"].append(HumanMessage(content=paraphrased_task))

        result = await agent.ainvoke({"messages": agent_input["messages"]})
        research_context = result["messages"][-1].content
        current_step.execution_res = research_context
        logger.info(f"Step '{current_step.title}' execution completed by {NodeType.researcher.name}")


        return Command(
            update={
                "messages": [SystemMessage(content=research_context)],
                "research_context": [research_context]
            },
            goto="research_team"
        )

    def invoke(self):
        pass
