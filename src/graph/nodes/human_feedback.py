from ..config import DeepResearchState, NodeType
from .base import BaseNode
from langchain_core.runnables.config import RunnableConfig
from langgraph.types import Command, interrupt

class HumanFeedback(BaseNode):
    def __init__(self) -> None:
        super().__init__()

    def invoke(self, state: DeepResearchState, config: RunnableConfig):
        auto_accepted_plan = state.auto_accepted_plan
        plan_iterations = state.plan_iterations
        current_plan = state.current_plan

        if not auto_accepted_plan:
            feedback = interrupt("Please Review the Plan.")
            if feedback and str(feedback).upper().startswith("[EDIT_PLAN]"):
                return Command(
                update={
                    "messages": [
                        HumanMessage(content=feedback, name="feedback"),
                    ],
                },
                goto="planner",
                )
        elif feedback and str(feedback).upper().startswith("[ACCEPTED]"):
            logger.info("Plan is accepted by user.")
        else:
            raise TypeError(f"Interrupt value of {feedback} is not supported.")


        if current_plan.has_enough_context:
            plan_iterations += 1
            goto = NodeType.research_team.name
        else:
            plan_iterations = 0
            goto = NodeType.reporter.name


        return Command(
            update={
                "plan_iterations": plan_iterations,
            },
            goto=goto,
        )

    async def ainvoke(self):
        pass