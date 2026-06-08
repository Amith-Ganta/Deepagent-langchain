# LangGraph Skill — Canonical Example

One complete, runnable deep agent with tools, memory, and streaming.

---

## Research Agent with Memory and Tool Calls

**Scenario:** A LangGraph ReAct agent that searches the web, remembers the conversation, and streams output.

```python
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent


# --- Tools ---

@tool
def search_web(query: str) -> str:
    """Search the web for up-to-date information on a topic.

    Args:
        query: The search query string.

    Returns:
        A short summary of the top search result.
    """
    # Replace with a real search API (e.g., Tavily, SerpAPI) in production.
    return f"[Mock result for '{query}']: LangGraph is a framework for building stateful agent workflows."


@tool
def calculator(expression: str) -> str:
    """Evaluate a simple arithmetic expression safely.

    Args:
        expression: A string like '2 + 2' or '10 * 3.5'.

    Returns:
        The numeric result as a string.

    Raises:
        ValueError: If the expression contains unsafe characters.
    """
    allowed = set("0123456789 +-*/.() ")
    if not all(c in allowed for c in expression):
        raise ValueError(f"Unsafe expression: {expression!r}")
    return str(eval(expression))  # noqa: S307 — guarded by allowlist above


# --- Agent ---

model = init_chat_model("anthropic:claude-sonnet-4-6")
checkpointer = MemorySaver()

agent = create_react_agent(
    model,
    tools=[search_web, calculator],
    checkpointer=checkpointer,
    state_modifier=(
        "You are a research assistant. Use search_web for factual queries "
        "and calculator for math. Be concise."
    ),
)

# --- Run with memory ---

config = {"configurable": {"thread_id": "research-session-1"}}

def chat(message: str) -> str:
    """Send a message and stream the agent's response."""
    full_response = ""
    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": message}]},
        config=config,
        stream_mode="values",
    ):
        last_msg = chunk["messages"][-1]
        if hasattr(last_msg, "content") and last_msg.type == "ai":
            full_response = last_msg.content
    return full_response


# Turn 1
print(chat("What is LangGraph?"))

# Turn 2 — agent remembers the previous question
print(chat("Can you give me an example of what you just described?"))

# Turn 3 — uses the calculator tool
print(chat("If I have 17 nodes and each has 3 edges, how many edges total?"))
```

**How it works:**
- `create_react_agent` builds the LLM → tool-call loop automatically.
- `MemorySaver` with a fixed `thread_id` persists conversation state across turns.
- `stream_mode="values"` emits the full graph state after each step; we grab the last AI message.
- Each tool has a docstring — the LLM uses it to decide when and how to call the tool.
- Swap `MemorySaver` for `SqliteSaver` or `PostgresSaver` for durable persistence.

**Dependencies:** `pip install langchain langchain-anthropic langgraph`
