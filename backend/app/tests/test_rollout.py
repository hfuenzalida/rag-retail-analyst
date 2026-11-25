"""Role-based progressive rollout tests."""

from app.core.rollout import get_rollout_matrix, is_feature_available_for_role, rollout_summary


def test_manager_blocked_from_cloud_routing():
    assert is_feature_available_for_role("cloud_routing", "manager") is False
    assert is_feature_available_for_role("cloud_routing", "analyst") is True


def test_manager_gets_recommendations():
    assert is_feature_available_for_role("recommendation_engine", "manager") is True


def test_manager_blocked_from_deep_dive():
    assert is_feature_available_for_role("deep_dive_mode", "manager") is False
    assert is_feature_available_for_role("deep_dive_mode", "analyst") is True


def test_rollout_matrix_includes_all_features():
    matrix = get_rollout_matrix()
    assert "cloud_routing" in matrix
    assert "driver_analysis" in matrix


def test_rollout_summary_structure():
    summary = rollout_summary()
    assert summary["environment"]
    assert "matrix" in summary
    assert len(summary["stages"]) >= 3
