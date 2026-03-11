from claims.claim_extractor import ClaimExtractor


def test_claim_extraction_basic():

    text = (
        "AI funding increased in 2024. "
        "Several startups raised over 100 million dollars."
    )

    extractor = ClaimExtractor()

    claims = extractor.extract_claims(text)

    assert len(claims) >= 2
    assert all(claim.text for claim in claims)
