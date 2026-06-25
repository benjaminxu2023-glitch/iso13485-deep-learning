from __future__ import annotations

import json
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator

from config.settings import PROVINCE_CONFIGS


class StudentProfile(BaseModel):
    province: str
    score: int
    rank: int
    subject_category: Optional[str] = None
    subjects: list[str]
    preferred_cities: list[str] = []
    preferred_majors: list[str] = []
    rejected_majors: list[str] = []
    budget_limit: Optional[int] = None
    accept_adjustment: bool = True
    accept_sino_foreign: bool = False
    risk_preference: str = "balanced"
    health_limits: Optional[str] = None
    career_direction: Optional[str] = None

    @field_validator("province")
    @classmethod
    def validate_province(cls, v: str) -> str:
        if v not in PROVINCE_CONFIGS:
            raise ValueError(f"不支持的省份: {v}，仅支持 zhejiang/jiangsu/shanghai")
        return v

    @field_validator("risk_preference")
    @classmethod
    def validate_risk_preference(cls, v: str) -> str:
        if v not in ("aggressive", "balanced", "conservative"):
            raise ValueError("风险偏好必须为 aggressive/balanced/conservative")
        return v

    @model_validator(mode="after")
    def validate_province_rules(self) -> StudentProfile:
        cfg = PROVINCE_CONFIGS[self.province]
        min_score, max_score = cfg["score_range"]
        if not (min_score <= self.score <= max_score):
            raise ValueError(f"{cfg['name']}分数范围为{min_score}-{max_score}")

        if self.province == "jiangsu":
            if not self.subject_category:
                raise ValueError("江苏考生必须选择首选科目（物理/历史）")
            if self.subject_category not in cfg["subject_categories"]:
                raise ValueError("首选科目必须为物理或历史")
            pool = cfg["subject_pool"]
            if len(self.subjects) != cfg["elective_count"]:
                raise ValueError(f"江苏考生需选择{cfg['elective_count']}门再选科目")
            for s in self.subjects:
                if s not in pool:
                    raise ValueError(f"再选科目 {s} 不在可选范围: {pool}")
        else:
            pool = cfg["subject_pool"]
            if len(self.subjects) != cfg["elective_count"]:
                raise ValueError(f"{cfg['name']}考生需选择{cfg['elective_count']}门选考科目")
            for s in self.subjects:
                if s not in pool:
                    raise ValueError(f"选考科目 {s} 不在可选范围: {pool}")
        return self

    def all_subjects(self) -> list[str]:
        base = ["语文", "数学", "英语"]
        if self.province == "jiangsu" and self.subject_category:
            return base + [self.subject_category] + self.subjects
        return base + self.subjects


class AdmissionRecord(BaseModel):
    id: Optional[int] = None
    province: str
    year: int
    university_name: str
    university_code: Optional[str] = None
    major_name: str
    major_code: Optional[str] = None
    major_group_code: Optional[str] = None
    batch: str = "普通类"
    plan_type: str = "major"
    enrollment_count: Optional[int] = None
    min_score: Optional[int] = None
    min_rank: Optional[int] = None
    avg_score: Optional[int] = None
    avg_rank: Optional[int] = None
    subject_requirements: list[str] = []
    subject_category: Optional[str] = None
    city: Optional[str] = None
    campus: Optional[str] = None
    tuition: Optional[int] = None
    remarks: Optional[str] = None

    @field_validator("subject_requirements", mode="before")
    @classmethod
    def parse_subjects(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v or []


class CurrentYearPlan(BaseModel):
    id: Optional[int] = None
    province: str
    year: int = 2025
    university_name: str
    university_code: Optional[str] = None
    major_name: str
    major_code: Optional[str] = None
    major_group_code: Optional[str] = None
    batch: str = "普通类"
    plan_type: str = "major"
    enrollment_count: Optional[int] = None
    subject_requirements: list[str] = []
    subject_category: Optional[str] = None
    tuition: Optional[int] = None
    city: Optional[str] = None
    campus: Optional[str] = None
    charter_special_conditions: Optional[str] = None
    remarks: Optional[str] = None

    @field_validator("subject_requirements", mode="before")
    @classmethod
    def parse_subjects(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v or []


class RiskItem(BaseModel):
    risk_type: str
    detail: str
    severity: str = "medium"

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        if v not in ("high", "medium", "low"):
            raise ValueError("severity 必须为 high/medium/low")
        return v


class RecommendationItem(BaseModel):
    university_name: str
    university_code: Optional[str] = None
    major_name: str
    major_code: Optional[str] = None
    major_group_code: Optional[str] = None
    city: Optional[str] = None
    campus: Optional[str] = None
    tuition: Optional[int] = None
    subject_requirements: list[str] = []
    historical_min_ranks: list[int] = []
    historical_min_scores: list[int] = []
    current_year_plan_count: Optional[int] = None
    tier: str = "match"
    risk_level: str = "medium"
    reason: str = ""
    manual_review_items: list[str] = []
    evidence: str = ""
    charter_risks: list[RiskItem] = []


class AuditResult(BaseModel):
    status: str
    issues: list[str] = []
    warnings: list[str] = []
    high_risks: list[str] = []

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in ("pass", "warning", "high_risk", "invalid"):
            raise ValueError("审核结果必须为 pass/warning/high_risk/invalid")
        return v


class StrategyPlan(BaseModel):
    strategy_type: str
    strategy_label: str
    recommendations: list[RecommendationItem] = []
    tier_distribution: dict[str, int] = {}
    overall_risk: str = ""
    summary: str = ""


class PipelineResult(BaseModel):
    student: StudentProfile
    strategies: list[StrategyPlan] = []
    audit_result: Optional[AuditResult] = None
    charter_risks: dict[str, list[RiskItem]] = {}
    all_recommendations: list[RecommendationItem] = []
