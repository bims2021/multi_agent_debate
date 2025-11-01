from abc import ABC, abstractmethod
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
import re
from utils.validators import ArgumentValidator
from config.settings import VALIDATION_CONFIG

class BaseDebateAgent(ABC):
    """Abstract base class for all debate agents"""
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        self.agent_id = agent_id
        self.config = config
        # Match the parameter names from your validators.py
        self.validator = ArgumentValidator(
            min_length=VALIDATION_CONFIG.get('min_argument_length', 10),
            max_similarity=VALIDATION_CONFIG.get('similarity_threshold', 0.7)  
        )
        self.llm = None  # To be initialized by subclasses if needed
    
    @abstractmethod
    def generate_argument(self, topic: str, memory: List[str], used_arguments: List[str]) -> str:
        """Generate a debate argument based on topic and context
        
        Args:
            topic: The debate topic
            memory: This agent's conversation memory
            used_arguments: All arguments used so far in the debate
            
        Returns:
            Generated argument string
        """
        pass
    
    def get_name(self) -> str:
        """Get the display name of the agent"""
        return self.config.get('name', self.agent_id.title())
    
    def get_persona(self) -> str:
        """Get the persona description"""
        return self.config.get('persona', 'Debater')
    
    def validate_and_refine_argument(self, argument: str, used_arguments: List[str], max_attempts: int = None) -> str:
        """Validate argument and refine if necessary
        
        Args:
            argument: The argument to validate
            used_arguments: Previously used arguments
            max_attempts: Maximum refinement attempts (from config if not provided)
            
        Returns:
            Valid argument (either original or refined)
        """
        if max_attempts is None:
            max_attempts = VALIDATION_CONFIG.get('max_refinement_attempts', 3)
        
        for attempt in range(max_attempts):
            # Check if argument is valid
            if self.validator.is_valid_argument(argument, used_arguments):
                return argument
            
            # Get specific validation errors using your validator's method
            feedback = self.validator.get_validation_feedback(argument, used_arguments)
            
            # If this is the last attempt, return what we have
            if attempt == max_attempts - 1:
                return argument
            
            # Try to refine the argument
            if hasattr(self, 'refine_argument'):
                refinement_prompt = self._build_refinement_prompt(argument, used_arguments, feedback)
                try:
                    argument = self.refine_argument(refinement_prompt)
                except Exception as e:
                    # If refinement fails, return original
                    return argument
            else:
                # No refinement capability, return as-is
                return argument
        
        return argument
    
    def _build_refinement_prompt(self, argument: str, used_arguments: List[str], feedback: str) -> str:
        """Build a prompt for refining an invalid argument"""
        recent_args = used_arguments[-5:] if used_arguments else []
        
        return f"""
        Your previous argument was rejected for the following reason:
        {feedback}
        
        Recent arguments to avoid repeating:
        {chr(10).join(f'- {arg[:100]}...' for arg in recent_args) if recent_args else 'None'}
        
        Please provide a DIFFERENT, more substantial argument that:
        1. Is at least 10 words and substantive
        2. Offers a genuinely novel perspective or point
        3. Is well-reasoned and stays in character
        4. Does not repeat or closely mirror previous arguments
        5. Uses logical connectors (because, therefore, however)
        
        Original argument: {argument}
        
        Provide ONLY your refined argument, with no meta-commentary.
        """