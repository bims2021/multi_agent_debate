#  Modular Debate Simulation System


A sophisticated **LangGraph-based system** that simulates structured debates between AI agents with distinct professional personas.  
It features dynamic agent selection, memory management, and automated judgment — all within a modular, extensible architecture.

---

## Features

- **Dynamic Agent System** – Choose from multiple professional personas (Scientist, Philosopher, Economist, etc.)
- **Modular Architecture** – Easily add new agents, nodes, and validation rules
- **Structured Debates** – Configurable rounds with alternating turns
- **Contextual Memory** – Each agent maintains relevant debate history
- **Intelligent Judgment** – GPT-4-powered evaluation with detailed reasoning
- **Comprehensive Logging** – Full state tracking and analytics
- **Visualization** – Automatic LangGraph diagram generation

---

##  Architecture Highlights

- **Modular Design** – Clean separation of concerns with factory and registry patterns  
- **LangGraph Integration** – State-machine–based debate flow control  
- **Type-Safe** – Full type hints and `TypedDict` state management  
- **Extensible** – Easy to add new agent types, validation rules, and debate logic  

###  Project Structure

```
multi_agent_debate/
│
├── src/
│   ├── config/
│   ├── core/
│   ├── agents/
│   ├── nodes/
│   ├── utils/
│   ├── .env
│   └── main.py
│
├── debate_logs/
├── README.md
└── requirements.txt
```

---

##  Core Components

### 1. **State Management** (`core/state.py`)
- Type-safe `TypedDict` structure for debate phases and agent memory
- Tracks progress, arguments, and results
- Immutable state updates for predictability

### 2. **Graph Builder** (`core/graph_builder.py`)
- Constructs LangGraph state machine
- Conditional routing between nodes
- Dynamically builds agent interaction graph

### 3. **Agent System**
- **Base Classes:** `BaseDebateAgent`, `LLMAgent`
- **Factory Pattern:** `AgentNodeFactory` for on-the-fly creation
- **Registry:** `AgentRegistry` for managing available personas
- **Specialized Agents:** Scientist, Philosopher, Economist, Lawyer

### 4. **Validation Layer** (`utils/validators.py`)
- Argument quality and novelty checks
- Substance and relevance validation
- Prevents repetition and empty responses

### 5. **Control Nodes**
- `UserInputNode`: Handles initialization and setup  
- `RoundControllerNode`: Manages turn-taking logic  
- `JudgeNode`: Evaluates arguments and declares winner  
- `MemoryManagerNode`: Handles context pruning and relevance filtering  

---

##  Agent Personas

###  **Scientist**
- **Expertise:** Empirical evidence, data-driven reasoning  
- **Style:** Pragmatic, analytical  
- **Example:**  
  > “Research indicates that AI regulation could reduce bias in automated decision-making by 40%, based on controlled studies in healthcare and finance.”

###  **Philosopher**
- **Expertise:** Ethics, logical reasoning, moral frameworks  
- **Style:** Principled and conceptual  
- **Example:**  
  > “From a deontological perspective, AI regulation respects human autonomy by ensuring transparency, which is a fundamental right.”

---

##  Prerequisites

- Python **3.8+**
- **OpenAI API key**
- **Graphviz** (for visualization)

---

##  Setup

```bash
# Clone the repository
git clone <repository-url>
cd multi_agent_debate

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

##  Basic Usage

```bash
python main.py
```

You’ll be prompted to enter a topic and select agents:

```
Enter topic for debate: Should AI be regulated by governments?

Available agents: scientist, philosopher, economist, lawyer
Default: scientist, philosopher

Enter agent names separated by commas (or press Enter for defaults):
> 

Selected agents: scientist, philosopher
Debate initialized with 2 agents
Maximum rounds: 3
```

[Debate proceeds…]

**WINNER: Philosopher**

---

##  System Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Debate System Flow                        │
└─────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │ User Input   │  ← Get topic & select agents
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   Agent A    │  ← Generate argument
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │ Round Ctrl   │  ← Manage turns and state
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │   Agent B    │  ← Generate counter-argument
    └──────┬───────┘
           │
           ▼
    ┌──────────────┐
    │    Judge     │  ← Evaluate & declare winner
    └──────────────┘
```

---

##  Output & Logs

All results and transcripts are automatically stored in `debate_logs/`:

```
debate_logs/
├── debate_transcript_20250131_143022.log
├── debate_transcript_final
├── state_transitions_20250131_143022.log
└── debate_report_20250131_143055.json
```

---

##  Extending the System

### ➕ Adding a New Agent

**1. Create the agent class** (`agents/historian.py`):
```python
from agents.llm_agent import LLMAgent

class HistorianAgent(LLMAgent):
    def __init__(self, agent_id: str = "historian", config: dict = None):
        default_config = {
            "name": "Historian",
            "persona": "Historical Analyst",
            "description": "Expert in historical patterns and precedents",
            "system_prompt": "You are a historian who analyzes current issues through historical patterns..."
        }
        merged_config = {**default_config, **(config or {})}
        super().__init__(agent_id, merged_config)
```

**2. Register the agent** (`config/settings.py`):
```python
DEFAULT_AGENTS_CONFIG["historian"] = AgentConfig(
    name="Historian",
    persona="Historical Analyst",
    description="Expert in historical patterns",
    system_prompt="..."
)
```

**3. Register in the Agent Registry** (`agents/agent_registry.py`):
```python
def register_default_agents(self):
    from agents.historian import HistorianAgent
    self.register_agent("historian", HistorianAgent)
    # ... existing agents
```

---

###  Custom Validation Rules

Extend `ArgumentValidator` in `utils/validators.py`:
```python
def is_valid_argument(self, argument: str, used_arguments: List[str]) -> bool:
    return (
        self.has_minimum_length(argument)
        and self.has_substance(argument)
        and self.is_novel(argument, used_arguments)
        and self.is_relevant(argument)
        and self.custom_rule(argument)
    )

def custom_rule(self, argument: str) -> bool:
    # Custom validation logic
    return True
```

---

###  Creating Custom Nodes

```python
from core.base_nodes import BaseNode

class CustomNode(BaseNode):
    def __init__(self):
        super().__init__("custom_node")

    def execute(self, state: DebateState) -> DebateState:
        # Your custom logic here
        return state
```

---

##  Troubleshooting

| Issue | Solution |
|-------|-----------|
| **Graphviz not found** | Install Graphviz via system package and ensure `pygraphviz` is installed |
| **API rate limits** | Reduce debate rounds, switch to `gpt-3.5-turbo`, or add retry logic |
| **Memory issues** | Reduce `max_rounds`, implement memory pruning, or enable context management |

---

##  Getting Help

- Review generated log files in `debate_logs/`
- Verify API key permissions and usage quotas
- Ensure all dependencies are correctly installed

---

##  License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

##  Acknowledgments

- Built with **LangGraph** for stateful workflow orchestration  
- Uses **LangChain** for LLM integration  
- Inspired by **formal debate structures** and **multi-agent systems**
