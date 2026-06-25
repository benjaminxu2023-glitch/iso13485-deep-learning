from __future__ import annotations

from abc import ABC, abstractmethod

from db.models import StudentProfile, CurrentYearPlan, AdmissionRecord


class EligibilityResult:
    def __init__(self, eligible: bool, reason: str = ""):
        self.eligible = eligible
        self.reason = reason


class BaseRuleEngine(ABC):

    @abstractmethod
    def get_province(self) -> str:
        ...

    @abstractmethod
    def get_max_applications(self) -> int:
        ...

    @abstractmethod
    def get_application_unit(self) -> str:
        ...

    @abstractmethod
    def validate_subjects(self, student: StudentProfile) -> bool:
        ...

    @abstractmethod
    def check_subject_match(self, student: StudentProfile, plan: CurrentYearPlan) -> EligibilityResult:
        ...

    @abstractmethod
    def check_eligibility(self, student: StudentProfile, plan: CurrentYearPlan) -> EligibilityResult:
        ...

    @abstractmethod
    def validate_application_count(self, count: int) -> bool:
        ...

    @abstractmethod
    def check_gradient(self, tier_counts: dict[str, int]) -> list[str]:
        ...
