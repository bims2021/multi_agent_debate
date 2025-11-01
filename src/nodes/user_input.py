from core.base_nodes import BaseNode
from core.state import DebateState, DebatePhase
from config.settings import DebateConfig
from agents.agent_registry import agent_registry
from datetime import datetime

class UserInputNode(BaseNode):
    """Node to handle user input and initialize debate"""
    
    def __init__(self, config: DebateConfig = None):
        super().__init__("user_input")
        self.config = config or DebateConfig()
    
    def execute(self, state: DebateState) -> DebateState:
        """Get user input and initialize debate state
        
        Args:
            state: Current debate state
            
        Returns:
            Updated state with topic and agent configuration
        """
        if state.get('topic'):
            return state  # Already initialized
        
        # Get topic from user
        print("\n" + "=" * 70)
        topic = input(" Enter topic for debate: ").strip()
        while not topic:
            print(" Topic cannot be empty. Please enter a valid topic.")
            topic = input(" Enter topic for debate: ").strip()
        
        self.logger.info(f"Debate topic set to: {topic}")
        
        # Get agent selection
        available_agents = agent_registry.get_available_agents()
        print(f"\n Available agents: {', '.join(available_agents)}")
        print(f"   Default: {', '.join(self.config.default_agents)}")
        print("   Enter agent names separated by commas (or press Enter for defaults):")
        agent_input = input("   > ").strip()
        
        if agent_input:
            selected_agents = [agent.strip().lower() for agent in agent_input.split(',')]
            # Validate agents
            valid_agents = [agent for agent in selected_agents if agent in available_agents]
            invalid_agents = [agent for agent in selected_agents if agent not in available_agents]
            
            if invalid_agents:
                print(f"⚠ Warning: Unknown agents ignored: {', '.join(invalid_agents)}")
            
            if len(valid_agents) < 2:
                print(f"⚠ Warning: Need at least 2 valid agents. Using defaults: {', '.join(self.config.default_agents)}")
                selected_agents = self.config.default_agents
            else:
                selected_agents = valid_agents
                print(f"✓ Selected agents: {', '.join(selected_agents)}")
        else:
            selected_agents = self.config.default_agents
            print(f"✓ Using default agents: {', '.join(selected_agents)}")
        
        # Create agents using registry
        try:
            agents = agent_registry.create_debate_agents(
                selected_agents,
                llm_model=self.config.llm_model,
                temperature=self.config.temperature
            )
            self.logger.info(f"Created {len(agents)} debate agents")
        except Exception as e:
            self.logger.error(f"Error creating agents: {e}")
            raise Exception(f"Failed to create debate agents: {e}")
        
        # Build agent configs from created agents
        agent_configs = {}
        for agent_id, agent in agents.items():
            agent_configs[agent_id] = {
                'name': agent.get_name(),
                'persona': agent.get_persona(),
                'description': agent.config.get('description', ''),
                'system_prompt': agent.config.get('system_prompt', ''),
                'llm_model': self.config.llm_model,
                'temperature': self.config.temperature
            }
        
        print(f"\n✓ Debate initialized with {len(selected_agents)} agents")
        print(f"✓ Maximum rounds: {self.config.max_rounds}")
        print("=" * 70 + "\n")
        
        # Initialize state
        return {
            **state,
            'topic': topic,
            'current_round': 0,
            'max_rounds': self.config.max_rounds,
            'phase': DebatePhase.DEBATE,
            'agent_order': selected_agents,
            'current_agent_index': 0,
            'agent_configs': agent_configs,
            'agent_memories': {agent_id: [] for agent_id in selected_agents},
            'full_transcript': [],
            'used_arguments': [],
            'last_argument': '',
            'judge_summary': '',
            'winner': '',
            'reasoning': '',
            'debate_complete': False,
            'start_time': str(datetime.now()),
            'end_time': '',
            'config': vars(self.config)
        }