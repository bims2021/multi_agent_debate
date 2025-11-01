from core.graph_builder import DebateGraphBuilder
from core.state import DebateState
from config.settings import DebateConfig
from utils.diagram_generator import save_graph_diagram, generate_simple_diagram
from utils.loggers import setup_logging, save_final_report, log_state_transition
from dotenv import load_dotenv
import os
import sys

load_dotenv()  # Load environment variables from .env file

def print_welcome():
    """Print welcome message and system overview"""
    print("=" * 70)
    print("               MODULAR DEBATE SIMULATION SYSTEM")
    print("=" * 70)
    print("\n✓ Features:")
    print("  • Dynamic agent selection (Scientist, Philosopher)")
    print("  • Configurable debate rounds and parameters") 
    print("  • Intelligent argument validation and memory management")
    print("  • Automated judging with detailed reasoning")
    print("  • Comprehensive logging and analytics")
    
    print("\n✓ System Architecture:")
    print(generate_simple_diagram())
    print("=" * 70)

def main():
    """Main CLI application with complete modular architecture"""
    # Setup logging first
    setup_logging()
    
    # Print welcome message
    print_welcome()
    
    # Configurable settings - easily modifiable
    config = DebateConfig(
        max_rounds=8,
        llm_model="gpt-3.5-turbo",
        judge_model="gpt-4", 
        temperature=0.7,
        judge_temperature=0.3,
        default_agents=["scientist", "philosopher"]  # Default debate pair
    )
    
    try:
        # Build graph dynamically based on configuration
        print("\n✓ Building debate graph...")
        graph_builder = DebateGraphBuilder(config)
        
        # Note: Agents will be selected during user input
        # The graph is built to handle dynamic agent selection
        graph = graph_builder.create_graph()
        
        # Save visualization
        print("\n✓ Generating system diagram...")
        try:
            save_graph_diagram(graph, "debate_system_diagram.png")
            print("  Diagram saved: debate_system_diagram.png")
        except Exception as e:
            print(f"  Warning: Could not save diagram: {e}")
        
        print("\n✓ Starting debate simulation...")
        print("  Please enter the debate topic and select participants when prompted.")
        print("-" * 70)
        
        # Initialize state - will be populated by UserInputNode
        initial_state = DebateState(
            topic="",
            current_round=0,
            max_rounds=config.max_rounds,
            phase="initialization",
            agent_order=[],
            current_agent_index=0,
            agent_configs={},
            agent_memories={},
            full_transcript=[],
            used_arguments=[],
            last_argument="",
            judge_summary="",
            winner="", 
            reasoning="",
            debate_complete=False,
            start_time="",
            end_time="",
            config=vars(config)
        )
        
        # Execute the graph
        print("\n✓ Executing debate workflow...")
        final_state = graph.invoke(initial_state, config={"recursion_limit": 100})
        
        # Display results
        print("\n" + "=" * 70)
        print("                      DEBATE COMPLETE")
        print("=" * 70)
        print(f"\n Topic: {final_state['topic']}")
        print(f" Participants: {', '.join(final_state['agent_order'])}")
        print(f" Rounds: {final_state['current_round']}/{final_state['max_rounds']}")
        
        print(f"\n JUDGE'S SUMMARY:")
        print("-" * 50)
        print(final_state['judge_summary'])
        print("-" * 50)
        
        print(f"\n WINNER: {final_state['winner']}")
        print(f"\n REASONING:")
        print(final_state['reasoning'])
        print("=" * 70)
        
        # Save comprehensive report
        try:
            report_path = save_final_report(final_state)
            print(f"\n✓ Report saved: {report_path}")
            print("  Check 'debate_logs/' directory for detailed analytics and transcripts")
        except Exception as e:
            print(f"\n Warning: Could not save report: {e}")
        
    except KeyboardInterrupt:
        print("\n\n Debate simulation cancelled by user.")
        sys.exit(0)
    except ImportError as e:
        print(f"\n Import Error: {e}")
        print("   Please ensure all dependencies are installed:")
        print("   pip install langchain langchain-openai python-dotenv")
        sys.exit(1)
    except Exception as e:
        print(f"\n Error during debate simulation: {e}")
        print("   Please check:")
        print("   - Your OpenAI API key is set (OPENAI_API_KEY environment variable)")
        print("   - You have internet connection")
        print("   - All required files are present")
        import traceback
        print("\n   Full error traceback:")
        traceback.print_exc()
        sys.exit(1)
    finally:
        print("\n✓ Thank you for using the Modular Debate Simulation System!")
        print("  Consider contributing new agents or features to expand the system!")

if __name__ == "__main__":
    main()