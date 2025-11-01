from core.base_nodes import BaseNode
from core.state import DebateState, DebatePhase
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from datetime import datetime
import json
import re

class JudgeNode(BaseNode):
    """Node to evaluate debate and declare winner"""
    
    def __init__(self, config: dict = None):
        super().__init__("judge")
        self.config = config or {}
        self.llm = ChatOpenAI(
            model=self.config.get('judge_model', 'gpt-4'),
            temperature=self.config.get('judge_temperature', 0.3)
        )
    
    def execute(self, state: DebateState) -> DebateState:
        if not state['debate_complete'] or state['phase'] != DebatePhase.JUDGMENT:
            return state
        
        self.logger.info("Evaluating debate and declaring winner...")
        
        # Build transcript and agent info
        transcript_text = self._build_transcript_text(state)
        agent_info = self._build_agent_info(state)
        agent_names = [state['agent_configs'][agent_id]['name'] for agent_id in state['agent_order']]
        
        try:
            judgment = self._evaluate_debate(state['topic'], transcript_text, agent_info, agent_names)
            self.logger.info(f"Judgment complete. Winner: {judgment['winner']}")
        except Exception as e:
            self.logger.error(f"Error during judgment: {e}")
            judgment = {
                'summary': 'Error occurred during judgment',
                'winner': 'Tie',
                'reasoning': f'Unable to complete judgment due to error: {str(e)}'
            }
        
        return {
            **state,
            'judge_summary': judgment['summary'],
            'winner': judgment['winner'],
            'reasoning': judgment['reasoning'],
            'phase': DebatePhase.COMPLETE,
            'end_time': str(datetime.now())
        }
    
    def _build_transcript_text(self, state: DebateState) -> str:
        """Build formatted transcript from debate history"""
        return "\n".join([
            f"Round {entry['round']} - {entry['speaker']}: {entry['argument']}"
            for entry in state['full_transcript']
        ])
    
    def _build_agent_info(self, state: DebateState) -> str:
        """Build agent information summary"""
        agent_descriptions = []
        for agent_id in state['agent_order']:
            config = state['agent_configs'][agent_id]
            agent_descriptions.append(
                f"{config['name']} ({config['persona']}): {config['description']}"
            )
        return "\n".join(agent_descriptions)
    
    def _evaluate_debate(self, topic: str, transcript: str, agent_info: str, agent_names: list) -> dict:
        """Evaluate the debate and determine winner using structured output"""
        system_message = """You are an impartial debate judge. Evaluate arguments based on:
        - Logical consistency and reasoning quality
        - Evidence and support for claims
        - Relevance to the topic and avoidance of repetition
        - Persuasiveness and rhetorical quality
        - Adherence to persona and perspective
        
        Provide a comprehensive summary and declare a clear winner with detailed justification."""
        
        # Create structured output request
        agent_names_str = ", ".join(agent_names)
        prompt = f"""
        DEBATE TOPIC: {topic}
        
        PARTICIPANTS:
        {agent_info}
        
        COMPLETE TRANSCRIPT:
        {transcript}
        
        Please evaluate this debate and provide your judgment in the following JSON format:
        {{
            "summary": "A comprehensive summary of the debate (3-5 sentences)",
            "winner": "The exact name of the winning agent (must be one of: {agent_names_str}) or 'Tie'",
            "reasoning": "Detailed reasoning for your decision (4-6 sentences explaining why the winner prevailed)"
        }}
        
        IMPORTANT: The "winner" field must contain EXACTLY one of these values: {agent_names_str}, or "Tie"
        """
        
        messages = [
            SystemMessage(content=system_message),
            HumanMessage(content=prompt)
        ]
        
        response = self.llm.invoke(messages)
        return self._parse_judgment(response.content, agent_names)
    
    def _parse_judgment(self, judgment_text: str, agent_names: list) -> dict:
        """Parse judgment from LLM response with robust extraction"""
        try:
            # Try to extract JSON if present
            json_match = re.search(r'\{[\s\S]*\}', judgment_text)
            if json_match:
                judgment_data = json.loads(json_match.group())
                
                # Validate winner field
                winner = judgment_data.get('winner', 'Tie')
                if winner not in agent_names and winner != 'Tie':
                    # Try to find closest match
                    winner = self._find_closest_agent_name(winner, agent_names)
                
                return {
                    'summary': judgment_data.get('summary', 'No summary provided'),
                    'reasoning': judgment_data.get('reasoning', 'No reasoning provided'),
                    'winner': winner
                }
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse JSON judgment, falling back to text parsing")
        
        # Fallback: Parse unstructured text
        return self._parse_unstructured_judgment(judgment_text, agent_names)
    
    def _parse_unstructured_judgment(self, judgment_text: str, agent_names: list) -> dict:
        """Fallback parser for unstructured judgment text"""
        lines = judgment_text.split('\n')
        summary_lines = []
        reasoning_lines = []
        winner = "Tie"
        
        current_section = None
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            line_lower = line_stripped.lower()
            
            # Detect sections
            if 'summary' in line_lower and len(line_stripped) < 50:
                current_section = 'summary'
                continue
            elif any(word in line_lower for word in ['reasoning', 'justification', 'decision']) and len(line_stripped) < 50:
                current_section = 'reasoning'
                continue
            elif 'winner' in line_lower and len(line_stripped) < 100:
                # Extract winner from this line
                for name in agent_names:
                    if name.lower() in line_lower:
                        winner = name
                        break
                continue
            
            # Collect content
            if current_section == 'summary':
                summary_lines.append(line_stripped)
            elif current_section == 'reasoning':
                reasoning_lines.append(line_stripped)
            else:
                # Before sections are identified, look for winner
                for name in agent_names:
                    if name.lower() in line_lower and any(word in line_lower for word in ['winner', 'wins', 'victory', 'prevails']):
                        winner = name
        
        return {
            'summary': ' '.join(summary_lines) if summary_lines else judgment_text[:500],
            'reasoning': ' '.join(reasoning_lines) if reasoning_lines else "See full judgment above",
            'winner': winner
        }
    
    def _find_closest_agent_name(self, winner_text: str, agent_names: list) -> str:
        """Find the closest matching agent name from the winner text"""
        winner_lower = winner_text.lower()
        
        # Direct substring match
        for name in agent_names:
            if name.lower() in winner_lower or winner_lower in name.lower():
                return name
        
        # If no match found, default to Tie
        return "Tie"