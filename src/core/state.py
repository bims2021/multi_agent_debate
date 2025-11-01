from typing import Dict, List, Any, Optional, TypedDict
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class DebatePhase(str, Enum):
    """Debate phases - inherits from str for TypedDict compatibility"""
    INIT = "initialization"
    DEBATE = "debate"
    JUDGMENT = "judgment"
    COMPLETE = "complete"

class DebateState(TypedDict):
    """Type definition for debate state"""
    # Core debate properties
    topic: str
    current_round: int
    max_rounds: int
    phase: str  # Changed from DebatePhase to str for compatibility
    
    # Agent management
    agent_order: List[str]
    current_agent_index: int
    agent_configs: Dict[str, Any]
    
    # Memory and content
    agent_memories: Dict[str, List[str]]
    full_transcript: List[Dict[str, Any]]
    used_arguments: List[str]
    last_argument: str
    
    # Results
    judge_summary: str
    winner: str
    reasoning: str
    debate_complete: bool
    
    # Metadata
    start_time: str
    end_time: str
    config: Dict[str, Any]