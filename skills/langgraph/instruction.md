# LangGraph Skill — Quick-Start Reference

A one-page cheat sheet for the deep agent. Read `instructions.md` for the full workflow.

## Graph Shape Decision Table
| User goal | Pick |
|-----------|------|
| Fixed sequence of steps | Linear: `START → a → b → END` |
| Branch on a condition | Router: one router node + `add_conditional_edges` |
| LLM picks tools repeatedly | ReAct: `create_react_agent` |
| Multiple agents collaborating | Multi-agent: subgraphs or supervisor pattern |

## Minimal Correct Graph
```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    input: str
    result: str

def process(state: State) -> dict:        # node: returns PARTIAL update
    return {"result": state["input"].upper()}

graph = StateGraph(State)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)
app = graph.compile()
```

## Memory in 3 Lines
```python
from langgraph.checkpoint.memory import MemorySaver
app = graph.compile(checkpointer=MemorySaver())
app.invoke(inputs, config={"configurable": {"thread_id": "user-1"}})
```

## Conditional Edge Pattern
```python
def route(state: State) -> str:
    return "tools" if state["messages"][-1].tool_calls else END

graph.add_conditional_edges("llm", route, ["tools", END])
```

## Common Mistakes to Flag
- Forgetting `thread_id` when checkpointer is set → runtime error
- Mutating `state` in place instead of returning a new dict
- No reducer on a key written by multiple nodes → `InvalidUpdateError`
- Missing recursion limit increase for long agent loops

## Streaming
```python
for chunk in app.stream(inputs, config, stream_mode="updates"):
    for node, update in chunk.items():
        print(f"[{node}] {update}")
```
