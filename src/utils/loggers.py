import logging
import os
import json
from datetime import datetime
from typing import Dict, Any
from core.state import DebateState

def setup_logging(log_dir: str = "debate_logs", level: int = logging.INFO):
    """Setup comprehensive logging configuration"""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Main transcript logger
    transcript_logger = logging.getLogger('transcript')
    transcript_logger.setLevel(level)
    
    transcript_handler = logging.FileHandler(
        os.path.join(log_dir, f"debate_transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    )
    transcript_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    transcript_handler.setFormatter(transcript_formatter)
    transcript_logger.addHandler(transcript_handler)
    
    # Console handler for real-time output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    transcript_logger.addHandler(console_handler)
    
    # State transition logger
    state_logger = logging.getLogger('state')
    state_logger.setLevel(logging.DEBUG)
    
    state_handler = logging.FileHandler(
        os.path.join(log_dir, f"state_transitions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    )
    state_formatter = logging.Formatter(
        '%(asctime)s - STATE - %(message)s'
    )
    state_handler.setFormatter(state_formatter)
    state_logger.addHandler(state_handler)

def save_final_report(state: DebateState, log_dir: str = "debate_logs"):
    """Save comprehensive debate report"""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    report = {
        'metadata': {
            'debate_topic': state['topic'],
            'total_rounds': state['max_rounds'],
            'completed_rounds': state['current_round'],
            'participants': state['agent_order'],
            'winner': state['winner'],
            'start_time': state['start_time'],
            'end_time': state['end_time'],
            'duration_minutes': calculate_duration(state['start_time'], state['end_time'])
        },
        'judgment': {
            'summary': state['judge_summary'],
            'reasoning': state['reasoning'],
            'winner': state['winner']
        },
        'performance_metrics': {
            'total_arguments': len(state['used_arguments']),
            'unique_arguments': len(set(state['used_arguments'])),
            'participant_contributions': count_contributions(state['full_transcript'])
        },
        'full_transcript': state['full_transcript'],
        'configuration': state.get('config', {})
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(log_dir, f"debate_report_{timestamp}.json")
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nFull debate report saved to: {filename}")
    return filename

def calculate_duration(start_time: str, end_time: str) -> float:
    """Calculate debate duration in minutes"""
    try:
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        duration = (end - start).total_seconds() / 60
        return round(duration, 2)
    except:
        return 0.0

def count_contributions(transcript: list) -> Dict[str, int]:
    """Count contributions by each participant"""
    contributions = {}
    for entry in transcript:
        speaker = entry['speaker']
        contributions[speaker] = contributions.get(speaker, 0) + 1
    return contributions

def log_state_transition(node_name: str, state: DebateState):
    """Log state transition for debugging"""
    logger = logging.getLogger('state')
    logger.debug(f"Node: {node_name} | Round: {state['current_round']} | "
                f"Current Agent: {state['agent_order'][state['current_agent_index']]} | "
                f"Phase: {state['phase']}")