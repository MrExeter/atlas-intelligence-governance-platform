from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.planner import planner_node
from agents.research.news import news_node
from agents.research.funding import funding_node
from agents.research.hiring import hiring_node
from agents.research.competitors import competitors_node
from agents.synthesizer import synthesizer_node
from agents.evaluator import evaluator_node
from rag.retriever import rag_node


def build_graph():
    builder = StateGraph(AgentState)

    # Core nodes
    builder.add_node("planner", planner_node)

    builder.add_node("news", news_node)
    builder.add_node("funding", funding_node)
    builder.add_node("hiring", hiring_node)
    builder.add_node("competitors", competitors_node)

    builder.add_node("rag", rag_node)
    builder.add_node("synthesizer", synthesizer_node)
    builder.add_node("evaluator", evaluator_node)

    # Entry
    builder.set_entry_point("planner")

    # Fan-out after planning
    builder.add_edge("planner", "news")
    builder.add_edge("planner", "funding")
    builder.add_edge("planner", "hiring")
    builder.add_edge("planner", "competitors")

    # Fan-in to RAG
    builder.add_edge("news", "rag")
    builder.add_edge("funding", "rag")
    builder.add_edge("hiring", "rag")
    builder.add_edge("competitors", "rag")

    # Final pipeline
    builder.add_edge("rag", "synthesizer")
    builder.add_edge("synthesizer", "evaluator")
    builder.add_edge("evaluator", END)

    return builder.compile()
