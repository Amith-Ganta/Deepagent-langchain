# Report Writer Skill — Canonical Example

One complete report showing the expected quality and format.

---

## Scenario

User asked: "How do I build a LangGraph agent that remembers conversations?"

The deep agent answered using the `langgraph` and `python` skills. After answering, it saved the following report:

**Saved to:** `/reports/langgraph-conversational-memory-report.md`

---

## The Report

```markdown
# Report: LangGraph Conversational Memory Agent

**Date:** 2026-06-08
**Requested by:** user
**Skills used:** langgraph, python

## 1. Question
How to build a LangGraph agent that persists conversation history across
multiple turns, so users can refer back to earlier messages.

## 2. Approach
- Read `langgraph/instructions.md` for checkpointer and memory patterns.
- Read `langgraph/examples.md` for the chat-agent-with-memory example.
- Read `python/instructions.md` for code standards (type hints, dataclasses).
- Combined `MemorySaver` + `thread_id` pattern with `create_react_agent`.

## 3. Key Findings
- `MemorySaver` snapshots graph state after every step; same `thread_id` replays history.
- `create_react_agent` is the fastest way to wire an LLM with tools + memory.
- `stream_mode="values"` emits the full state after each node; extract `messages[-1]` for the reply.
- For production, replace `MemorySaver` (in-process) with `SqliteSaver` or `PostgresSaver`.
- Cross-thread (user-level) memory requires a `BaseStore` in addition to the checkpointer.

## 4. Answer
```python
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

model = init_chat_model("anthropic:claude-sonnet-4-6")
agent = create_react_agent(model, tools=[], checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "session-42"}}

def chat(message: str) -> str:
    result = agent.invoke(
        {"messages": [{"role": "user", "content": message}]}, config
    )
    return result["messages"][-1].content

print(chat("My name is Alex."))
print(chat("What is my name?"))   # agent correctly replies "Alex"
```

## 5. Sources / Tools Used
- Skill files: `langgraph/instructions.md`, `langgraph/examples.md`,
  `python/instructions.md`
- Model knowledge of LangGraph 0.3+ API.

## 6. Caveats & Next Steps
- `MemorySaver` state is lost on process restart — use `SqliteSaver` for durable sessions.
- The example has no tools; add them to the `tools=[]` list as needed.
- Next step: add a `BaseStore` for per-user facts that persist across different thread IDs.
```

---

## What Made This Report Good
- **Section 1** restates the question precisely — no ambiguity.
- **Section 3** contains only facts that appeared in the actual answer.
- **Section 4** includes the final working code, not an intermediate draft.
- **Section 6** honest caveats about `MemorySaver` limits.
- Total length: ~280 words + code — within the 150-400 word target.
