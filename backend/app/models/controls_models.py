"""Runtime controls and feature flag models."""

from pydantic import BaseModel, Field


class RuntimeDefaults(BaseModel):
    local_llm_model: str = "llama3.2"
    cloud_routing_enabled: bool = False
    eval_sampling_rate: float = 0.05


class SensitivityControls(BaseModel):
    high_keywords: list[str] = Field(default_factory=list)
    default_decision: str = "local_only"


class RuntimeControlsSnapshot(BaseModel):
    defaults: RuntimeDefaults = Field(default_factory=RuntimeDefaults)
    sensitivity: SensitivityControls = Field(default_factory=SensitivityControls)
    feature_flags: dict[str, bool] = Field(default_factory=dict)
    kill_switches: dict[str, bool] = Field(default_factory=dict)
    rollout: dict[str, dict[str, bool]] = Field(default_factory=dict)
    source_path: str | None = None


class RuntimeControlsUpdate(BaseModel):
    feature_flags: dict[str, bool] | None = None
    kill_switches: dict[str, bool] | None = None
    defaults: RuntimeDefaults | None = None
    rollout: dict[str, dict[str, bool]] | None = None
