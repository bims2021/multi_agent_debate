from typing import Dict, Type, Any, List
from agents.base_agent import BaseDebateAgent
from agents.llm_agent import LLMAgent

class AgentRegistry:
    """Registry for managing and creating debate agents"""
    
    def __init__(self):
        self._agent_classes: Dict[str, Type[BaseDebateAgent]] = {}
        self._default_configs = {}
        self._initialized = False
    
    def _lazy_init(self):
        """Lazy initialization to avoid circular imports"""
        if self._initialized:
            return
        
        # Import default configs
        from config.settings import DEFAULT_AGENTS_CONFIG
        self._default_configs = DEFAULT_AGENTS_CONFIG
        
        # Register default agents
        self.register_default_agents()
        self._initialized = True
    
    def register_agent(self, agent_type: str, agent_class: Type[BaseDebateAgent]):
        """Register a new agent type"""
        self._agent_classes[agent_type] = agent_class
    
    def register_default_agents(self):
        """Register default agent types"""
        # Import agent classes here to avoid circular imports
        from agents.scientist import ScientistAgent
        from agents.philosopher import PhilosopherAgent
        
        self.register_agent('scientist', ScientistAgent)
        self.register_agent('philosopher', PhilosopherAgent)
        self.register_agent('llm', LLMAgent)
    
    def create_agent(self, agent_id: str, agent_type: str = None, **config) -> BaseDebateAgent:
        """Create a new agent instance
        
        Args:
            agent_id: Identifier for the agent (e.g., 'scientist', 'philosopher')
            agent_type: Type of agent class to use (defaults to agent_id if registered)
            **config: Additional configuration parameters
        """
        self._lazy_init()
        
        # If no agent_type specified, try to use agent_id as the type
        if agent_type is None:
            agent_type = agent_id
        
        if agent_type not in self._agent_classes:
            raise ValueError(f"Unknown agent type: {agent_type}. Available: {list(self._agent_classes.keys())}")
        
        # Merge with default config if available
        if agent_id in self._default_configs:
            default_config = vars(self._default_configs[agent_id])
            config = {**default_config, **config}
        
        agent_class = self._agent_classes[agent_type]
        return agent_class(agent_id, config)
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agent configurations"""
        self._lazy_init()
        return list(self._default_configs.keys())
    
    def create_debate_agents(self, agent_ids: List[str], **global_config) -> Dict[str, BaseDebateAgent]:
        """Create multiple agents for a debate
        
        Args:
            agent_ids: List of agent identifiers
            **global_config: Global configuration (llm_model, temperature, etc.)
        """
        self._lazy_init()
        agents = {}
        for agent_id in agent_ids:
            # Each agent_id corresponds to its own agent type
            agents[agent_id] = self.create_agent(
                agent_id=agent_id,
                agent_type=agent_id,
                **global_config
            )
        return agents

# Global registry instance
agent_registry = AgentRegistry()