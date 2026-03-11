import uuid
from typing import List

from claims.claim_model import Claim, ClaimType


class ClaimExtractor:
    """
    Extracts structured claims from a research report.
    """

    def extract_claims(self, report_text: str) -> List[Claim]:
        """
        Basic extraction strategy.
        For now we split the report into candidate statements.
        Later this can be replaced with an LLM extraction pipeline.
        """

        claims: List[Claim] = []

        # naive sentence split (safe placeholder)
        sentences = [s.strip() for s in report_text.split(".") if s.strip()]

        for sentence in sentences:

            claim = Claim(
                claim_id=str(uuid.uuid4()),
                text=sentence,
                claim_type=self._infer_claim_type(sentence),
                supporting_sources=None,
                verified=None,
            )

            claims.append(claim)

        return claims

    def _infer_claim_type(self, sentence: str) -> ClaimType:
        """
        Very simple heuristics for claim type.
        Can be replaced later with LLM classification.
        """

        if any(char.isdigit() for char in sentence):
            return ClaimType.STATISTIC

        if "predict" in sentence.lower() or "expected" in sentence.lower():
            return ClaimType.PREDICTION

        if "suggests" in sentence.lower() or "indicates" in sentence.lower():
            return ClaimType.INFERENCE

        return ClaimType.FACT
