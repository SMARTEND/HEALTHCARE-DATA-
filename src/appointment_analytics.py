"""
Appointment analytics utilities for healthcare scheduling data.
"""

from pathlib import Path
from typing import Dict, Iterable, Optional

import pandas as pd


APPOINTMENT_REQUIRED_COLUMNS = {
    "appointment_id",
    "patient_age",
    "department",
    "appointment_type",
    "status",
    "sms_reminder_sent",
    "appointment_date",
    "service_duration_min",
    "completed_flag",
    "wait_time_min",
    "los_days",
    "referral_delay_days",
}


NUMERIC_COLUMNS = [
    "patient_age",
    "sms_reminder_sent",
    "service_duration_min",
    "completed_flag",
    "wait_time_min",
    "los_days",
    "referral_delay_days",
]


class AppointmentDataLoader:
    """Load and normalize healthcare appointment data from Excel or CSV."""

    def __init__(self, source_path: str, sheet_name: Optional[str] = None):
        self.source_path = Path(source_path)
        self.sheet_name = sheet_name

    def load(self) -> pd.DataFrame:
        """Load the configured appointment source."""
        if not self.source_path.exists():
            raise FileNotFoundError(f"Appointment source not found: {self.source_path}")

        suffix = self.source_path.suffix.lower()
        if suffix in {".xlsx", ".xls"}:
            df = pd.read_excel(self.source_path, sheet_name=self.sheet_name or 0)
        elif suffix == ".csv":
            df = pd.read_csv(self.source_path)
        else:
            raise ValueError(f"Unsupported appointment source format: {suffix}")

        return normalize_appointment_data(df)


def normalize_appointment_data(df: pd.DataFrame) -> pd.DataFrame:
    """Return an analytics-ready appointment dataframe."""
    df = df.copy()
    df.columns = [_normalize_column_name(col) for col in df.columns]
    validate_appointment_columns(df.columns)

    df["appointment_date"] = pd.to_datetime(df["appointment_date"], errors="coerce")
    if "arrival_time" in df.columns:
        df["arrival_time"] = pd.to_datetime(df["arrival_time"], errors="coerce")

    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df["status_category"] = normalize_status(df["status"])
    df["appointment_month"] = df["appointment_date"].dt.to_period("M").astype(str)
    return df


def validate_appointment_columns(columns: Iterable[str]) -> None:
    """Ensure the appointment source contains the expected analytic fields."""
    missing = sorted(APPOINTMENT_REQUIRED_COLUMNS.difference(set(columns)))
    if missing:
        raise ValueError(f"Missing appointment columns: {', '.join(missing)}")


def normalize_status(status: pd.Series) -> pd.Series:
    """Normalize common appointment status spellings for reliable KPI logic."""
    normalized = (
        status.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"[\s_]+", "-", regex=True)
    )
    return normalized.replace(
        {
            "completed": "completed",
            "complete": "completed",
            "cancelled": "cancelled",
            "canceled": "cancelled",
            "no-show": "no_show",
            "noshow": "no_show",
        }
    )


class AppointmentKPICalculator:
    """Calculate appointment-level scheduling KPIs and grouped summaries."""

    @staticmethod
    def summary_kpis(df: pd.DataFrame) -> Dict:
        """Calculate portfolio-level appointment KPIs."""
        df = normalize_appointment_data(df)
        total = len(df)
        status = df["status_category"]

        completed = int(status.eq("completed").sum())
        no_show = int(status.eq("no_show").sum())
        cancelled = int(status.eq("cancelled").sum())

        return {
            "total_appointments": total,
            "completed_appointments": completed,
            "no_show_appointments": no_show,
            "cancelled_appointments": cancelled,
            "completion_rate_pct": _pct(completed, total),
            "no_show_rate_pct": _pct(no_show, total),
            "cancellation_rate_pct": _pct(cancelled, total),
            "sms_reminder_rate_pct": round(df["sms_reminder_sent"].mean() * 100, 2),
            "avg_patient_age": round(df["patient_age"].mean(), 2),
            "avg_wait_time_min": round(df["wait_time_min"].mean(), 2),
            "avg_service_duration_min": round(df["service_duration_min"].mean(), 2),
            "avg_los_days": round(df["los_days"].mean(), 2),
            "avg_referral_delay_days": round(df["referral_delay_days"].mean(), 2),
            "appointment_start_date": _date_or_none(df["appointment_date"].min()),
            "appointment_end_date": _date_or_none(df["appointment_date"].max()),
        }

    @staticmethod
    def status_summary(df: pd.DataFrame) -> pd.DataFrame:
        """Count appointment outcomes by status."""
        df = normalize_appointment_data(df)
        total = len(df)

        summary = (
            df.groupby(["status_category", "status"], dropna=False)
            .size()
            .reset_index(name="appointments")
            .sort_values("appointments", ascending=False)
        )
        summary["appointment_pct"] = summary["appointments"].apply(lambda value: _pct(value, total))
        return summary.reset_index(drop=True)

    @staticmethod
    def department_summary(df: pd.DataFrame) -> pd.DataFrame:
        """Summarize scheduling performance by department."""
        df = normalize_appointment_data(df)
        grouped = df.groupby("department", dropna=False)
        summary = grouped.agg(
            appointments=("appointment_id", "count"),
            completed=("status_category", lambda values: int(values.eq("completed").sum())),
            no_show=("status_category", lambda values: int(values.eq("no_show").sum())),
            cancelled=("status_category", lambda values: int(values.eq("cancelled").sum())),
            avg_patient_age=("patient_age", "mean"),
            avg_wait_time_min=("wait_time_min", "mean"),
            avg_service_duration_min=("service_duration_min", "mean"),
            avg_los_days=("los_days", "mean"),
            avg_referral_delay_days=("referral_delay_days", "mean"),
            sms_reminder_rate_pct=("sms_reminder_sent", lambda values: values.mean() * 100),
        )

        summary["completion_rate_pct"] = summary.apply(
            lambda row: _pct(row["completed"], row["appointments"]), axis=1
        )
        summary["no_show_rate_pct"] = summary.apply(
            lambda row: _pct(row["no_show"], row["appointments"]), axis=1
        )
        summary["cancellation_rate_pct"] = summary.apply(
            lambda row: _pct(row["cancelled"], row["appointments"]), axis=1
        )

        return _round_summary(summary.reset_index())

    @staticmethod
    def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
        """Summarize appointment scheduling performance by month."""
        df = normalize_appointment_data(df)
        grouped = df.groupby("appointment_month", dropna=False)
        summary = grouped.agg(
            appointments=("appointment_id", "count"),
            completed=("status_category", lambda values: int(values.eq("completed").sum())),
            no_show=("status_category", lambda values: int(values.eq("no_show").sum())),
            cancelled=("status_category", lambda values: int(values.eq("cancelled").sum())),
            avg_wait_time_min=("wait_time_min", "mean"),
            avg_service_duration_min=("service_duration_min", "mean"),
            avg_referral_delay_days=("referral_delay_days", "mean"),
            sms_reminder_rate_pct=("sms_reminder_sent", lambda values: values.mean() * 100),
        )

        summary["completion_rate_pct"] = summary.apply(
            lambda row: _pct(row["completed"], row["appointments"]), axis=1
        )
        summary["no_show_rate_pct"] = summary.apply(
            lambda row: _pct(row["no_show"], row["appointments"]), axis=1
        )
        summary["cancellation_rate_pct"] = summary.apply(
            lambda row: _pct(row["cancelled"], row["appointments"]), axis=1
        )

        return _round_summary(summary.reset_index())


def export_appointment_summaries(df: pd.DataFrame, output_dir: str) -> Dict[str, Path]:
    """Write aggregate appointment summary CSVs and return their paths."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    kpis = pd.DataFrame([AppointmentKPICalculator.summary_kpis(df)])
    status = AppointmentKPICalculator.status_summary(df)
    department = AppointmentKPICalculator.department_summary(df)
    monthly = AppointmentKPICalculator.monthly_summary(df)

    outputs = {
        "kpis": output_path / "appointment_kpis.csv",
        "status": output_path / "appointment_status_summary.csv",
        "department": output_path / "appointment_department_summary.csv",
        "monthly": output_path / "appointment_monthly_summary.csv",
    }

    kpis.to_csv(outputs["kpis"], index=False)
    status.to_csv(outputs["status"], index=False)
    department.to_csv(outputs["department"], index=False)
    monthly.to_csv(outputs["monthly"], index=False)
    return outputs


def _normalize_column_name(column: object) -> str:
    return str(column).strip().lower().replace(" ", "_")


def _pct(numerator: float, denominator: float) -> float:
    return round((float(numerator) / float(denominator) * 100), 2) if denominator else 0.0


def _date_or_none(value) -> Optional[str]:
    return value.date().isoformat() if pd.notna(value) else None


def _round_summary(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = df.select_dtypes(include=["number"]).columns
    df[numeric_cols] = df[numeric_cols].round(2)
    return df
