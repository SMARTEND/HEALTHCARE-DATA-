"""
Example: Analyze appointment scheduling data from Excel or CSV.
"""

import argparse
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent / "src"))

from appointment_analytics import (  # noqa: E402
    AppointmentDataLoader,
    AppointmentKPICalculator,
    export_appointment_summaries,
)


def main():
    parser = argparse.ArgumentParser(description="Analyze healthcare appointment scheduling data.")
    parser.add_argument("source", help="Path to Healthcare Appointments.xlsx or an appointment CSV export.")
    parser.add_argument("--sheet-name", default=None, help="Excel sheet name. Defaults to the first sheet.")
    parser.add_argument("--output-dir", default="data", help="Directory for aggregate summary CSV outputs.")
    args = parser.parse_args()

    loader = AppointmentDataLoader(args.source, sheet_name=args.sheet_name)
    df = loader.load()
    kpis = AppointmentKPICalculator.summary_kpis(df)
    outputs = export_appointment_summaries(df, args.output_dir)

    print("=" * 64)
    print("Healthcare Appointment Scheduling Analysis")
    print("=" * 64)
    print(f"Source rows: {kpis['total_appointments']:,}")
    print(f"Date range: {kpis['appointment_start_date']} to {kpis['appointment_end_date']}")
    print(f"Completion rate: {kpis['completion_rate_pct']:.2f}%")
    print(f"No-show rate: {kpis['no_show_rate_pct']:.2f}%")
    print(f"Cancellation rate: {kpis['cancellation_rate_pct']:.2f}%")
    print(f"Average wait time: {kpis['avg_wait_time_min']:.2f} minutes")
    print(f"Average service duration: {kpis['avg_service_duration_min']:.2f} minutes")
    print(f"Average referral delay: {kpis['avg_referral_delay_days']:.2f} days")
    print("\nGenerated summary files:")
    for label, path in outputs.items():
        print(f"  {label}: {path}")


if __name__ == "__main__":
    main()
