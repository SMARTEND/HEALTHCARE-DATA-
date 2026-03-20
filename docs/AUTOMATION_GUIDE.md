# Healthcare Analytics Automation Guide

## Overview

The Healthcare Analytics platform includes a complete automation framework for:
- **ETL (Extract, Transform, Load)** - Automated data ingestion and cleaning
- **Reporting** - Dynamic HTML/PDF report generation
- **Scheduling** - APScheduler-based job orchestration
- **Quality Monitoring** - Automated health checks and alerts
- **Financial Analysis** - Periodic financial metrics calculation
- **ML Model Retraining** - Scheduled model updates with new data

---

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Configuration](#configuration)
3. [Job Definitions](#job-definitions)
4. [Running Automation](#running-automation)
5. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
6. [Examples](#examples)
7. [Best Practices](#best-practices)

---

## Installation & Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Create Configuration Files

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Copy YAML config (already provided)
# config.yaml contains all job definitions
```

### 3. Prepare Data Directories

```bash
# Create required directories
mkdir -p data/processed
mkdir -p reports/daily
mkdir -p reports/weekly
mkdir -p reports/archive
mkdir -p logs
```

---

## Configuration

### Environment Variables (.env)

Key settings to configure:

```env
# Data Sources
DATA_SOURCE_PATH=./data/healthcare_data.csv
DATA_OUTPUT_PATH=./data/processed/

# Email (for report distribution)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Quality Thresholds
READMISSION_THRESHOLD_PCT=8.0
ADVERSE_EVENT_THRESHOLD_PCT=2.0
MORTALITY_THRESHOLD_PCT=1.0
SATISFACTION_THRESHOLD=8.0
WAIT_TIME_THRESHOLD_MIN=30

# Scheduler
SCHEDULER_TIMEZONE=UTC
SCHEDULER_WORKER_THREADS=5
```

### YAML Configuration (config.yaml)

The `config.yaml` file defines:

**Job Scheduling:**
```yaml
jobs:
  etl_daily:
    schedule:
      type: cron
      hour: 2
      minute: 0
      day_of_week: '*'  # Runs daily at 2 AM
```

**Quality Thresholds:**
```yaml
quality_thresholds:
  readmission_rate_pct: 8.0
  adverse_event_rate_pct: 2.0
  mortality_rate_pct: 1.0
```

**Report Configuration:**
```yaml
reporting:
  default_format: html
  supported_formats: [html, pdf, csv, json]
  retention:
    days: 90
```

---

## Job Definitions

### ETL Pipeline Job

**What it does:**
- Extracts data from CSV/Excel source
- Validates data quality (completeness, ranges, categories)
- Cleans and transforms data
- Adds calculated fields (time features, costs, ratios)
- Loads processed data to output location

**Configuration:**
```yaml
etl_daily:
  schedule: cron | hour: 2 | minute: 0 | day_of_week: '*'
  parameters:
    data_source: ./data/healthcare_data.csv
    output_path: ./data/processed/
    validate: true
    backup_before_load: true
```

**Validation Rules:**
- Missing data < 5%
- Numeric fields within valid ranges
- Categorical values in allowed set
- No excessive duplicates

### Report Generation Job

**What it does:**
- Loads processed data
- Calculates KPIs and metrics
- Generates HTML/PDF/CSV reports
- Includes charts and tables
- Sends reports via email (optional)

**Configuration:**
```yaml
weekly_report:
  schedule: cron | hour: 8 | minute: 0 | day_of_week: 'mon'
  parameters:
    report_title: "Weekly Healthcare Analytics Report"
    output_format: [html, pdf, csv]
    recipients: [admin@hospital.com]
```

**Report Contents:**
- Executive summary metrics
- KPI dashboard with status indicators
- Department performance analysis
- Financial summary
- Quality metrics
- Alerts and warnings

### Quality Metrics Job

**What it does:**
- Calculates readmission rates
- Measures adverse event rates
- Analyzes patient satisfaction
- Performs risk stratification
- Triggers alerts on threshold breaches

**Configuration:**
```yaml
quality_check:
  schedule: cron | hour: 10 | minute: 0 | day_of_week: '*'
  parameters:
    metrics:
      - readmission_rate
      - adverse_events
      - mortality_rate
      - patient_satisfaction
```

**Thresholds:**
- Readmission: < 8% (status: PASS)
- Adverse Events: < 2%
- Mortality: < 1%
- Satisfaction: ≥ 8.0/10

### Model Retraining Job

**What it does:**
- Loads latest data
- Retrains all ML models
- Performs cross-validation
- Evaluates performance
- Saves updated models

**Configuration:**
```yaml
model_retrain:
  schedule: cron | hour: 3 | minute: 0 | day_of_week: 'sun'
  parameters:
    models:
      - wait_time_forecaster
      - los_forecaster
      - referral_delay_predictor
      - patient_demand_forecaster
```

**Models Retrained:**
1. **Wait Time Forecaster** - Predicts patient wait times
2. **LOS Forecaster** - Forecasts length of stay
3. **Referral Delay Predictor** - Predicts referral delays
4. **Patient Demand Forecaster** - Forecasts patient volume
5. **Seasonality Analyzer** - Detects temporal patterns

### Financial Analysis Job

**What it does:**
- Calculates total costs and revenue
- Analyzes profitability by department
- Identifies cost drivers
- Calculates ROI by intervention
- Performs break-even analysis

**Configuration:**
```yaml
financial_analysis:
  schedule: cron | hour: 6 | minute: 0 | day_of_week: '*'
  parameters:
    include_cost_breakdown: true
    include_department_analysis: true
    calculate_roi: true
```

---

## Running Automation

### Option 1: Using the Automation Example Script

```python
# Run all automation examples
python automation_example.py

# This will:
# 1. Run ETL pipeline
# 2. Generate reports
# 3. Calculate quality metrics
# 4. Perform financial analysis
# 5. Calculate KPIs
# 6. Configure scheduler
# 7. Setup report scheduling
```

### Option 2: Manual Job Scheduling

```python
from src.scheduler import SchedulerManager, JobDefinitions

# Create scheduler
scheduler = SchedulerManager(timezone='UTC')

# Add ETL job
scheduler.add_cron_job(
    func=JobDefinitions.etl_job('./data/input.csv', './data/output/'),
    job_id='daily_etl',
    hour=2,
    minute=0,
    day_of_week='*',
    description='Daily ETL'
)

# Add report job
scheduler.add_cron_job(
    func=JobDefinitions.report_generation_job('./data/output.csv', './reports/'),
    job_id='daily_report',
    hour=10,
    minute=0,
    day_of_week='*',
    description='Daily Report'
)

# Start scheduler
scheduler.start()
```

### Option 3: Configuration-Driven Setup

```python
import yaml
from src.scheduler import SchedulerManager

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Create scheduler
scheduler = SchedulerManager(timezone=config['scheduler']['timezone'])

# Setup jobs from config
for job_name, job_config in config['jobs'].items():
    if job_config['enabled']:
        # Add job based on job_name
        # (In production, use factory pattern)
        pass

# Start
scheduler.start()
```

---

## Monitoring & Troubleshooting

### Viewing Scheduled Jobs

```python
scheduler = SchedulerManager()

# Get all jobs
jobs = scheduler.get_jobs()
print(f"Total jobs: {jobs['total_jobs']}")
for job_id, job_info in jobs['active_jobs'].items():
    print(f"  {job_id}: {job_info['next_run_time']}")
```

### Checking Job History

```python
# Get execution history
history = scheduler.get_job_history(job_id='daily_etl', limit=10)
for entry in history:
    print(f"{entry['timestamp']}: {entry['status']}")
```

### Scheduler Status

```python
# Get overall status
status = scheduler.get_scheduler_status()
print(f"Running: {status['running']}")
print(f"Total jobs: {status['total_jobs']}")
print(f"Last activity: {status['last_activity']}")
```

### Troubleshooting Common Issues

#### Issue: Job Not Running

**Cause:** Scheduler not started or incorrect schedule

```python
# Check if scheduler is running
print(scheduler.scheduler.running)

# Verify next run time
for job in scheduler.scheduler.get_jobs():
    print(f"{job.id}: next run = {job.next_run_time}")

# Start scheduler if not running
scheduler.start()
```

#### Issue: Data Validation Failures

**Cause:** Missing data or out-of-range values

```python
from src.etl_pipeline import DataValidator
import pandas as pd

df = pd.read_csv('./data/input.csv')
validator = DataValidator()
report = validator.generate_validation_report(df)

print(f"Status: {report['overall_status']}")
print(f"Completeness: {report['completeness']['completeness_pct']}%")
for issue in report['numeric_validation']:
    print(f"  {issue}")
```

#### Issue: Report Generation Timeout

**Cause:** Large data volume or complex calculations

**Solution:**
1. Reduce data size or date range
2. Increase timeout in config
3. Run reports during off-peak hours

```yaml
jobs:
  daily_report:
    timeout_seconds: 3600  # 1 hour
```

#### Issue: Memory Usage High

**Cause:** Large datasets or inefficient aggregations

**Solution:**
1. Process data in batches
2. Enable parallel processing (disable if memory-constrained)
3. Archive old reports

```python
# Process in batches
from src.reporting import ReportGenerator

generator = ReportGenerator()

# Load data in chunks
for chunk in pd.read_csv('./data/large_file.csv', chunksize=1000):
    report = generator.generate_from_dataframe(chunk)
```

### Logging

Logs are written to `./logs/automation.log`

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Job started")
logger.warning("Potential issue detected")
logger.error("Job failed", exc_info=True)
```

View logs:
```bash
# Real-time tail
tail -f ./logs/automation.log

# Search for errors
grep ERROR ./logs/automation.log

# Get recent entries
tail -100 ./logs/automation.log
```

---

## Examples

### Example 1: Daily ETL + Report

```python
from src.etl_pipeline import ETLPipeline
from src.reporting import ReportGenerator
import pandas as pd

# ETL
pipeline = ETLPipeline('./data/raw_data.csv')
df, results = pipeline.run('./data/processed.csv')

# Reporting
generator = ReportGenerator()
report_data = generator.generate_from_dataframe(df, "Daily Report")
generator.save_html_report(report_data, './reports/daily.html')
```

### Example 2: Quality Monitoring

```python
from src.clinical_quality import ClinicalQualityMetrics
import pandas as pd

df = pd.read_csv('./data/processed.csv')
quality = ClinicalQualityMetrics()

# Check metrics
readmission = quality.readmission_analysis(df)
if readmission['readmission_rate'] > 8.0:
    # Send alert
    logger.warning(f"High readmission: {readmission['readmission_rate']}%")
```

### Example 3: Weekly Scheduler

```python
from src.scheduler import SchedulerManager, JobDefinitions

scheduler = SchedulerManager()

# Weekly tasks
scheduler.add_cron_job(
    JobDefinitions.etl_job('./data/raw.csv', './data/processed/'),
    'weekly_etl',
    hour=2, minute=0, day_of_week='sun'
)

scheduler.add_cron_job(
    JobDefinitions.report_generation_job('./data/processed.csv', './reports/'),
    'weekly_report',
    hour=8, minute=0, day_of_week='mon'
)

scheduler.start()
```

### Example 4: Email Report Distribution

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

def send_report_email(recipient, report_path, subject):
    msg = MIMEMultipart()
    msg['From'] = 'analytics@hospital.com'
    msg['To'] = recipient
    msg['Subject'] = subject
    
    with open(report_path, 'r') as f:
        msg.attach(MIMEText(f.read(), 'html'))
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your_email@gmail.com', 'your_password')
    server.send_message(msg)
    server.quit()

# Send report
send_report_email(
    'admin@hospital.com',
    './reports/daily.html',
    'Daily Analytics Report'
)
```

---

## Best Practices

### 1. Schedule Jobs During Off-Peak Hours

```yaml
jobs:
  heavy_etl:
    schedule:
      hour: 2    # 2 AM - low traffic
      minute: 0
      day_of_week: '*'
```

### 2. Implement Error Handling

```python
def safe_job_execution(job_func):
    def wrapper(*args, **kwargs):
        try:
            return job_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Job failed: {str(e)}")
            # Send alert to ops team
            # Implement retry logic
            raise
    return wrapper
```

### 3. Enable Audit Logging

```python
scheduler.log_job_execution(
    'daily_etl',
    status='SUCCESS',
    duration_seconds=45.2
)
```

### 4. Regular Backup of Processed Data

```yaml
jobs:
  etl_daily:
    parameters:
      backup_before_load: true  # Auto backup
```

### 5. Monitor Resource Usage

```python
import psutil

# Check memory before/after job
pid = os.getpid()
process = psutil.Process(pid)
memory_before = process.memory_info().rss / 1024 / 1024

# ... run job ...

memory_after = process.memory_info().rss / 1024 / 1024
logger.info(f"Memory used: {memory_after - memory_before:.2f} MB")
```

### 6. Alert Thresholds

Set appropriate thresholds to avoid false positives:

```yaml
quality_thresholds:
  readmission_rate_pct: 8.0     # True threshold
  alert_threshold_pct: 6.0       # Alert earlier to investigate
```

### 7. Regular Testing

Test jobs in dry-run mode before production:

```python
import os
os.environ['DRY_RUN_MODE'] = 'true'

# Run jobs - no data written
result = job_func()
```

### 8. Maintenance Schedule

- **Weekly:** Review job failures and performance
- **Monthly:** Archive old reports, optimize configurations
- **Quarterly:** Retrain ML models with full dataset
- **Annually:** Review alert thresholds, update SLAs

---

## Advanced Configuration

### Custom Job Factory

```python
class JobFactory:
    @staticmethod
    def create_job(job_config):
        job_type = job_config['type']
        if job_type == 'etl':
            return JobDefinitions.etl_job(**job_config['params'])
        elif job_type == 'report':
            return JobDefinitions.report_generation_job(**job_config['params'])
        # ... etc

# Load jobs from YAML
with open('config.yaml') as f:
    config = yaml.safe_load(f)

for job_name, job_config in config['jobs'].items():
    job_func = JobFactory.create_job(job_config)
    scheduler.add_job(job_func, job_name)
```

### Database Integration

For production, use database job store:

```yaml
scheduler:
  job_store: database
  database_url: postgresql://user:pass@localhost/scheduling
```

### Webhook Notifications

Send job notifications to monitoring system:

```python
def notify_webhook(job_id, status, duration):
    import requests
    requests.post('https://monitoring.example.com/job-complete', json={
        'job_id': job_id,
        'status': status,
        'duration': duration,
        'timestamp': datetime.now().isoformat()
    })
```

---

## Support & Documentation

For more information:
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Technical Guide](./docs/TECHNICAL_GUIDE.md)
- [ML Guide](./docs/ML_GUIDE.md)
- [Data Dictionary](./docs/DATA_DICTIONARY.md)

---

**Last Updated:** 2024
**Version:** 3.0.0
