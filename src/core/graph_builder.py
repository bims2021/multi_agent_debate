from langgraph.graph import StateGraph, END
from core.state import DebateState
from nodes.user_input import UserInputNode
from nodes.round_controller import RoundControllerNode
from nodes.judge import JudgeNode
from nodes.memory_manager import MemoryManagerNode
from nodes.agent_factory import AgentNodeFactory
from typing import List, Dict, Any
from config.settings import DebateConfig

class DebateGraphBuilder:
    """Builds and configures the debate graph dynamically using factory pattern"""
    
    def __init__(self, config: DebateConfig = None):
        self.config = config or DebateConfig()
        self.graph = StateGraph(DebateState)
        self.nodes = {}
    
    def add_user_input(self):
        """Add user input node"""
        user_input_node = UserInputNode(self.config)
        self.graph.add_node("user_input", user_input_node)
        self.nodes["user_input"] = user_input_node
        return self
    
    def add_agents(self, agent_ids: List[str] = None):
        """Add agent nodes dynamically using AgentNodeFactory"""
        if agent_ids is None:
            agent_ids = self.config.default_agents
        
        for agent_id in agent_ids:
            # Create agent configuration
            agent_config = {
                'llm_model': self.config.llm_model,
                'temperature': self.config.temperature
            }
            
            # Use factory to create specialized agent node
            agent_node = AgentNodeFactory.create_agent_node(agent_id, agent_config)
            node_name = f"agent_{agent_id}"
            
            self.graph.add_node(node_name, agent_node)
            self.nodes[node_name] = agent_node
        
        return self
    
    def add_round_controller(self):
        """Add round controller node"""
        round_controller = RoundControllerNode()
        self.graph.add_node("round_controller", round_controller)
        self.nodes["round_controller"] = round_controller
        return self
    
    def add_memory_manager(self):
        """Add memory manager node (optional)"""
        memory_manager = MemoryManagerNode()
        self.graph.add_node("memory_manager", memory_manager)
        self.nodes["memory_manager"] = memory_manager
        return self
    
    def add_judge(self):
        """Add judge node"""
        judge_config = {
            'judge_model': self.config.judge_model,
            'judge_temperature': self.config.judge_temperature
        }
        judge_node = JudgeNode(judge_config)
        self.graph.add_node("judge", judge_node)
        self.nodes["judge"] = judge_node
        return self
    
    # --- NEW ROUTER FUNCTION ---
    def _round_controller_router(self, agent_ids: List[str]):
        """Router to determine next step from Round Controller: Agent or Judge"""
        def router(state: DebateState):
            # If the RoundControllerNode set 'debate_complete' to True, go to the Judge.
            if state.get('debate_complete'):
                return "judge"
            
            # Otherwise, route to the next agent based on the updated index.
            next_agent_id = agent_ids[state['current_agent_index']]
            return f"agent_{next_agent_id}"
        return router
    # ---------------------------
    
    def build_flow(self, agent_ids: List[str] = None):
        """Build the complete graph flow"""
        if agent_ids is None:
            agent_ids = self.config.default_agents
        
        # Set entry point
        self.graph.set_entry_point("user_input")
        
        # From user input, go to first agent
        self.graph.add_edge("user_input", f"agent_{agent_ids[0]}")
        
        # Build the debate loop: Agent -> Round Controller
        for agent_id in agent_ids:
            current_agent_node = f"agent_{agent_id}"
            
            # After each agent runs, ALWAYS go to the Round Controller (unconditional edge).
            # The controller will update the state (e.g., increment index) and decide the next node.
            self.graph.add_edge(current_agent_node, "round_controller")
        
        # The Round Controller now handles the conditional routing.
        # Create a mapping for all possible transitions from the Round Controller (all agents + judge).
        conditional_mapping = {f"agent_{aid}": f"agent_{aid}" for aid in agent_ids}
        conditional_mapping["judge"] = "judge" 
        
        # Round controller decides the next step (Agent or Judge) using the new router.
        self.graph.add_conditional_edges(
            "round_controller", 
            self._round_controller_router(agent_ids), 
            conditional_mapping
        )
        
        # Judge is the definitive end point
        self.graph.add_edge("judge", END)
        
        return self.graph.compile()
    
    def create_graph(self, agent_ids: List[str] = None) -> Any:
        """Create complete graph with all nodes"""
        if agent_ids is None:
            agent_ids = self.config.default_agents
        
        return (self
                .add_user_input()
                .add_agents(agent_ids)
                .add_round_controller()
                .add_judge()
                .build_flow(agent_ids))