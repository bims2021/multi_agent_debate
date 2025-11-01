from core.base_nodes import BaseNode
from core.state import DebateState, DebatePhase

class RoundControllerNode(BaseNode):
    """Node to control debate rounds and progression"""
    
    def __init__(self):
        super().__init__("round_controller")
    
    def execute(self, state: DebateState) -> DebateState:
        """Control round progression and check completion
        
        For 8 rounds with 2 agents:
        - Each speaking turn is 1 round
        - Total of 8 speaking turns = 4 per agent
        - Round increments after EACH agent speaks
        """
        current_round = state['current_round']
        max_rounds = state['max_rounds']
        
        # Count the number of arguments made so far
        # Each argument = 1 round
        total_arguments = len(state['full_transcript'])
        
        # Update current_round to match total arguments
        current_round = total_arguments
        
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