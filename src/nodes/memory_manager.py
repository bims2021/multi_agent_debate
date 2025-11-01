from core.base_nodes import BaseNode
from core.state import DebateState
from typing import List, Dict
import logging

class MemoryManagerNode(BaseNode):
    """Node for managing and optimizing agent memories"""
    
    def __init__(self, max_memory_size: int = 10):
        super().__init__("memory_manager")
        self.max_memory_size = max_memory_size
    
    def execute(self, state: DebateState) -> DebateState:
        """Optimize memories by removing oldest entries if needed"""
        if not state.get('agent_memories'):
            return state
        
        optimized_memories = {}
        for agent_id, memory in state['agent_memories'].items():
            # Keep only the most recent entries
            if len(memory) > self.max_memory_size:
                optimized_memory = memory[-self.max_memory_size:]
                self.logger.info(f"Trimmed memory for {agent_id}: {len(memory)} -> {len(optimized_memory)}")
            else:
                optimized_memory = memory
            
            optimized_memories[agent_id] = optimized_memory
        
        return {
            **state,
            'agent_memories': optimized_memories
        }
    
    def get_relevant_context(self, agent_id: str, memories: Dict[str, List[str]]) -> List[str]:
        """Get relevant context for a specific agent"""
        relevant_memory = []
        
        # Always include the agent's own recent arguments
        if agent_id in memories:
            relevant_memory.extend(memories[agent_id][-3:])
        
        # Include recent arguments from other agents
        for other_agent, memory in memories.items():
            if other_agent != agent_id and memory:
                relevant_memory.append(memory[-1])  # Most recent argument
        
        return relevant_memory[-5:]  # Last 5 relevant items