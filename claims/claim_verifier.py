from typing import List
from claims.claim_model import Claim

from sentence_transformers import SentenceTransformer, util


class ClaimVerifier:

    def __init__(self, similarity_threshold: float = 0.45):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.similarity_threshold = similarity_threshold


    def verify_claims(self, claims: List[Claim], sources: List[str]) -> List[Claim]:
        """
        Updates each claim with verification results.
        """

        verified_claims: List[Claim] = []

        for claim in claims:
            supporting_sources, max_similarity = self._find_supporting_sources(claim.text, sources)

            claim.supporting_sources = supporting_sources
            claim.support_score = max_similarity
            claim.verified = max_similarity > self.similarity_threshold

            verified_claims.append(claim)

        return verified_claims


    def _is_supported(self, claim_text: str, sources: List[str]) -> bool:
        """
        Semantic verification using embedding similarity.
        """

        if not sources:
            return False

        claim_embedding = self.model.encode(
            claim_text,
            convert_to_tensor=True
        )

        source_embeddings = self.model.encode(
            sources,
            convert_to_tensor=True
        )

        similarities = util.cos_sim(claim_embedding, source_embeddings)

        max_similarity = similarities.max().item()

        return max_similarity > self.similarity_threshold

    def _find_supporting_sources(self, claim_text: str, sources: List[str]) -> tuple[List[str], float]:
        """
        Returns supporting sources and the max semantic similarity score.
        """

        if not sources:
            return [], 0.0

        claim_embedding = self.model.encode(
            claim_text,
            convert_to_tensor=True
        )

        source_embeddings = self.model.encode(
            sources,
            convert_to_tensor=True
        )

        similarities = util.cos_sim(claim_embedding, source_embeddings)

        supporting_sources = []
        max_similarity = 0.0

        for i, score in enumerate(similarities[0]):
            similarity = score.item()

            if similarity > max_similarity:
                max_similarity = similarity

            if similarity > self.similarity_threshold:
                supporting_sources.append(sources[i])

        return supporting_sources, max_similarity
