"""Evaluation result models."""

from pydantic import BaseModel, Field


class EvalScore(BaseModel):
    name: str
    passed: bool
    score: float
    details: str = ""


class GoldenCaseResult(BaseModel):
    case_id: str
    question: str
    passed: bool
    factual_accuracy: EvalScore
    groundedness: EvalScore
    abstention_correct: EvalScore
    format_valid: EvalScore
    failure_modes: list[str] = Field(default_factory=list)


class GoldenEvalReport(BaseModel):
    client_id: str
    total_cases: int
    passed_cases: int
    factual_accuracy_rate: float
    groundedness_rate: float
    abstention_correct_rate: float
    format_valid_rate: float
    meets_thresholds: bool
    cases: list[GoldenCaseResult] = Field(default_factory=list)


class EvalRunRequest(BaseModel):
    client_id: str = "demo-retail"
    subset: str | None = None  # "ci" for compressed subset


class AuthTokenRequest(BaseModel):
    client_id: str = "demo-retail"
    role: str = "manager"
    user_id: str = "dev-user"


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    client_id: str
    role: str
