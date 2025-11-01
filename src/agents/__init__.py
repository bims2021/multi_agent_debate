from agents.base_agent import BaseDebateAgent
from agents.llm_agent import LLMAgent
from agents.scientist import ScientistAgent
from agents.philosopher import PhilosopherAgent
from agents.agent_registry import AgentRegistry, agent_registry

# Register concrete agent implementations
agent_registry.register_agent('scientist', ScientistAgent)
agent_registry.register_agent('philosopher', PhilosopherAgent) 
agent_registry.register_agent('llm', LLMAgent)  # Generic LLM agent

__all__ = [
    'BaseDebateAgent',
    'LLMAgent', 
    'ScientistAgent',
    'PhilosopherAgent',
    'AgentRegistry',
    'agent_registry'
]