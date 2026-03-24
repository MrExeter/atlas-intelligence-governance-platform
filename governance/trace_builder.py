from datetime import datetime, UTC
import uuid

from models.execution_trace import ExecutionTrace, RetrievalStep, Source


def build_execution_trace(result: dict, query: str) -> ExecutionTrace:
    """
    Convert the research graph output into an ExecutionTrace
    used by the governance pipeline.
    """

    # ---------------------------
    # Build Sources
    # ---------------------------

    sources = []

    for doc in result.get("raw_documents", []):
        if not isinstance(doc, dict):
            continue

        url = doc.get("url")
        if not url:
            continue

        try:
            domain = url.split("/")[2]
        except IndexError:
            domain = ""

        sources.append(
            Source(
                url=url,
                domain=domain,
                title=doc.get("title"),
                content=doc.get("content"),
            )
        )

    # ---------------------------
    # Build Retrieval Steps
    # ---------------------------

    retrieval_steps = []

    chunks = result.get("retrieved_chunks", [])

    if chunks:
        retrieval_steps.append(
            RetrievalStep(
                query=query,
                returned_documents=len(chunks),
                selected_documents=len(chunks),
            )
        )

    domains = []

    for source in sources:
        domains.append(source.domain)


    # ---------------------------
    # Build Trace
    # ---------------------------

    # Concatenate all report fields so the claim extractor sees the full output
    text_parts = []

    for field in ("executive_summary", "market_overview"):
        value = result.get(field)
        if value:
            text_parts.append(value)

    for competitor in result.get("competitors") or []:
        if isinstance(competitor, dict) and competitor.get("summary"):
            text_parts.append(competitor["summary"])

    for item in (result.get("opportunities") or []) + (result.get("risks") or []):
        if isinstance(item, str):
            text_parts.append(item)

    final_output = " ".join(text_parts)

    trace = ExecutionTrace(
        run_id=str(uuid.uuid4()),
        timestamp=datetime.now(UTC),
        query=query,
        research_plan=None,
        retrieval_steps=retrieval_steps,
        sources=sources,
        reasoning_steps=[],
        final_output=final_output,
        domains=domains,
        unique_domain_count=len(set(domains)),
    )

    return trace
