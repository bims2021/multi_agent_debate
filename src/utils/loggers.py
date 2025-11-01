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
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Configure root logger first
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Main transcript logger
    transcript_logger = logging.getLogger('transcript')
    transcript_logger.setLevel(level)
    transcript_logger.propagate = False  # Don't propagate to root
    
    # Clear any existing handlers
    transcript_logger.handlers.clear()
    
    transcript_handler = logging.FileHandler(
        os.path.join(log_dir, f"debate_transcript_{timestamp}.log"),
        mode='w',
        encoding='utf-8'
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
    state_logger.propagate = False  # Don't propagate to root
    
    # Clear any existing handlers
    state_logger.handlers.clear()
    
    state_handler = logging.FileHandler(
        os.path.join(log_dir, f"state_transitions_{timestamp}.log"),
        mode='w',
        encoding='utf-8'
    )
    state_formatter = logging.Formatter(
        '%(asctime)s - STATE - %(message)s'
    )
    state_handler.setFormatter(state_formatter)
    state_logger.addHandler(state_handler)
    
    # Node loggers (for each node type)
    for node_name in ['user_input', 'round_controller', 'judge', 'memory_manager', 'agent_factory']:
        node_logger = logging.getLogger(f'node.{node_name}')
        node_logger.setLevel(logging.DEBUG)
        node_logger.propagate = False
        node_logger.handlers.clear()
        
        # Add file handler
        node_handler = logging.FileHandler(
            os.path.join(log_dir, f"debate_transcript_{timestamp}.log"),
            mode='a',
            encoding='utf-8'
        )
        node_handler.setFormatter(transcript_formatter)
        node_logger.addHandler(node_handler)
        
        # Add console handler
        node_console = logging.StreamHandler()
        node_console.setLevel(logging.INFO)
        node_console.setFormatter(logging.Formatter('%(message)s'))
        node_logger.addHandler(node_console)
    
    # Log initialization
    transcript_logger.info("=" * 70)
    transcript_logger.info("DEBATE SIMULATION STARTED")
    transcript_logger.info(f"Timestamp: {timestamp}")
    transcript_logger.info("=" * 70)
    
    state_logger.debug("State transition logging initialized")
    
    return transcript_logger, state_logger

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
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nFull debate report saved to: {filename}")
    
    # Also save a text version of the transcript
    text_filename = os.path.join(log_dir, f"debate_transcript_final_{timestamp}.txt")
    with open(text_filename, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("DEBATE TRANSCRIPT\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Topic: {state['topic']}\n")
        f.write(f"Participants: {', '.join(state['agent_order'])}\n")
        f.write(f"Rounds: {state['current_round']}/{state['max_rounds']}\n")
        f.write(f"Duration: {report['metadata']['duration_minutes']} minutes\n")
        f.write("\n" + "=" * 70 + "\n")
        f.write("ARGUMENTS\n")
        f.write("=" * 70 + "\n\n")
        
        for entry in state['full_transcript']:
            f.write(f"[Round {entry['round']}] {entry['speaker']}:\n")
            f.write(f"{entry['argument']}\n\n")
        
        f.write("=" * 70 + "\n")
        f.write("JUDGMENT\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Summary:\n{state['judge_summary']}\n\n")
        f.write(f"Winner: {state['winner']}\n\n")
        f.write(f"Reasoning:\n{state['reasoning']}\n")
    
    print(f"Text transcript saved to: {text_filename}")
    
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
    
    agent_index = state.get('current_agent_index', 0)
    agent_order = state.get('agent_order', [])
    current_agent = agent_order[agent_index] if agent_order and agent_index < len(agent_order) else 'unknown'
    
    logger.debug(f"Node: {node_name} | Round: {state.get('current_round', 0)} | "
                f"Current Agent: {current_agent} | "
                f"Phase: {state.get('phase', 'unknown')}")
    
    # Also log to transcript if it's an important transition
    if node_name in ['user_input', 'judge'] or node_name.startswith('agent_'):
        transcript_logger = logging.getLogger('transcript')
        transcript_logger.info(f"--- {node_name.upper()} NODE EXECUTED ---")

def log_argument(round_num: int, agent_name: str, argument: str):
    """Log an argument to transcript"""
    logger = logging.getLogger('transcript')
    logger.info(f"\n[Round {round_num}] {agent_name}:")
    logger.info(f"{argument}")
    logger.info("-" * 70)