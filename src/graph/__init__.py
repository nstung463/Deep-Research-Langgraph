
from langgraph.graph import END, START, StateGraph
from langgraph.pregel import RetryPolicy, CachePolicy
from .nodes import (
    BackgroundInvestigation,
    Coder,
    Coordinator,
    HumanFeedback,
    Planner,
    Reporter,
    ResearchTeam,
    Researcher,
)
from .config import NodeType, DeepResearchState
from langgraph.graph.state import CompiledStateGraph
from .models import StepType

# with PostgresSaver.from_conn_string(
#     str(Database().sqlalchemy_checkpoint_url)
# ) as checkpointer:
#     checkpointer.setup()

class DeepResearchGraph:
    def __init__(self):
        self.graph = StateGraph(DeepResearchState)
        self.retry_policy = RetryPolicy(
            initial_interval=1.0,
            backoff_factor=2.0,
            max_interval=10.0,
            max_attempts=1,
            jitter=True,
        )
        self.cache_policy = CachePolicy()
        self.compiled_graph = self._build_graph()
        
    def _add_nodes(self):
        """
        Adds nodes to the graph.
        Each node corresponds to a specific role in the research process.
        """
        self.graph.add_node(
            NodeType.coordinator.name,
            Coordinator().invoke,
            retry_policy=self.retry_policy,
            cache_policy=self.cache_policy,
        )
        self.graph.add_node(
            NodeType.background_investigation.name,
            BackgroundInvestigation().invoke,
            retry_policy=self.retry_policy,
            cache_policy=self.cache_policy,
        )
        self.graph.add_node(
            NodeType.planner.name,
            Planner().invoke,
            retry_policy=self.retry_policy,
            cache_policy=self.cache_policy,
        )
        self.graph.add_node(
            NodeType.research_team.name,
            ResearchTeam().invoke,
            retry_policy=self.retry_policy,
            cache_policy=self.cache_policy,
        )
        self.graph.add_node(
            NodeType.researcher.name,
            Researcher().ainvoke,
            retry_policy=self.retry_policy,
            cache_policy=self.cache_policy,
        )
        self.graph.add_node(
            NodeType.coder.name,
            Coder().invoke,
            retry_policy=self.retry_policy,
            cache_policy=self.cache_policy,
        )
        self.graph.add_node(
            NodeType.reporter.name,
            Reporter().invoke,
            retry_policy=self.retry_policy,
            cache_policy=self.cache_policy,
        )
        self.graph.add_node(
            NodeType.human_feedback.name,
            HumanFeedback().invoke,
            retry_policy=self.retry_policy,
            cache_policy=self.cache_policy,
        )  
    
    def _add_edges(self):
        self.graph.add_edge(START, NodeType.coordinator.name)
        self.graph.add_edge(NodeType.background_investigation.name, NodeType.planner.name)
        self.graph.add_edge(NodeType.reporter.name, END)
        self.graph.add_conditional_edges(
            NodeType.research_team.name,
            self._add_conditional_research_team,
            [NodeType.researcher.name, NodeType.coder.name, NodeType.planner.name]
        )

    def _add_conditional_research_team(self, state: DeepResearchState):
        current_plan = state.current_plan

        if not current_plan or not current_plan.steps:
            return NodeType.planner.name
        if all(step.execution_res for step in current_plan.steps):
            return NodeType.planner.name
        
        # Each step is executed by a researcher/coder
        for step in current_plan.steps:
            if not step.execution_res:
                break
        if step.step_type == StepType.RESEARCH:
            return NodeType.researcher.name
        elif step.step_type == StepType.PROCESSING:
            return NodeType.coder.name
        
        return NodeType.planner.name
        
    def _build_graph(self, use_memory: bool = False) -> CompiledStateGraph:
        self._add_nodes()
        self._add_edges()
        if use_memory:
            from langgraph.checkpoint.memory import MemorySaver  # For debugging
            memory = MemorySaver()
            return self.graph.compile(memory)
        return self.graph.compile()
    
    def visualize_graph(
        self,
        visualization_type: str = "ascii",
        save_graph_path: str = "graph_visualization.png",
    ):
        if visualization_type == "ascii":
            self.compiled_graph.get_graph().print_ascii()
        else:
            from io import BytesIO
            from langchain_core.runnables.graph import MermaidDrawMethod
            from PIL import Image
            file = Image.open(
                BytesIO(
                    self.compiled_graph.get_graph().draw_mermaid_png(
                        draw_method=MermaidDrawMethod.API,
                    )
                )
            )
            file.save(save_graph_path)
    