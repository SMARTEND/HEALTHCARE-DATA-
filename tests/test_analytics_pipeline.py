import pandas as pd
import pytest

from analytics import HealthcareDataLoader, KPICalculator
from etl_pipeline import DataTransformer, DataValidator
from generate_data import generate_sample_data


def test_generate_sample_data_is_deterministic_and_expanded():
    first = generate_sample_data(num_records=25, expanded=True)
    second = generate_sample_data(num_records=25, expanded=True)

    pd.testing.assert_frame_equal(first, second)
    assert len(first) == 25
    assert {
        "patient_id",
        "department",
        "visit_date",
        "wait_time_minutes",
        "los_minutes",
        "referral_delay_days",
        "total_cost",
        "patient_satisfaction",
        "delay_reason",
    }.issubset(first.columns)
    assert (first["wait_time_minutes"] >= 5).all()
    assert (first["los_minutes"] >= 30).all()
    assert (first["referral_delay_days"] >= 0).all()


def test_data_loader_reads_generated_patient_data(tmp_path):
    data_path = tmp_path / "patient_visits.csv"
    generated = generate_sample_data(num_records=10, output_path=data_path, expanded=False)

    loader = HealthcareDataLoader(data_dir=str(tmp_path))
    loaded = loader.load_patient_data()

    assert len(loaded) == len(generated)
    assert loaded["patient_id"].iloc[0] == "P00000"


def test_kpi_calculator_returns_expected_stats_and_rollups():
    df = pd.DataFrame(
        {
            "department": ["ED", "ED", "SURG"],
            "visit_date": ["2025-01-01", "2025-01-15", "2025-02-01"],
            "wait_time_minutes": [10, 20, 30],
            "los_minutes": [60, 120, 180],
        }
    )

    wait_stats = KPICalculator.calculate_wait_time_stats(df)
    los_stats = KPICalculator.calculate_los_stats(df)
    department = KPICalculator.department_performance(df, "wait_time_minutes")
    monthly = KPICalculator.monthly_trends(df, "wait_time_minutes")

    assert wait_stats["mean"] == pytest.approx(20)
    assert los_stats["q95"] == pytest.approx(174)
    assert department.loc["ED", "count"] == 2
    assert department.loc["SURG", "mean"] == pytest.approx(30)
    assert monthly.index.astype(str).tolist() == ["2025-01", "2025-02"]
    assert monthly.loc[pd.Period("2025-01", freq="M"), "count"] == 2


def test_data_validator_and_transformer_handle_quality_checks():
    df = pd.DataFrame(
        {
            "department": ["ED", "BAD", "ED"],
            "visit_date": ["2025-01-01", "2025-01-02", "2025-01-01"],
            "wait_time_minutes": [10, -5, None],
            "los_minutes": [60, 90, 60],
            "referral_delay_days": [1, 2, 1],
            "insurance_type": ["Private", "Medicare", "Private"],
        }
    )

    completeness = DataValidator.validate_completeness(df, ["department", "wait_time_minutes"])
    range_check = DataValidator.validate_ranges(df, "wait_time_minutes", min_val=0)
    category_check = DataValidator.validate_categories(
        df, "department", ["ED", "IM", "OBGYN", "OPD", "PED", "SURG"]
    )
    transformed = DataTransformer.add_calculated_fields(DataTransformer.clean_data(df))

    assert completeness["missing_by_column"]["wait_time_minutes"] == 1
    assert range_check["status"] == "FAIL"
    assert category_check["invalid_count"] == 1
    assert (transformed["wait_time_minutes"] >= 0).all()
    assert {"month", "quarter", "los_hours", "reimbursement_rate"}.issubset(transformed.columns)


def test_validate_completeness_handles_empty_dataframes():
    result = DataValidator.validate_completeness(
        pd.DataFrame(columns=["department"]), ["department"]
    )

    assert result["total_records"] == 0
    assert result["missing_by_column"] == {"department": 0}
    assert result["completeness_pct"] == 100.0
