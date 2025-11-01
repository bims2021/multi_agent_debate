from agents.base_agent import BaseDebateAgent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List, Dict, Any

class LLMAgent(BaseDebateAgent):
    """LLM-powered debate agent with persona-based argument generation"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        super().__init__(agent_id, config)
        self.llm = ChatOpenAI(
            model=config.get('llm_model', 'gpt-3.5-turbo'),
            temperature=config.get('temperature', 0.7)
        )
    
    def generate_argument(self, topic: str, memory: List[str], used_arguments: List[str]) -> str:
        """Generate argument using LLM with persona context
        
        Args:
            topic: The debate topic
            memory: This agent's previous arguments
            used_arguments: All arguments in the debate
            
        Returns:
            Generated argument
        """
        system_prompt = self._build_system_prompt(topic, used_arguments, memory)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Provide your argument about: {topic}")
        ]
        
        try:
            response = self.llm.invoke(messages)
            argument = response.content.strip()
            
            # Validate and refine if necessary
            return self.validate_and_refine_argument(argument, used_arguments)
        except Exception as e:
            # Fallback argument in case of API error
            return f"[Error generating argument: {str(e)}]"
    
    def refine_argument(self, refinement_prompt: str) -> str:
        """Refine an argument based on feedback
        
        Args:
            refinement_prompt: Prompt explaining what needs to be refined
            
        Returns:
            Refined argument
        """
        persona = self.config.get('system_prompt', '')
        
        messages = [
            SystemMessage(content=f"{persona}\n\nYou need to refine your argument."),
            HumanMessage(content=refinement_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content.strip()
        except Exception as e:
            raise Exception(f"Failed to refine argument: {str(e)}")
    
    def _build_system_prompt(self, topic: str, used_arguments: List[str], memory: List[str]) -> str:
        """Build system prompt with persona and context
        
        Args:
            topic: Debate topic
            used_arguments: All arguments used so far
            memory: This agent's memory
            
        Returns:
            Complete system prompt
        """
        persona = self.config.get('system_prompt', 'You are a participant in a formal debate.')
        
        # Get recent context (last 3 used arguments, last 2 from memory)
        recent_used = used_arguments[-3:] if used_arguments else []
        recent_memory = memory[-2:] if memory else []
        
        context_section = ""
        if recent_memory:
            context_section += f"\n\nYour previous arguments:\n" + "\n".join(f"- {arg[:100]}..." for arg in recent_memory)
        
        if recent_used:
            context_section += f"\n\nRecent arguments from all participants (DO NOT REPEAT):\n" + "\n".join(f"- {arg[:100]}..." for arg in recent_used)
        
        return f"""{persona}

Debate Topic: {topic}
{context_section}

Instructions:
1. Provide a logical, well-reasoned argument from your professional perspective
2. DO NOT repeat or closely mirror previous arguments - offer NEW insights
3. Build upon or counter previous points when relevant
4. Keep arguments concise but substantive (2-4 sentences, 30-100 words)
5. Maintain professional tone and stay in character
6. Be specific and avoid vague generalities

Your response should be ONLY your argument, with no meta-commentary or explanations."""