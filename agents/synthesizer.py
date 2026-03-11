from langchain_openai import ChatOpenAI
from agents.state import AgentState
import json

from governance.token_utils import update_token_usage

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

SYSTEM_PROMPT = """
You are a senior strategy consultant.

Using the provided context, generate an executive market brief with:

- executive_summary (string)
- market_overview (string)
- competitors (array of objects with name + summary)
- opportunities (array of strings)
- risks (array of strings)

Return STRICT JSON in this format:

{
  "executive_summary": "...",
  "market_overview": "...",
  "competitors": [{"name": "...", "summary": "..."}],
  "opportunities": ["..."],
  "risks": ["..."]
}
"""


def synthesizer_node(state: AgentState) -> AgentState:
    chunks = state.get("retrieved_chunks", [])
    topic = state.get("topic")

    context = "\n\n".join([d["content"] for d in chunks])

    prompt = f"""
Topic: {topic}

Context:
{context}

Generate executive brief.
"""

    response = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ])

    # Add token usage and cost monitoring
    usage_update = update_token_usage(state, response)

    parsed = json.loads(response.content)

    return {
        "executive_summary": parsed["executive_summary"],
        "market_overview": parsed["market_overview"],
        "competitors": parsed["competitors"],
        "opportunities": parsed["opportunities"],
        "risks": parsed["risks"],
        **usage_update
    }
