import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from schemas.v4_core import (
    Hypothesis, HypothesisStatus, 
    ValidationReport, PolicyEnvelope, EnvelopeStatus
)

logger = logging.getLogger("LifecycleRunner")
logger.setLevel(logging.INFO)

# ==========================================
# THRESHOLDS & CONFIGS
# ==========================================
EMERGING_MIN_SUPPORT = 0.5
ACTIVE_CHALLENGE_CONTRADICTION = 0.7
CHALLENGED_INVALIDATION_CONTRADICTION = 0.9
DECAYING_FRESHNESS_THRESHOLD = 0.3
MAX_DECAY_LIFETIME_SECONDS = 86400 * 7

class LifecycleRunner:
    """
    4.0 架构的心脏起搏器 (The Heartbeat of Architecture 4.0)
    负责对象生命周期的流转与权限级联剥夺。
    """
    
    def __init__(self):
        pass

    def evaluate_hypothesis_status(
        self, 
        hypothesis: Hypothesis, 
        latest_report: Optional[ValidationReport],
        current_time: datetime
    ) -> HypothesisStatus:
        """
        核心状态机流转逻辑。
        """
        current_status = hypothesis.status

        # -------------------------------------------------------------
        # 转移 1: EMERGING -> ACTIVE
        # -------------------------------------------------------------
        if current_status == HypothesisStatus.EMERGING:
            if latest_report:
                has_veto = any(latest_report.veto_flags.values())
                if not has_veto and latest_report.support_score >= EMERGING_MIN_SUPPORT and latest_report.contradiction_score < ACTIVE_CHALLENGE_CONTRADICTION:
                    return HypothesisStatus.ACTIVE
                elif has_veto or latest_report.contradiction_score >= ACTIVE_CHALLENGE_CONTRADICTION:
                     return HypothesisStatus.CHALLENGED
            return current_status

        # -------------------------------------------------------------
        # 转移 2: ACTIVE -> CHALLENGED
        # -------------------------------------------------------------
        if current_status == HypothesisStatus.ACTIVE:
            if latest_report:
                has_veto = any(latest_report.veto_flags.values())
                is_highly_contradicted = latest_report.contradiction_score >= ACTIVE_CHALLENGE_CONTRADICTION
                
                if has_veto or is_highly_contradicted:
                    return HypothesisStatus.CHALLENGED

        # -------------------------------------------------------------
        # 转移 3: ACTIVE -> DECAYING
        # -------------------------------------------------------------
        if current_status == HypothesisStatus.ACTIVE:
            if latest_report and latest_report.freshness_score < DECAYING_FRESHNESS_THRESHOLD:
                return HypothesisStatus.DECAYING

        # -------------------------------------------------------------
        # 转移 4: CHALLENGED -> INVALIDATED
        # -------------------------------------------------------------
        if current_status == HypothesisStatus.CHALLENGED:
            if latest_report and latest_report.contradiction_score >= CHALLENGED_INVALIDATION_CONTRADICTION:
                return HypothesisStatus.INVALIDATED

        # -------------------------------------------------------------
        # 转移 5: DECAYING -> ARCHIVED
        # -------------------------------------------------------------
        if current_status == HypothesisStatus.DECAYING:
            if hypothesis.superseded_by_hypothesis_id:
                return HypothesisStatus.ARCHIVED
            
            time_alive = (current_time - hypothesis.generated_at).total_seconds()
            if time_alive > MAX_DECAY_LIFETIME_SECONDS:
                return HypothesisStatus.ARCHIVED

        return current_status

    def process_cascade_rules(
        self, 
        hypothesis: Hypothesis, 
        new_status: HypothesisStatus,
        related_envelopes: List[PolicyEnvelope]
    ) -> List[PolicyEnvelope]:
        """
        处理向下级联规则 (Cascade Rules)。
        """
        updated_envelopes = []

        if new_status == HypothesisStatus.INVALIDATED:
            for env in related_envelopes:
                if env.status in [EnvelopeStatus.COMPILED, EnvelopeStatus.ADMITTED, EnvelopeStatus.PARTIALLY_EXECUTED]:
                    env.status = EnvelopeStatus.VETOED
                    updated_envelopes.append(env)

        if hypothesis.superseded_by_hypothesis_id:
            for env in related_envelopes:
                if env.status not in [EnvelopeStatus.SUPERSEDED, EnvelopeStatus.EXECUTED, EnvelopeStatus.EXPIRED]:
                    env.status = EnvelopeStatus.SUPERSEDED
                    updated_envelopes.append(env)

        return updated_envelopes

    def run_cycle(self, active_hypotheses: List[Hypothesis], report_store: Dict[str, ValidationReport], envelope_store: Dict[str, List[PolicyEnvelope]]) -> Dict[str, Any]:
        """
        模拟一次定时轮询任务，返回变更摘要
        """
        current_time = datetime.now(timezone.utc)
        
        result = {
            "updated_hypotheses": [],
            "updated_envelopes": [],
            "transitions": []
        }
        
        for hypothesis in active_hypotheses:
            latest_report = report_store.get(hypothesis.hypothesis_id)
            related_envs = envelope_store.get(hypothesis.hypothesis_id, [])

            new_status = self.evaluate_hypothesis_status(hypothesis, latest_report, current_time)

            if new_status != hypothesis.status:
                result["transitions"].append(f"{hypothesis.hypothesis_id}: {hypothesis.status.value} -> {new_status.value}")
                
                updated_envs = self.process_cascade_rules(hypothesis, new_status, related_envs)
                
                hypothesis.status = new_status
                result["updated_hypotheses"].append(hypothesis)
                result["updated_envelopes"].extend(updated_envs)
                
            # If no status change but it has a supersede pointer, still trigger cascade check
            elif hypothesis.superseded_by_hypothesis_id:
                updated_envs = self.process_cascade_rules(hypothesis, hypothesis.status, related_envs)
                if updated_envs:
                    result["updated_envelopes"].extend(updated_envs)

        return result
