from enum import Enum
from typing import List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field

# ==========================================
# 1. LIFECYCLE ENUMS (生命周期枚举)
# ==========================================

class EventStatus(str, Enum):
    EMERGING = "emerging"
    ACTIVE = "active"
    DECAYING = "decaying"
    RESOLVED = "resolved"

class HypothesisStatus(str, Enum):
    EMERGING = "emerging"       # 刚提出，等待初步 Validation
    ACTIVE = "active"           # 已激活，允许驱动 Intent
    CHALLENGED = "challenged"   # 正在被 Validation 质询或被 CounterHypothesis 强力压制
    DECAYING = "decaying"       # 随着时间或数据变弱
    INVALIDATED = "invalidated" # 触碰失效条件，被硬杀
    ARCHIVED = "archived"       # 历史归档

class EnvelopeStatus(str, Enum):
    COMPILED = "compiled"             # 刚由 Policy Compiler 生成，尚未提交
    ADMITTED = "admitted"             # Constitution 裁决通过，允许执行
    PARTIALLY_EXECUTED = "partially_executed" # 正在执行层运作
    EXECUTED = "executed"             # 执行完毕
    EXPIRED = "expired"               # 超过 TTL 未执行完
    SUPERSEDED = "superseded"         # 被更高版本的 Envelope 覆盖
    VETOED = "vetoed"                 # 被 Constitution 否决

# ==========================================
# 2. CORE SCHEMA BASE CLASSES (核心对象)
# ==========================================

class EvidenceRecord(BaseModel):
    """
    原始证据标准对象。所有高层对象都必须可追溯到它。
    """
    evidence_id: str
    source: str
    modality: Literal["text", "timeseries", "event", "market_state", "execution_state", "research_note", "onchain", "derivatives"]
    observed_time: datetime
    effective_time: datetime
    ingest_time: datetime
    ttl_seconds: int
    reliability_prior: float
    entity_tags: List[str]
    overlap_group_hint: Optional[str] = None
    lineage_id: str
    payload_hash: str
    raw_uri: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    raw_payload: dict

class InvalidationCondition(BaseModel):
    condition_id: str
    description: str
    expected_validator: Optional[str] = Field(None, description="由哪个 validator 负责质询此条件")
    deadline: Optional[datetime] = None

class CausalStep(BaseModel):
    step: int
    statement: str
    supporting_claim_ids: List[str] = []
    supporting_event_ids: List[str] = []

class Hypothesis(BaseModel):
    """
    Cognition Plane: 核心主假设。必须包含明确的因果链和失效条件。
    """
    hypothesis_id: str
    status: HypothesisStatus = HypothesisStatus.EMERGING
    thesis_text: str
    thesis_summary: str
    horizon: Literal["h24", "d7", "d30"]
    bias: Literal["long", "short", "neutral", "mixed"]
    regime_context: Optional[str] = None
    
    causal_chain: List[CausalStep]
    primary_mechanism_tags: List[str]
    
    supporting_evidence_refs: List[str]
    counter_evidence_refs: List[str]
    missing_evidence_refs: List[str]  # 极其重要：承认“我还需要什么证据”
    overlap_groups_touched: List[str] # 用于计算 Echo Risk
    
    evidence_diversity_score: float
    echo_risk_score: float
    fragility: Literal["low", "medium", "high"]
    reflexivity_risk: Literal["low", "medium", "high"]
    
    invalidation_conditions: List[InvalidationCondition]
    ambiguity_notes: List[str]
    confidence_expression: Literal["weak", "moderate", "strong"]
    
    generated_by: str
    generated_at: datetime
    parent_hypothesis_id: Optional[str] = None
    superseded_by_hypothesis_id: Optional[str] = None


class CounterHypothesis(BaseModel):
    """
    Cognition Plane: 真实的对手盘。必须具备“如果...我就能赢”的条件。
    """
    counter_hypothesis_id: str
    primary_hypothesis_id: str
    thesis_text: str
    thesis_summary: str
    horizon: Literal["h24", "d7", "d30"]
    bias: Literal["long", "short", "neutral", "mixed"]
    
    strongest_conflict_points: List[str]
    supporting_evidence_refs: List[str]
    missing_evidence_refs: List[str]
    what_would_make_this_dominate: List[str] # 翻盘条件
    
    confidence_expression: Literal["weak", "moderate", "strong"]
    generated_by: str
    generated_at: datetime


class ActionIntent(BaseModel):
    """
    Cognition Plane: 认知层给出的策略意图（无精确定量，只有定性区间）。
    """
    intent_id: str
    hypothesis_id: str
    primary_bias: Literal["long", "short", "neutral"]
    aggression: Literal["low", "medium", "high"]
    conviction_style: Literal["tentative", "moderate", "strong"]
    hold_profile: Literal["tactical", "swing", "structural"]
    fragility: Literal["low", "medium", "high"]
    hedge_preference: Literal["none", "partial", "strong"]
    
    expected_confirmation_window: Literal["immediate", "short", "medium"]
    required_confirmations: List[str]
    invalidation_triggers: List[str]
    action_notes: List[str]
    
    expires_at: Optional[datetime] = None
    generated_at: datetime


class ValidationReport(BaseModel):
    """
    Validation Plane: 数据现实审查报告。天然偏向负面挑错。
    """
    validation_id: str
    hypothesis_id: str
    intent_id: Optional[str] = None
    
    # Validator 家族质询结果
    validator_family_scores: dict = Field(
        default_factory=lambda: {
            "macro_structure": None,
            "derivatives_structure": None,
            "spot_confirmation": None,
            "liquidity_conversion": None,
            "event_followthrough": None,
            "execution_context": None
        }
    )
    
    support_score: float
    contradiction_score: float     # 越高说明反驳越强烈
    alignment_score: float
    freshness_score: float
    redundancy_score: float        # 越高说明 Echo Risk 越大
    
    calibration_class: Literal[
        "historically_robust", 
        "moderate", 
        "fragile_breakout_pattern", 
        "event_only_pattern", 
        "low_repeatability", 
        "unknown"
    ]
    validator_notes: List[str]
    
    # 质询层的一票否决权
    veto_flags: dict = Field(
        default_factory=lambda: {
            "stale_critical_data": False,
            "semantic_numeric_conflict": False, # LLM看多但数据看空
            "missing_core_confirmation": False,
            "excessive_echo_risk": False,
            "historical_low_repeatability": False
        }
    )
    
    generated_at: datetime
    valid_until: datetime


class CompilerMode(str, Enum):
    STRUCTURAL_ALLOWED = "structural_allowed"
    TACTICAL_ONLY = "tactical_only"
    FROZEN = "frozen"

class ExposureBand(BaseModel):
    lower: float
    upper: float

class DecayProfile(BaseModel):
    mode: Literal["fast", "medium", "slow"]
    ttl_seconds: int

class PolicyEnvelope(BaseModel):
    """
    Policy Compiler: 将认知、质询和宪法规则编译为受限操作包络。消除伪精确。
    """
    envelope_id: str
    status: EnvelopeStatus = EnvelopeStatus.COMPILED
    
    # 溯源引用链
    hypothesis_id: str
    intent_id: str
    validation_id: str
    constitution_decision_id: str # 必须先有宪法法院判决
    
    allowed_direction: Literal["long", "short", "neutral"]
    max_exposure: float
    min_exposure: float
    target_exposure_band: ExposureBand
    compiler_mode: CompilerMode = CompilerMode.STRUCTURAL_ALLOWED
    
    hedge_requirement: dict = Field(
        default_factory=lambda: {
            "required": False,
            "min_hedge_ratio": None
        }
    )
    
    aggression_cap: Literal["low", "medium", "high"]
    decay_profile: DecayProfile
    revalidation_deadline: Optional[datetime] = None
    invalidation_triggers: List[str]
    execution_urgency: Literal["low", "medium", "high"]
    
    policy_notes: List[str]
    compiled_at: datetime
    superseded_by_envelope_id: Optional[str] = None
