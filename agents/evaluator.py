from langchain_openai import ChatOpenAI
from agents.state import AgentState
import json
from datetime import datetime, UTC

from governance.token_utils import update_token_usage

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)

SYSTEM_PROMPT = """
You are a QA evaluator for market research reports.

Score the following fields from 0 to 1:

- executive_summary
- market_overview
- competitors
- opportunities
- risks

Also estimate hallucination_risk from 0 to 1.

Return STRICT JSON:

{
  "executive_summary": 0.0,
  "market_overview": 0.0,
  "competitors": 0.0,
  "opportunities": 0.0,
  "risks": 0.0,
  "hallucination_risk": 0.0
}
"""


def evaluator_node(state: AgentState) -> AgentState:
    payload = {
        "executive_summary": state.get("executive_summary"),
        "market_overview": state.get("market_overview"),
        "competitors": state.get("competitors"),
        "opportunities": state.get("opportunities"),
        "risks": state.get("risks"),
    }

    prompt = f"""
Evaluate this report:

{json.dumps(payload, indent=2)}
"""

    response = llm.invoke([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ])

    usage_update = update_token_usage(state, response)

    scores = json.loads(response.content)

    return {
        "eval_scores": scores,
        "completed_at": datetime.now(UTC),
        **usage_update
    }
