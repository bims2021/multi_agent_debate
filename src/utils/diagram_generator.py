import os
import subprocess
from typing import Optional

def save_graph_diagram(graph, output_path: str = "debate_system_diagram.png") -> bool:
    """Generate and save visual diagram of the debate graph"""
    try:
        # Get mermaid representation
        mermaid_text = graph.get_graph().draw_mermaid()
        
        # Save mermaid source
        mmd_path = output_path.replace('.png', '.mmd')
        with open(mmd_path, 'w') as f:
            f.write(mermaid_text)
        
        # Try to generate PNG if graphviz is available
        try:
            graph.get_graph().draw_mermaid_png(output_file_path=output_path)
            print(f"Graph diagram saved as: {output_path}")
            return True
        except Exception as e:
            print(f"PNG generation failed: {e}. Mermaid source saved as: {mmd_path}")
            print("Install Graphviz for PNG generation: brew install graphviz (Mac) or apt-get install graphviz (Linux)")
            return False
            
    except Exception as e:
        print(f"Diagram generation failed: {e}")
        return False

def generate_simple_diagram() -> str:
    """Generate a simple text-based diagram for documentation"""
    diagram = """
    Debate System Flow:
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │ User Input  │───▶│   Agent A   │───▶│ Round Ctrl  │
    └─────────────┘    └─────────────┘    └─────────────┘
                                            │
    ┌─────────────┐    ┌─────────────┐      │
    │   Judge     │◀───│   Agent B   │◀─────┘
    └─────────────┘    └─────────────┘
    
    Key:
    - User Input: Topic and agent selection
    - Agent A/B: Dynamic agent nodes (2+ agents supported)
    - Round Controller: Manages turns and round completion  
    - Judge: Evaluates debate and declares winner
    """
    return diagram