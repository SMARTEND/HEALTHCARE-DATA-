import pandas as pd
import pytest

from appointment_analytics import (
    AppointmentKPICalculator,
    export_appointment_summaries,
    normalize_appointment_data,
    normalize_status,
)


def _appointment_fixture():
    return pd.DataFrame(
        {
            "appointment_id": [1, 2, 3, 4],
            "patient_age": [30, 45, 60, 50],
            "department": ["Cardiology", "Pediatrics", "Cardiology", "Pediatrics"],
            "appointment_type": ["New", "Urgent", "Follow-up", "New"],
            "status": ["Completed", "No-Show", "Cancelled", "completed"],
            "sms_reminder_sent": [1, 0, 1, 1],
            "appointment_date": ["2025-01-01", "2025-01-15", "2025-02-01", "2025-02-15"],
            "service_duration_min": [30, 20, 25, 35],
            "completed_flag": [1, 0, 0, 1],
            "wait_time_min": [10, 20, 30, 40],
            "los_days": [1.0, 2.0, 1.5, 2.5],
            "referral_delay_days": [3, 5, 7, 9],
        }
    )


def test_normalize_status_handles_common_spellings():
    normalized = normalize_status(pd.Series(["No-Show", "no show", "Cancelled", "canceled"]))

    assert normalized.tolist() == ["no_show", "no_show", "cancelled", "cancelled"]


def test_appointment_kpis_count_no_show_and_cancelled_rates():
    kpis = AppointmentKPICalculator.summary_kpis(_appointment_fixture())

    assert kpis["total_appointments"] == 4
    assert kpis["completed_appointments"] == 2
    assert kpis["no_show_appointments"] == 1
    assert kpis["cancelled_appointments"] == 1
    assert kpis["completion_rate_pct"] == pytest.approx(50)
    assert kpis["no_show_rate_pct"] == pytest.approx(25)
    assert kpis["cancellation_rate_pct"] == pytest.approx(25)
    assert kpis["avg_wait_time_min"] == pytest.approx(25)
    assert kpis["appointment_start_date"] == "2025-01-01"
    assert kpis["appointment_end_date"] == "2025-02-15"


def test_department_and_monthly_summaries_are_grouped():
    department = AppointmentKPICalculator.department_summary(_appointment_fixture())
    monthly = AppointmentKPICalculator.monthly_summary(_appointment_fixture())

    cardiology = department.set_index("department").loc["Cardiology"]
    assert cardiology["appointments"] == 2
    assert cardiology["completion_rate_pct"] == pytest.approx(50)
    assert cardiology["no_show_rate_pct"] == pytest.approx(0)

    february = monthly.set_index("appointment_month").loc["2025-02"]
    assert february["appointments"] == 2
    assert february["cancellation_rate_pct"] == pytest.approx(50)


def test_export_appointment_summaries_writes_aggregate_files(tmp_path):
    outputs = export_appointment_summaries(_appointment_fixture(), tmp_path)

    assert set(outputs) == {"kpis", "status", "department", "monthly"}
    for path in outputs.values():
        assert path.exists()

    kpis = pd.read_csv(outputs["kpis"]).iloc[0]
    assert kpis["total_appointments"] == 4


def test_normalize_appointment_data_requires_core_columns():
    with pytest.raises(ValueError, match="Missing appointment columns"):
        normalize_appointment_data(pd.DataFrame({"appointment_id": [1]}))
