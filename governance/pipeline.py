from typing import List

from claims.claim_extractor import ClaimExtractor
from claims.claim_verifier import ClaimVerifier
from governance.evaluation_engine import EvaluationEngine
from governance.policy_engine import PolicyEngine
from governance.reliability_metrics import ReliabilityMetrics
from models.execution_trace import ExecutionTrace
from models.policy_decision import PolicyDecision
from models.run_metrics import RunMetrics


class GovernancePipeline:
    """
    Orchestrates the full governance evaluation pipeline.
    """

    def __init__(self):
        self.claim_extractor = ClaimExtractor()
        self.claim_verifier = ClaimVerifier()
        self.evaluation_engine = EvaluationEngine()
        self.policy_engine = PolicyEngine()
        self.metrics_engine = ReliabilityMetrics()

    def run(self, trace: ExecutionTrace) -> tuple[PolicyDecision, RunMetrics]:

        # 1. Extract claims from final report
        claims = self.claim_extractor.extract_claims(trace.final_output)

        # 2. Prepare source texts (simple version: use URLs or summaries)
        source_texts: List[str] = [s.url for s in trace.sources]

        # 3. Verify claims against sources
        verified_claims = self.claim_verifier.verify_claims(claims, source_texts)

        # 4. Evaluate run
        evaluation = self.evaluation_engine.evaluate(
            run_id=trace.run_id,
            claims=verified_claims,
            sources=source_texts,
        )

        # 5. Apply governance policy
        policy_decision = self.policy_engine.evaluate_policy(evaluation)

        # 6. Generate reliability metrics
        metrics = self.metrics_engine.generate_metrics(
            evaluation=evaluation,
            policy=policy_decision,
            claims=verified_claims,
            sources=source_texts,
        )

        return policy_decision, metrics
