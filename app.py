from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from core.agent import SKILLS_ROOT, build_agent
from core.backends import load_agents_md

# ── Constants ────────────────────────────────────────────────────────────────
APP_TITLE = "Deep Agent Chatbot"
APP_ICON = "🤖"
DEFAULT_SYSTEM_PROMPT = (
    "You are a deep-agent assistant. Plan before multi-step work, "
    "offload bulky results into files, and delegate independent research "
    "to subagents when it improves quality."
)
MODELS = [
    "openai:gpt-4o-mini",
    "openai:gpt-4o",
    "groq:qwen/qwen3-32b",
    "openai:gpt-5.4",
    "openai:gpt-5.5",
]
BACKENDS = ["StateBackend", "FilesystemBackend", "StoreBackend"]
BACKEND_DESCRIPTIONS = {
    "StateBackend":      "RAM only — fast, lost on shutdown (like a sticky note)",
    "FilesystemBackend": "Real disk — survives restarts (like a file on your drive)",
    "StoreBackend":      "LangGraph store — cross-thread memory (like a database)",
}


# ── Helpers ──────────────────────────────────────────────────────────────────
def message_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text") or item.get("content")
                if text:
                    parts.append(str(text))
            elif item is not None:
                parts.append(str(item))
        return "\n\n".join(parts)
    return str(content) if content is not None else ""


def pretty_json(value: Any) -> str:
    try:
        return json.dumps(value, indent=2, ensure_ascii=False, default=str)
    except TypeError:
        return str(value)


# ── Cached agent builder (rebuilds only when config changes) ─────────────────
@st.cache_resource(show_spinner=False)
def get_cached_agent(
    model: str,
    backend_name: str,
    workspace_root: str,
    system_prompt: str,
    enable_web_search: bool,
    enable_subagents: bool,
    use_structured_output: bool,
    subagent_model: str,
) -> tuple[Any, str]:
    return build_agent(
        model=model,
        backend_name=backend_name,
        workspace_root=workspace_root,
        system_prompt=system_prompt,
        enable_web_search=enable_web_search,
        enable_subagents=enable_subagents,
        use_structured_output=use_structured_output,
        subagent_model=subagent_model,
    )


# ── Session state ────────────────────────────────────────────────────────────
def init_state() -> None:
    st.session_state.setdefault(
        "messages",
        [{"role": "assistant", "content": "Ask me to plan, research, write files, or delegate work to a subagent."}],
    )
    st.session_state.setdefault("last_result", None)
    st.session_state.setdefault("thread_id", "main-thread")


# ── Sidebar ──────────────────────────────────────────────────────────────────
def render_sidebar(agents_md: str) -> dict[str, Any]:
    with st.sidebar:
        st.title("⚙️ Configuration")

        model = st.selectbox("Model", MODELS, index=0)
        backend_name = st.selectbox("Memory Backend", BACKENDS, index=0)
        st.caption(BACKEND_DESCRIPTIONS[backend_name])

        st.divider()
        st.subheader("Features")
        enable_web_search = st.toggle("Web Search (Tavily)", value=True)
        enable_subagents = st.toggle("Research Subagent", value=True)
        use_structured_output = st.toggle("Structured Subagent Output", value=False)
        subagent_model = st.text_input("Subagent Model", value="groq:qwen/qwen3-32b")
        thread_id = st.text_input("Thread ID", value=st.session_state.thread_id)
        system_prompt = st.text_area("System Prompt", value=DEFAULT_SYSTEM_PROMPT, height=130)

        st.divider()
        st.subheader("🧠 AGENTS.md")
        with st.expander("View rulebook", expanded=False):
            st.markdown(agents_md or "_No AGENTS.md found._")

        st.divider()
        st.subheader("📚 Skills")
        if SKILLS_ROOT.exists():
            for skill_dir in sorted(SKILLS_ROOT.iterdir()):
                if skill_dir.is_dir():
                    skill_md = skill_dir / "SKILL.md"
                    with st.expander(f"`{skill_dir.name}`"):
                        st.markdown(
                            skill_md.read_text(encoding="utf-8")
                            if skill_md.exists()
                            else "_SKILL.md not found_"
                        )
        else:
            st.caption("skills/ folder not found.")

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 New Thread", use_container_width=True):
                st.session_state.thread_id = str(uuid.uuid4())[:8]
                st.session_state.messages = [
                    {"role": "assistant", "content": "New thread started. Ask me anything."}
                ]
                st.session_state.last_result = None
                st.rerun()
        with col2:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = [
                    {"role": "assistant", "content": "Chat cleared."}
                ]
                st.rerun()

    return {
        "model": model,
        "backend_name": backend_name,
        "enable_web_search": enable_web_search,
        "enable_subagents": enable_subagents,
        "use_structured_output": use_structured_output,
        "subagent_model": subagent_model,
        "thread_id": thread_id,
        "system_prompt": system_prompt,
    }


# ── Feature cards ─────────────────────────────────────────────────────────────
def render_feature_cards() -> None:
    cols = st.columns(5)
    cards = [
        ("📋 Planning",            "Agent writes a todo list before multi-step work."),
        ("🧠 Context Engineering", "AGENTS.md + system prompt loaded into agent context."),
        ("🤖 Subagents",           "Isolated research subagent with optional structured output."),
        ("💾 Backends",            "Switch RAM / disk / database — same code, different durability."),
        ("📚 Skills",              "Python, AWS, LangGraph, Report-Writer loaded on-demand."),
    ]
    for col, (title, desc) in zip(cols, cards):
        with col:
            st.markdown(f"**{title}**")
            st.caption(desc)


# ── Chat ──────────────────────────────────────────────────────────────────────
def render_chat(agent: Any, thread_id: str) -> None:
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(message_text(msg["content"]))
            if (
                i == len(st.session_state.messages) - 1
                and msg["role"] == "assistant"
                and st.session_state.last_result
            ):
                with st.expander("Agent trace", expanded=False):
                    for m in st.session_state.last_result.get("messages", []):
                        role = getattr(m, "type", m.__class__.__name__)
                        st.markdown(f"**{role}**")
                        st.write(message_text(getattr(m, "content", m)))

    prompt = st.chat_input("Ask the deep agent to plan, research, write files, or use subagents…")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Agent thinking…"):
            result = agent.invoke(
                {"messages": [{"role": "user", "content": prompt}]},
                config={"configurable": {"thread_id": thread_id}},
            )

        last = result.get("messages", [{}])[-1]
        reply = message_text(getattr(last, "content", ""))
        st.markdown(reply)

        if result.get("files"):
            with st.expander("📁 Files written by the agent", expanded=True):
                for path, data in result["files"].items():
                    st.markdown(f"**`{path}`**")
                    text = data.get("content", str(data)) if isinstance(data, dict) else str(data)
                    st.code(text)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.last_result = result
        st.session_state.thread_id = thread_id


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")
    init_state()

    agents_md = load_agents_md()
    settings = render_sidebar(agents_md)

    st.title(f"{APP_ICON} {APP_TITLE}")
    st.caption(
        f"**Backend:** `{settings['backend_name']}` &nbsp;|&nbsp; "
        f"**Model:** `{settings['model']}` &nbsp;|&nbsp; "
        f"**Thread:** `{settings['thread_id']}`"
    )

    render_feature_cards()
    st.divider()

    with st.spinner("Building agent…"):
        agent, search_status = get_cached_agent(
            model=settings["model"],
            backend_name=settings["backend_name"],
            workspace_root=str(Path.cwd()),
            system_prompt=settings["system_prompt"],
            enable_web_search=settings["enable_web_search"],
            enable_subagents=settings["enable_subagents"],
            use_structured_output=settings["use_structured_output"],
            subagent_model=settings["subagent_model"],
        )

    st.info(search_status, icon="🔍")
    render_chat(agent, settings["thread_id"])


if __name__ == "__main__":
    main()
