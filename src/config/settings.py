from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class DebateConfig:
    max_rounds: int = 8  # Changed to 8 as per task requirement
    default_agents: List[str] = None
    llm_model: str = "gpt-3.5-turbo"
    judge_model: str = "gpt-4"
    temperature: float = 0.7
    judge_temperature: float = 0.3
    max_memory_size: int = 10  # For memory management
    
    def __post_init__(self):
        if self.default_agents is None:
            self.default_agents = ["scientist", "philosopher"]

@dataclass
class AgentConfig:
    name: str
    persona: str
    description: str
    system_prompt: str

# Default agent configurations
DEFAULT_AGENTS_CONFIG: Dict[str, AgentConfig] = {
    "scientist": AgentConfig(
        name="Scientist",
        persona="Research Scientist",
        description="Expert in empirical evidence and data-driven decision making",
        system_prompt="""You are a research scientist with expertise in technology and empirical evidence. 
        You value data, reproducibility, and evidence-based decision making. You're pragmatic and focus on 
        measurable outcomes and risk assessment. Your arguments should be:
        - Grounded in scientific principles
        - Supported by evidence or logical reasoning
        - Focused on practical implications
        - Analytical and objective
        
        Avoid philosophical speculation and focus on verifiable facts and logical consequences."""
    ),
    "philosopher": AgentConfig(
        name="Philosopher", 
        persona="Ethics Philosopher",
        description="Specialist in ethical principles and philosophical frameworks",
        system_prompt="""You are a philosopher specializing in ethics and epistemology. 
        You value logical consistency, ethical principles, and theoretical frameworks. 
        You're concerned with broader implications, human values, and philosophical consistency.
        Your arguments should be:
        - Ethically grounded and principled
        - Conceptually rigorous
        - Focused on long-term implications
        - Concerned with human values and rights
        
        Bring philosophical perspectives like utilitarianism, deontology, or virtue ethics to bear on issues."""
    ),
    
}

# Logging configuration
LOG_DIR = "debate_logs"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

# Validation settings - FIXED to match validators.py parameter names
VALIDATION_CONFIG = {
    'min_argument_length': 10,      # min_length parameter in ArgumentValidator
    'similarity_threshold': 0.7,     # max_similarity parameter in ArgumentValidator
    'max_refinement_attempts': 3
}