"""Golden dataset loader tests."""

from app.eval.golden_loader import load_golden_dataset


def test_load_golden_dataset_has_50_plus_cases():
    cases = load_golden_dataset(client_id="demo-retail")
    assert len(cases) >= 50


def test_ci_subset_is_smaller():
    all_cases = load_golden_dataset(client_id="demo-retail")
    ci_cases = load_golden_dataset(client_id="demo-retail", subset="ci")
    assert 0 < len(ci_cases) < len(all_cases)
