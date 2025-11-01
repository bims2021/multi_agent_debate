from core.base_nodes import BaseNode
from core.state import DebateState, DebatePhase

class RoundControllerNode(BaseNode):
    """Node to control debate rounds and progression"""
    
    def __init__(self):
        super().__init__("round_controller")
    
    def execute(self, state: DebateState) -> DebateState:
        """Control round progression and check completion
        
        A round is considered complete when all agents have spoken once.
        When we return to the first agent (index 0), we've completed a full round.
        """
        current_round = state['current_round']
        max_rounds = state['max_rounds']
        current_agent_index = state['current_agent_index']
        
        # Check if we just completed a round (all agents have spoken)
        # A round completes when we've cycled back to the first agent
        if current_agent_index == 0 and len(state['full_transcript']) > 0:
            # We're back at the first agent and have transcript entries
            # Check if the last entry was from the last agent in order
            last_entry = state['full_transcript'][-1]
            last_agent_id = last_entry.get('agent_id', '')
            
            # If last speaker was the last agent in order, round is complete
            if last_agent_id == state['agent_order'][-1]:
                current_round += 1
                self.logger.info(f"Round {current_round} completed")
        
        # Check if debate is complete
        debate_complete = current_round >= max_rounds
        
        if debate_complete:
            self.logger.info(f"Debate complete after {current_round} rounds")
        else:
            self.logger.info(f"Round progress: {current_round}/{max_rounds}")
        
        return {
            **state,
            'current_round': current_round,
            'debate_complete': debate_complete,
            'phase': DebatePhase.JUDGMENT if debate_complete else DebatePhase.DEBATE
        }