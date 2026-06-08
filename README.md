# Deep Agent Chatbot

A Streamlit chatbot demonstrating every feature of the [deepagents](https://pypi.org/project/deepagents/) library — planning, context engineering, subagents, multiple storage backends, and on-demand skills — all in one conversational UI.

---

## Features

| Feature | What it does |
|---|---|
| **Planning** | Agent writes a `write_todos` checklist before multi-step work |
| **Context Engineering** | `config/AGENTS.md` rulebook + editable system prompt injected at startup |
| **Subagents** | Spawns an isolated research subagent (optional structured output via Pydantic) |
| **Backends** | Switch RAM / disk / store without changing agent code |
| **Skills** | Python, AWS, LangGraph, Report-Writer loaded on-demand to save tokens |
| **Web Search** | Tavily-powered search available to main agent and subagent |

---

## Project Structure

```
.
├── app.py              # Streamlit entry point (UI only)
├── core/
│   ├── agent.py        # Agent builder, subagents, skills hint
│   ├── backends.py     # StateBackend / FilesystemBackend / StoreBackend setup
│   └── tools.py        # Tavily web search tool
├── config/
│   └── AGENTS.md       # Agent rulebook loaded into context at startup
├── skills/
│   ├── aws/
│   ├── langgraph/
│   ├── python/
│   └── report-writer/
├── notebooks/
│   ├── 01_basic_deep_agent.ipynb
│   ├── 02_context_engineering.ipynb
│   ├── 03_backends.ipynb
│   └── 04_subagents.ipynb
├── .env.example
├── requirements.txt
└── pyproject.toml
```

---

## Quick Start

**1. Clone and install**
```bash
git clone https://github.com/your-username/deep-agents-demo.git
cd deep-agents-demo
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

**2. Add API keys**
```bash
cp .env.example .env
# edit .env and fill in your keys
```

**3. Run**
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

> Get keys at: [OpenAI](https://platform.openai.com) · [Groq](https://console.groq.com) · [Tavily](https://tavily.com)

---

## Backends Explained

| Backend | Analogy | Survives shutdown? | Cross-thread? |
|---|---|---|---|
| `StateBackend` | Sticky note in RAM | No | No |
| `FilesystemBackend` | File on your hard disk | Yes | Yes |
| `StoreBackend` | LangGraph store (DB) | With persistent store | Yes |

---

## Notebooks

Step-by-step walkthroughs in `notebooks/`:

1. `01_basic_deep_agent.ipynb` — create your first deep agent
2. `02_context_engineering.ipynb` — AGENTS.md, system prompts, MemorySaver
3. `03_backends.ipynb` — all three backends with live demos
4. `04_subagents.ipynb` — sync subagents and structured output

---

## Tech Stack

- [deepagents](https://pypi.org/project/deepagents/) — agent framework
- [LangGraph](https://github.com/langchain-ai/langgraph) — state machine backbone
- [LangChain](https://github.com/langchain-ai/langchain) — model/tool abstractions
- [Streamlit](https://streamlit.io) — UI
- [Tavily](https://tavily.com) — web search
- [Groq](https://groq.com) — fast inference for subagent
