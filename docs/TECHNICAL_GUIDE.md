# Technical Documentation - Healthcare Analytics Project

## Architecture Overview

This project has been enhanced to support advanced analytics capabilities using Python, SQL, and interactive visualizations.

```
HEALTHCARE-DATA-/
├── src/                          # Python analytics modules
│   ├── analytics.py             # Core KPI calculations & data loading
│   ├── visualization.py         # Advanced visualizations & statistical analysis
│   ├── generate_data.py         # Synthetic data generation
│   └── __init__.py
├── sql/                          # Database schemas
│   └── schema.sql               # SQL DDL for healthcare database
├── data/                         # Data storage
│   └── patient_visits.csv       # Sample dataset
├── reports/                      # Generated reports
├── requirements.txt              # Python dependencies
├── example_analysis.py           # Example usage script
└── README.md                     # Project documentation
```

## Quick Start Guide

### 1. Setup Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Sample Data

```bash
python src/generate_data.py
```

This creates `data/patient_visits.csv` with 5,000 synthetic patient records.

### 3. Run Example Analysis

```bash
python example_analysis.py
```

This demonstrates:
- Data loading and preprocessing
- KPI calculations
- Statistical analysis
- Interactive visualizations
- Anomaly detection
- Time series forecasting

## Core Modules

### analytics.py

**HealthcareDataLoader**
- `load_patient_data(filename)` - Load CSV data
- `preprocess_data(df)` - Clean and validate data

**KPICalculator**
- `calculate_wait_time_stats(df)` - Wait time analysis
- `calculate_los_stats(df)` - Length of stay analysis
- `department_performance(df, metric)` - Compare departments
- `monthly_trends(df, metric)` - Track trends over time

### visualization.py

**AdvancedVisualizer**
- `create_kpi_distribution(df, metric)` - Distribution plots
- `create_department_comparison(df, metric)` - Interactive comparisons
- `create_trend_analysis(df, metric)` - Trend visualization
- `create_correlation_heatmap(df)` - Correlation matrix

**StatisticalAnalysis**
- `anomaly_detection(df, metric)` - Z-score based outlier detection
- `forecasting(df, metric, periods)` - Exponential smoothing forecast

### machine_learning.py (NEW!)

**SeasonalityAnalyzer**
- `detect_seasonality(df, metric, period)` - Autocorrelation-based seasonality detection
- `extract_temporal_features(df)` - Create time-based features
- `extract_department_features(df)` - Encode categorical variables

**WaitTimeForecaster**
- `train_department_model(df, department)` - Train Gradient Boosting model per department
- `predict(df, department)` - Predict wait times
- Department-specific accuracy tracking

**LOSForecaster**
- `train_department_model(df, department)` - Train Random Forest model per department
- `predict(df, department)` - Predict length of stay
- `feature_importance(department)` - Analyze feature contributions

**ReferralDelayPredictor**
- `train(df)` - Train global referral delay model
- `predict(df)` - Forecast referral delays
- Cross-hospital standardization

**PatientDemandForecaster**
- `train_monthly_forecast(df, department)` - Train demand models
- `forecast_next_months(df, months, department)` - Multi-month forecasts
- Monthly and departmental granularity

## Database Integration

### SQL Schema

The `sql/schema.sql` file defines:

1. **Core Tables:**
   - `departments` - Department information
   - `patient_visits` - Individual visit records
   - `kpi_daily_summary` - Daily KPI aggregates
   - `department_performance` - Department-level metrics

2. **Analytics Views:**
   - `v_monthly_kpi_summary` - Monthly aggregations
   - `v_department_comparison` - Department benchmarking

### Connect to Database

```python
from sqlalchemy import create_engine

# Example: Connect to MySQL
engine = create_engine('mysql+pymysql://user:password@localhost/healthcare_db')

# Load data from database
df = pd.read_sql('SELECT * FROM patient_visits', engine)

# Save KPI results back to database
df_summary.to_sql('kpi_daily_summary', engine, if_exists='append')
```

## Data Pipeline

The recommended workflow:

```
Raw Data (CSV/Excel)
    ↓
Data Loader (analytics.py)
    ↓
Data Cleaning & Validation
    ↓
KPI Calculation
    ↓
Statistical Analysis
    ↓
Visualization & Reporting
    ↓
Database Storage (Optional)
    ↓
Dashboard/Reports
```

## Advanced Features

### 1. Anomaly Detection
Identifies outliers using Z-score method:
```python
anomalies, z_scores = StatisticalAnalysis.anomaly_detection(df, 'wait_time_minutes')
```

### 2. Time Series Forecasting
Exponential smoothing for predictive analytics:
```python
forecast = StatisticalAnalysis.forecasting(df, 'wait_time_minutes', periods=30)
```

### 3. Interactive Dashboards
Generated as HTML files using Plotly:
- Department comparison charts
- Trend analysis with rolling averages
- Correlation matrices

## Machine Learning Models (NEW!)

### Seasonality Detection
Identifies recurring patterns in healthcare metrics:

```python
analyzer = SeasonalityAnalyzer()
seasonality = analyzer.detect_seasonality(df, 'wait_time_minutes', period=30)

# Returns:
# - autocorrelation: Strength of 30-day pattern
# - is_seasonal: Boolean flag
# - strength: Pattern strength percentage
```

**Use Cases:**
- Identify peak demand periods
- Plan staffing for seasonal variations
- Optimize shift schedules

### Wait Time Prediction
Department-specific models using Gradient Boosting:

```python
wait_forecaster = WaitTimeForecaster()

# Train models for each department
for dept in df['department'].unique():
    wait_forecaster.train_department_model(df, dept)

# Make predictions
predicted_wait = wait_forecaster.predict(new_data, 'ED')
```

**Performance Metrics:**
- MAE (Mean Absolute Error): Typical ~15-20 minutes
- R² Score: Typical 0.65-0.85
- Handles department-specific patterns

### Length of Stay (LOS) Prediction
Ensemble Random Forest model for LOS forecasting:

```python
los_forecaster = LOSForecaster()

# Train and predict
los_forecaster.train_department_model(df, 'SURG')
predicted_los = los_forecaster.predict(new_data, 'SURG')

# Understand drivers
importance = los_forecaster.feature_importance('SURG')
```

**Key Features:**
- Wait time as predictor
- Patient demographics
- Day of week and seasonality
- Department-specific optimization

### Referral Delay Forecasting
Global model predicting delays in patient referrals:

```python
ref_predictor = ReferralDelayPredictor()
ref_predictor.train(df)

predicted_delays = ref_predictor.predict(patient_records)
```

**Enables:**
- Proactive referral management
- Identify bottlenecks in care pathway
- Estimate care continuity timelines

### Patient Demand Forecasting
Predict future patient volume by department:

```python
demand_forecast = PatientDemandForecaster()

# Train overall and department models
demand_forecast.train_monthly_forecast(df)
demand_forecast.train_monthly_forecast(df, department='ED')

# Forecast next 3 months
next_3_months = demand_forecast.forecast_next_months(df, months=3, department='ED')
# Result: [1200, 1250, 1180] patients
```

**Benefits:**
- Capacity planning
- Resource allocation optimization
- Budget forecasting
- Staffing decisions

## Machine Learning Workflow

```
Raw Data
    ↓
Temporal Feature Engineering
    ↓
Seasonality Analysis
    ↓
Model Training (per department/metric)
    ↓
Cross-validation & Performance Evaluation
    ↓
Predictions & Insights
    ↓
Action Items
```

## Model Selection & Algorithms

| Metric | Model | Algorithm | Why |
|--------|-------|-----------|-----|
| Wait Time | Gradient Boosting | XGBoost-style | Handles non-linear patterns |
| LOS | Random Forest | Ensemble | Captures feature interactions |
| Referral Delay | Gradient Boosting | XGBoost-style | Interpretable gradients |
| Demand | Linear Regression | Autoregressive | Simple, stable for trends |

## Feature Engineering

### Temporal Features
- Day of week (0-6)
- Week of year (1-52)
- Month (1-12)
- Quarter (1-4)
- Day of month (1-31)
- Is weekend (binary)

### Categorical Features
- Department encoding
- Visit outcome encoding
- Age group mapping

### Derived Features
- Lagged metrics (previous values)
- Rolling statistics
- Cumulative metrics

## Model Training & Evaluation

### Training Workflow
```python
# 1. Prepare features
df_prepared, features = forecaster.prepare_features(df)

# 2. Split data (80% train, 20% test)
X_train, X_test = train_test_split(X)

# 3. Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)

# 4. Train model
model.fit(X_scaled, y_train)

# 5. Evaluate
mae = mean_absolute_error(y_test, predictions)
r2 = r2_score(y_test, predictions)
```

### Expected Performance
- **Wait Time**: MAE 15-20 minutes, R² 0.65-0.85
- **LOS**: MAE 20-40 minutes, R² 0.70-0.85
- **Referral Delay**: MAE 1-2 days, R² 0.50-0.70
- **Demand**: MAE 50-100 patients/month, MAE <10%

## Performance Metrics

The analytics calculate:

- **Wait Time**: Registration to clinical start
- **Length of Stay (LOS)**: Clinical start to end
- **Referral Delay**: Days between referral date and visit
- **Department Performance**: By visit volume and metrics
- **Monthly Trends**: Seasonal patterns and changes

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | 2.1.3 | Data manipulation |
| numpy | 1.24.3 | Numerical computing |
| scikit-learn | 1.3.2 | Machine learning |
| matplotlib | 3.8.2 | Static visualizations |
| seaborn | 0.13.0 | Statistical graphics |
| plotly | 5.17.0 | Interactive charts |
| sqlalchemy | 2.0.23 | Database ORM |
| jupyter | 1.0.0 | Interactive notebooks |

## Future Enhancements

- [x] Machine learning models for wait time prediction
- [x] Length of stay forecasting
- [x] Referral delay prediction
- [x] Patient demand forecasting
- [x] Seasonal pattern detection
- [ ] Deep learning models (LSTM/GRU) for sequences
- [ ] Ensemble meta-models
- [ ] Hyperparameter optimization (Bayesian tuning)
- [ ] Real-time prediction API
- [ ] Model interpretability (SHAP/LIME)
- [ ] Multi-hospital transfer prediction
- [ ] Patient outcome risk scoring
- [ ] Cost-benefit optimization
- [ ] Power BI/Tableau connector
- [ ] REST API for predictions

## Troubleshooting

### Import Errors
Ensure virtual environment is activated and all packages are installed:
```bash
pip install -r requirements.txt
```

### Data File Not Found
Generate sample data first:
```bash
python src/generate_data.py
```

### Database Connection Issues
Verify connection string and credentials in your database config.

## Contact & Support

For questions or issues, please refer to the main README.md or create an issue in the repository.
