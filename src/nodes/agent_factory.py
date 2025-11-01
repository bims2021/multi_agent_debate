from core.base_nodes import BaseAgentNode
from core.state import DebateState
from agents.agent_registry import agent_registry
from datetime import datetime
import logging

class AgentNodeFactory:
    """Factory for creating dynamic agent nodes"""
    
    @staticmethod
    def create_agent_node(agent_id: str, agent_config: dict) -> BaseAgentNode:
        """Create a specialized agent node for a specific agent
        
        Args:
            agent_id: The identifier for the agent (e.g., 'scientist', 'philosopher')
            agent_config: Configuration dictionary for the agent
        """
        
        class DynamicAgentNode(BaseAgentNode):
            def __init__(self, agent_id: str, config: dict):
                super().__init__(agent_id, config)
                # Create the actual agent instance using registry
                # Use agent_id as the agent_type since they correspond
                self.agent = agent_registry.create_agent(
                    agent_id=agent_id,
                    agent_type=agent_id,
                    **config
                )
            
            def execute(self, state: DebateState) -> DebateState:
                """Execute agent's turn in the debate"""
                if not self.should_execute(state):
                    return state
                
                agent_name = self.get_agent_name()
                current_round = state['current_round']
                
                self.logger.info(f"ROUND {current_round + 1} - {agent_name.upper()} preparing argument...")
                
                # Get this agent's memory context
                memory = state['agent_memories'].get(self.agent_id, [])
                
                try:
                    # Generate argument using the specific agent implementation
                    argument = self.agent.generate_argument(
                        state['topic'],
                        memory,
                        state['used_arguments']
                    )
                except Exception as e:
                    self.logger.error(f"Error generating argument for {agent_name}: {e}")
                    argument = f"[{agent_name} encountered an error generating argument]"
                
                # Update all agent memories with this new argument
                new_memories = self.update_memories(state, argument)
                
                # Add to transcript
                new_transcript = state['full_transcript'] + [{
                    'round': current_round + 1,
                    'speaker': agent_name,
                    'agent_id': self.agent_id,
                    'argument': argument,
                    'timestamp': str(datetime.now())
                }]
                
                # Move to next agent in rotation
                next_agent_index = (state['current_agent_index'] + 1) % len(state['agent_order'])
                
                # Log the argument
                self.logger.info(f"[Round {current_round + 1}] {agent_name}: {argument[:100]}...")
                
                return {
                    **state,
                    'current_agent_index': next_agent_index,
                    'agent_memories': new_memories,
                    'full_transcript': new_transcript,
                    'used_arguments': state['used_arguments'] + [argument],
                    'last_argument': argument
                }
        
        return DynamicAgentNode(agent_id, agent_config)