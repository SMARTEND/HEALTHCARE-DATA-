# Data Directory

This directory stores datasets used in the healthcare analytics project.

## Files

- **patient_visits.csv** - Synthetic dataset of 5,000 patient visits with the following columns:
  - `patient_id`: Unique patient identifier
  - `department`: Clinical department (ED, IM, OBGYN, OPD, PED, SURG)
  - `visit_date`: Date of visit
  - `wait_time_minutes`: Minutes waited before clinical care
  - `los_minutes`: Length of stay in minutes
  - `referral_delay_days`: Days between referral and visit
  - `age_group`: Patient age category
  - `visit_outcome`: Discharge, Admitted, or Transferred

## Generation

To regenerate sample data:

```bash
python src/generate_data.py
```

## Data Privacy

This is synthetic data generated for demonstration and testing purposes only.
Any use of real patient data must comply with HIPAA and other privacy regulations.

## Data Quality

- All records have been validated for completeness
- Outliers are preserved for anomaly detection analysis
- Missing values are handled during preprocessing
- Duplicates are removed in the pipeline
