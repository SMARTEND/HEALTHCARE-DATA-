# Data Directory

This directory stores data files used in the healthcare analytics project.

## Files

- `healthcare visit.csv` - Raw Excel dashboard export containing KPI cards and summarized department KPI values.
- `department_kpi_summary.csv` - Clean department-level dataset extracted from the dashboard export. Columns: `department`, `wait_minutes`, `los_minutes`.
- `patient_visits.csv` - Generated synthetic patient-level dataset. This file is created by running `python src/generate_data.py`.

## Clean Department KPI Dataset

| Department | Wait Minutes | LOS Minutes |
|---|---:|---:|
| ED | 40.05 | 181.04 |
| IM | 39.63 | 180.60 |
| OBGYN | 40.19 | 179.94 |
| OPD | 40.12 | 181.86 |
| PED | 40.02 | 180.81 |
| SURG | 40.15 | 181.43 |

The generated patient-level dataset includes fields such as:

- `patient_id`: Unique patient identifier
- `department`: Clinical department, including ED, IM, OBGYN, OPD, PED, and SURG
- `visit_date`: Date of visit
- `wait_time_minutes`: Minutes waited before clinical care
- `los_minutes`: Length of stay in minutes
- `referral_delay_days`: Days between referral and visit
- `age_group`: Patient age category
- `visit_outcome`: Discharged, admitted, or transferred

## Generation

To generate the full synthetic dataset:

```bash
python src/generate_data.py
```

## Data Privacy

This project uses synthetic data for demonstration and testing only. Any use of real patient data must comply with HIPAA and applicable privacy regulations.

## Data Quality

- Missing numeric values are handled during preprocessing.
- Duplicate records are removed in the pipeline.
- Outliers are preserved for anomaly detection analysis.
- Expanded generated data includes operational, financial, and clinical quality fields.
