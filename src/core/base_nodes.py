from abc import ABC, abstractmethod
from typing import Any, Dict, List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from core.state import DebateState
import logging

class BaseNode(ABC):
    """Abstract base class for all graph nodes"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"node.{name}")
    
    @abstractmethod
    def execute(self, state: DebateState) -> DebateState:
        """Execute node logic and return updated state"""
        pass
    
    def __call__(self, state: DebateState) -> DebateState:
        """Make node callable by LangGraph"""
        self.logger.info(f"Executing node: {self.name}")
        
        # Log state transition
        from utils.loggers import log_state_transition
        log_state_transition(self.name, state)
        
        result = self.execute(state)
        
        # Log after execution
        self.logger.debug(f"Node {self.name} completed")
        
        return result

class BaseAgentNode(BaseNode):
    """Base class for agent nodes with common functionality"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(f"agent_{agent_id}")
        self.agent_id = agent_id
        self.config = config
        self.llm = ChatOpenAI(
            model=config.get('llm_model', 'gpt-3.5-turbo'),
            temperature=config.get('temperature', 0.7)
        )
    
    def get_agent_name(self) -> str:
        """Get display name for the agent"""
        return self.config.get('name', self.agent_id.title())
    
    def should_execute(self, state: DebateState) -> bool:
        """Check if this agent should speak in current turn"""
        if state['debate_complete']:
            return False
        
        current_agent = state['agent_order'][state['current_agent_index']]
        return current_agent == self.agent_id
    
    def update_memories(self, state: DebateState, argument: str) -> Dict[str, List[str]]:
        """Update memories for all agents"""
        agent_name = self.get_agent_name()
        new_memories = state['agent_memories'].copy()
        
        for agent_id in state['agent_memories']:
            memory_entry = f"{agent_name}: {argument}"
            new_memories[agent_id] = new_memories[agent_id] + [memory_entry]
        
        return new_memories