# Healthcare Data Dictionary

Complete reference to all data fields and metrics in the Healthcare Analytics system.

## Overview

The expanded dataset includes operational, financial, clinical quality, and patient safety metrics across 5,000+ patient visits.

## Patient Operational Metrics

### Basic Visit Information
| Field | Type | Description | Range/Values |
|-------|------|-------------|--------------|
| `patient_id` | String | Unique patient identifier | P00001-P99999 |
| `department` | String | Clinical department | ED, IM, OBGYN, OPD, PED, SURG |
| `visit_date` | Date | Date of visit | 2025-01-01 to 2025-12-31 |
| `visit_outcome` | String | Visit result | Discharged, Admitted, Transferred |
| `gender` | Character | Patient gender | M, F |
| `age_group` | String | Age category | 0-18, 19-45, 46-65, 65+ |

### Timing Metrics
| Field | Type | Description | Units | Typical Range |
|-------|------|-------------|-------|----------------|
| `wait_time_minutes` | Integer | Time from registration to clinical start | Minutes | 5-120 |
| `los_minutes` | Integer | Length of stay (clinical start to end) | Minutes | 30-480 |
| `referral_delay_days` | Integer | Days between referral and visit | Days | 0-20 |
| `registration_time` | DateTime | Patient registration timestamp | - | - |
| `triage_start_time` | DateTime | Triage assessment start | - | - |
| `triage_end_time` | DateTime | Triage assessment end | - | - |
| `clinical_start_time` | DateTime | Clinical care start | - | - |
| `clinical_end_time` | DateTime | Clinical care end | - | - |

## Clinical Metrics

### Patient Complexity
| Field | Type | Description | Range | Notes |
|-------|------|-------------|-------|-------|
| `severity_score` | Integer | Clinical severity (1=lowest, 5=highest) | 1-5 | Predicts resource needs |
| `comorbidity_count` | Integer | Number of chronic conditions | 0-5 | Higher = increased risk |

### Clinical Outcomes
| Field | Type | Description | Range | Notes |
|-------|------|-------------|-------|-------|
| `readmitted_30days` | Boolean | Readmission within 30 days | Yes/No | Quality indicator (~8%) |
| `adverse_event` | Boolean | Adverse event during visit | Yes/No | Patient safety metric (~2%) |
| `mortality_flag` | Boolean | Patient death during visit | Yes/No | Critical outcome (~1%) |
| `patient_satisfaction` | Decimal | Patient satisfaction score | 1.0-10.0 | Survey-based |

## Financial Metrics

### Cost Breakdown
| Field | Type | Description | Currency | Typical Range |
|-------|------|-------------|----------|----------------|
| `direct_cost` | Decimal | Personnel and facility costs | USD | $500-$50,000 |
| `supply_cost` | Decimal | Medical supplies and materials | USD | $10-$500 |
| `lab_cost` | Decimal | Laboratory testing | USD | $0-$2,000 |
| `imaging_cost` | Decimal | CT/MRI/Ultrasound | USD | $0-$3,000 |
| `pharmacy_cost` | Decimal | Medications | USD | $0-$500 |
| `total_cost` | Decimal | Sum of all costs | USD | $500-$50,000 |

### Revenue & Profitability
| Field | Type | Description | Currency | Notes |
|-------|------|-------------|----------|-------|
| `revenue` | Decimal | Reimbursement received | USD | Based on insurance |
| `profit_margin` | Decimal | Revenue minus costs | USD | Can be negative |

### Insurance
| Field | Type | Description | Values | Typical % |
|-------|------|-------------|--------|----------|
| `insurance_type` | String | Insurance coverage | Medicare, Medicaid, Private, Uninsured | 35%, 25%, 35%, 5% |

## Resource Utilization

### Staffing
| Field | Type | Description | Units | Notes |
|-------|------|-------------|-------|-------|
| `bed_hours` | Decimal | Hours bed was occupied | Hours | LOS / 60 |
| `nurse_hours` | Decimal | Nursing time allocation | Hours | ~0.5 hours/visit |
| `physician_hours` | Decimal | Physician time allocation | Hours | ~0.2 hours/visit |
| `attending_physician_id` | Integer | Primary physician ID | 1-30 | For provider analysis |
| `nurse_id` | Integer | Primary nurse ID | 1-100 | For staff analysis |

### Infrastructure
| Field | Type | Description | Type | Typical % |
|-------|------|-------------|------|----------|
| `icu_admission` | Boolean | ICU-level care needed | Yes/No | 12% of high-severity |
| `bed_hours` | Decimal | Bed occupancy hours | Hours | Capacity planning |

## Procedures & Interventions

### Surgical
| Field | Type | Description | Type | Notes |
|-------|------|-------------|------|-------|
| `surgery_performed` | Boolean | Surgical intervention | Yes/No | 80% of SURG dept |
| `blood_transfusion` | Boolean | Blood transfusion given | Yes/No | ~5% of visits |

### Diagnostic Imaging
| Field | Type | Description | Type | Typical % |
|-------|------|-------------|------|----------|
| `ct_scan` | Boolean | CT scanning performed | Yes/No | ~15% of visits |
| `mri_scan` | Boolean | MRI scanning performed | Yes/No | ~8% of visits |

## Operational Flags

### Care Coordination
| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `delay_reason` | String | Primary cause of delay | None (60%), Equipment (10%), Staff (10%), Lab_Result (10%), Specialist (5%), Bed_Availability (5%) |
| `handoff_count` | Integer | Inter-department transfers | 0-5 | Higher = care fragmentation |

## Categorical Variables

### Departments
- **ED** (Emergency Department) - Acute care, shortest LOS
- **IM** (Internal Medicine) - Complex medical conditions
- **OBGYN** (Obstetrics/Gynecology) - Higher costs, specialized
- **OPD** (Outpatient) - Lowest costs, shortest LOS
- **PED** (Pediatrics) - Special populations
- **SURG** (Surgery) - Highest costs, longer LOS

### Visit Outcomes
- **Discharged** - Sent home (60%)
- **Admitted** - Hospitalized (30%)
- **Transferred** - To another facility (10%)

### Age Groups
- **0-18** - Pediatric
- **19-45** - Young adult
- **46-65** - Mature adult
- **65+** - Elderly (higher costs, complications)

### Insurance Types
- **Medicare** - Federal elderly program (35%)
- **Medicaid** - State low-income program (25%)
- **Private** - Commercial insurance (35%)
- **Uninsured** - No coverage (5%)

## Key Performance Indicators (KPIs)

### Access & Efficiency
| KPI | Formula | Target | Current |
|-----|---------|--------|---------|
| Avg Wait Time | AVG(wait_time_minutes) | <30 min | ~40 min |
| Avg Length of Stay | AVG(los_minutes) | <180 min | ~181 min |
| Avg Referral Delay | AVG(referral_delay_days) | <3 days | ~4.5 days |

### Quality & Safety
| KPI | Formula | Target | Current |
|-----|---------|--------|---------|
| Readmission Rate | SUM(readmitted_30days) / COUNT | <7% | ~8% |
| Adverse Event Rate | SUM(adverse_event) / COUNT | <1% | ~2% |
| Mortality Rate | SUM(mortality_flag) / COUNT | <0.5% | ~1% |

### Patient Experience
| KPI | Formula | Target | Current |
|-----|---------|--------|---------|
| Avg Satisfaction | AVG(patient_satisfaction) | >8/10 | ~7.5/10 |
| Very Satisfied % | SUM(satisfaction >= 8) / COUNT | >70% | ~65% |

### Financial
| KPI | Formula | Target |
|-----|---------|--------|
| Avg Cost/Visit | AVG(total_cost) | Control costs |
| Revenue/Cost Ratio | SUM(revenue) / SUM(total_cost) | >1.0 |
| Profit Margin % | (Revenue - Cost) / Revenue * 100 | >10-20% |

### Resource
| KPI | Formula | Notes |
|-----|---------|-------|
| Nursing Hours/Visit | AVG(nurse_hours) | Staffing workload |
| Physician Hours/Visit | AVG(physician_hours) | Provider productivity |
| Bed Hours/Visit | SUM(bed_hours) | Used for capacity planning |

## Derived Metrics

### Risk Stratification
Calculated from:
- Age (0-45: 0pts, 46-65: 1pt, 65+: 2pts)
- Severity (normalized 0-3)
- Comorbidities (normalized 0-2)

**Risk Categories:**
- **Low:** Score 0-2
- **Medium:** Score 2-4
- **High:** Score 4-6
- **Critical:** Score >6

### Cost Categories
Departments have cost multipliers:
- OPD: 0.6x baseline
- ED, PED: 1.0x baseline
- IM: 1.2x baseline
- OBGYN: 1.8x baseline
- SURG: 3.5x baseline

### Severity Levels
- **1 (Minimal):** Simple diagnosis, quick resolution
- **2 (Mild):** Standard care, minor complications risk
- **3 (Moderate):** Complex condition, multi-modal treatment
- **4 (Severe):** Life-threatening, ICU possible
- **5 (Critical):** Emergency, high mortality risk

## Quality Metrics by Department

Department-level scorecards include:
- Visit volume
- Avg satisfaction
- Readmission rate
- Adverse event rate
- Mortality rate
- Avg LOS
- Avg wait time

## Data Quality Notes

### Handling Missing Data
- All cost fields default to 0 if not provided
- Satisfaction scores are estimated from wait time/LOS if not recorded
- Outcomes assumed "Discharged" if not specified

### Realistic Distributions
- Wait times: Normal distribution, mean 40 min, SD 15
- LOS: Skewed right, mean 181 min, longer for surgical
- Costs: Vary by department and severity
- Satisfaction: Inverse correlation with wait time/LOS
- Comorbidities: Poisson distribution (mean 1.5)

### Temporal Patterns
- All visits randomly distributed across 2025
- Slight variations in volume by day of week
- No explicit seasonal patterns (can be detected via autocorrelation)

## Common Use Cases

### 1. Operational Management
Use: wait_time, los, referral_delay, handoff_count, delay_reason
Goal: Optimize patient flow and clinical processes

### 2. Financial Analysis
Use: total_cost, revenue, profit_margin, insurance_type, direct_cost components
Goal: Improve profitability and cost control

### 3. Quality Improvement
Use: readmitted_30days, adverse_event, mortality_flag, patient_satisfaction
Goal: Enhance patient safety and experience

### 4. Clinical Decision Support
Use: severity_score, comorbidity_count, age_group, procedures
Goal: Risk stratification and outcome prediction

### 5. Resource Planning
Use: bed_hours, nurse_hours, physician_hours, department, los_minutes
Goal: Optimize staffing and capacity

## References

See documentation files:
- `TECHNICAL_GUIDE.md` - Architecture and modules
- `ML_GUIDE.md` - Machine learning models
- `docs/` - Comprehensive guides

---

**Last Updated:** March 20, 2026
**Data Format:** CSV (expandable to database)
**Sample Size:** 5,000+ patient visits
