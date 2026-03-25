from typing import Dict
from datetime import datetime, timezone
from uuid import uuid4

from langchain_openai import ChatOpenAI
from agents.state import AgentState, ResearchTask

from usage import get_tracker

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)


SYSTEM_PROMPT = """
You are a senior market research analyst.

Given a topic, decompose it into research tasks covering:

- Market overview
- Key competitors
- Recent funding activity
- Hiring trends

Return a JSON array with objects:

{
  "type": "market|competitors|funding|hiring",
  "query": "search query"
}
"""


def planner_node(state: AgentState) -> AgentState:
    topic = state["topic"]

    prompt = f"""
Topic: {topic}

Generate research tasks.
"""

    response = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ])

    usage = response.response_metadata.get("token_usage", {})
    get_tracker(state.get("run_id", "")).record_llm_call(
        provider="openai",
        model="gpt-4o-mini",
        input_tokens=usage.get("prompt_tokens", 0),
        output_tokens=usage.get("completion_tokens", 0),
    )

    raw = response.content.strip()

    if not raw:
        raise RuntimeError("Planner returned empty response")

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        raw = raw.replace("json", "", 1).strip()

    import json
    parsed = json.loads(raw)

    tasks: list[ResearchTask] = []

    for item in parsed:
        tasks.append({
            "id": str(uuid4()),
            "type": item["type"],
            "query": item["query"],
            "status": "pending"
        })

    return {
        "tasks": tasks,
        "started_at": datetime.now(timezone.utc),
    }
