# Machine Learning Models Guide

Complete guide to healthcare ML models and their applications.

## Quick Start

```bash
# Generate data and train all models
python example_analysis.py

# Run ML pipeline
python ml_pipeline_example.py

# Explore real-world use cases
python ml_use_cases.py
```

## Available Models

### 1. Wait Time Prediction
**What it does:** Predicts how long patients will wait before clinical care begins.

**Input Features:**
- Temporal: Day of week, month, quarter, is_weekend
- Patient: Department, age group
- Historical: Previous visit metrics

**Output:** Predicted wait time (minutes)

**Performance:** MAE ~15-20 min, R² ~0.70-0.85

**Use In:**
- Real-time patient communication
- Triage prioritization
- Resource allocation
- Queue management

**Example:**
```python
forecaster = WaitTimeForecaster()
forecaster.train_department_model(df, 'ED')
prediction = forecaster.predict(new_patient_df, 'ED')
# Returns: [42.5] minutes
```

### 2. Length of Stay (LOS) Prediction
**What it does:** Estimates how long patients will remain in the facility.

**Input Features:**
- Wait time (as predictor)
- Patient demographics
- Department
- Temporal factors

**Output:** Predicted LOS (minutes)

**Performance:** MAE ~20-40 min, R² ~0.70-0.85

**Use In:**
- Bed management
- Discharge planning
- Clinical workflow optimization
- Patient preparation

**Example:**
```python
los_model = LOSForecaster()
los_model.train_department_model(df, 'SURG')
pred_los = los_model.predict(patient_df, 'SURG')
importance = los_model.feature_importance('SURG')
```

### 3. Referral Delay Prediction
**What it does:** Forecasts delays in patient referrals and care pathways.

**Input Features:**
- Department information
- Clinical metrics (wait time, LOS)
- Temporal factors
- Historical patterns

**Output:** Predicted delay (days)

**Performance:** MAE ~1-2 days, R² ~0.50-0.70

**Use In:**
- Care continuity planning
- Identifying bottlenecks
- Proactive follow-up scheduling
- Pathway optimization

**Example:**
```python
ref_model = ReferralDelayPredictor()
ref_model.train(df)
delays = ref_model.predict(patient_df)
```

### 4. Patient Demand Forecasting
**What it does:** Projects future patient volume by department and timeframe.

**Input Features:**
- Historical volume trends
- Seasonal patterns
- Lagged metrics (previous months)

**Output:** Forecasted patient count

**Performance:** MAE <10%, Suitable for monthly planning

**Use In:**
- Capacity planning
- Staffing budgets
- Supply chain planning
- Financial forecasting

**Example:**
```python
demand = PatientDemandForecaster()
demand.train_monthly_forecast(df, department='ED')
next_3_months = demand.forecast_next_months(df, months=3, department='ED')
# Returns: [1200, 1250, 1180] patients
```

### 5. Seasonality Detection
**What it does:** Identifies recurring patterns in healthcare metrics.

**Output:**
- Autocorrelation strength
- Seasonal flag (Yes/No)
- Pattern period length

**Use In:**
- Staffing optimization
- Resource planning
- Holiday coverage
- Budget seasonality

**Example:**
```python
analyzer = SeasonalityAnalyzer()
seasonal = analyzer.detect_seasonality(df, 'wait_time_minutes', period=30)
# Returns: {'autocorrelation': 0.65, 'is_seasonal': True, 'strength': 0.65}
```

## Training Models

### Basic Training

```python
from machine_learning import WaitTimeForecaster
from analytics import HealthcareDataLoader

# Load data
loader = HealthcareDataLoader()
df = loader.load_patient_data()
df = loader.preprocess_data(df)

# Train model
forecaster = WaitTimeForecaster()
result = forecaster.train_department_model(df, 'ED')

print(f"MAE: {result['mae']:.2f} minutes")
print(f"R² Score: {result['r2']:.4f}")
```

### Training Multiple Departments

```python
results = {}
for department in df['department'].unique():
    result = forecaster.train_department_model(df, department)
    if result:
        results[department] = result
        print(f"{department}: R²={result['r2']:.4f}")
```

### Cross-Validation

Models use 80/20 train-test split automatically. For more robust validation:

```python
from sklearn.model_selection import cross_val_score

# Get predictions on test set multiple times
scores = []
for i in range(5):
    # Retrain with different random state
    result = forecaster.train_department_model(df, 'ED')
    scores.append(result['r2'])

avg_r2 = np.mean(scores)
print(f"Average R²: {avg_r2:.4f} ± {np.std(scores):.4f}")
```

## Making Predictions

### Single Record Prediction

```python
new_patient = pd.DataFrame({
    'visit_date': [pd.Timestamp.now()],
    'department': ['ED'],
    'age_group': ['45-65']
})

predicted_wait = forecaster.predict(new_patient, 'ED')
# Result: array([42.5]) - expected 42.5 minutes wait
```

### Batch Predictions

```python
patients_df = df.head(100).copy()
predictions = forecaster.predict(patients_df, 'ED')
# Result: array of 100 predicted wait times
```

### Adding Predictions to DataFrame

```python
df_results = df.copy()
df_results['predicted_wait'] = forecaster.predict(df, 'ED')
df_results['residual'] = df_results['wait_time_minutes'] - df_results['predicted_wait']

# Analyze prediction errors
print(f"Mean error: {df_results['residual'].mean():.2f} minutes")
print(f"Error std: {df_results['residual'].std():.2f} minutes")
```

## Model Evaluation

### Performance Metrics

```python
from sklearn.metrics import mean_absolute_error, r2_score

# Evaluate on test set
y_true = df_test['wait_time_minutes']
y_pred = forecaster.predict(df_test, 'ED')

mae = mean_absolute_error(y_true, y_pred)
rmse = np.sqrt(np.mean((y_true - y_pred)**2))
r2 = r2_score(y_true, y_pred)

print(f"MAE:  {mae:.2f} min")   # Average absolute error
print(f"RMSE: {rmse:.2f} min")  # Accounts for large errors
print(f"R²:   {r2:.4f}")        # Proportion of variance explained
```

### Residual Analysis

```python
residuals = y_true - y_pred

# Check for bias
print(f"Mean residual: {residuals.mean():.2f} (should be ~0)")

# Check for distribution
import matplotlib.pyplot as plt
plt.hist(residuals, bins=30)
plt.xlabel('Prediction Error (minutes)')
plt.ylabel('Frequency')
plt.title('Distribution of Prediction Errors')
plt.show()
```

### Feature Importance

```python
# For LOS model
importance = los_model.feature_importance('SURG')
print(importance)
#         feature  importance
# 0  wait_time    0.35
# 1  department   0.25
# 2  month        0.20
# 3  age_code     0.15
# 4  day_of_week  0.05
```

## Advanced Usage

### Custom Feature Engineering

```python
from machine_learning import SeasonalityAnalyzer

# Extract temporal features
analyzer = SeasonalityAnalyzer()
df_features = analyzer.extract_temporal_features(df)
df_features = analyzer.extract_department_features(df_features)

# Now has: day_of_week, month, quarter, department_code, etc.
```

### Threshold-Based Alerts

```python
# Alert if predicted wait > 60 minutes
predictions = forecaster.predict(new_patients_df, 'ED')
high_wait = new_patients_df[predictions > 60]

if len(high_wait) > 0:
    print(f"⚠️ Alert: {len(high_wait)} patients with expected wait > 60min")
```

### Time Series Decomposition

```python
# Analyze daily vs. seasonal vs. residual components
df['visit_date'] = pd.to_datetime(df['visit_date'])
daily_avg = df.groupby(df['visit_date'].dt.date)['wait_time_minutes'].mean()

# Plot components
from statsmodels.tsa.seasonal import seasonal_decompose
decomposition = seasonal_decompose(daily_avg, period=30)
decomposition.plot()
```

## Production Deployment

### 1. Model Persistence

```python
import pickle

# Save trained model
with open('wait_time_model_ed.pkl', 'wb') as f:
    pickle.dump(forecaster.models['ED'], f)

# Load in production
with open('wait_time_model_ed.pkl', 'rb') as f:
    model = pickle.load(f)
```

### 2. Automated Retraining

```bash
# Weekly retraining script
0 2 * * 0 python /path/to/retrain_models.py
```

### 3. Model Monitoring

```python
# Track model performance over time
def monitor_model(new_data, old_predictions):
    actual = new_data['wait_time_minutes']
    mae = mean_absolute_error(actual, old_predictions)
    
    if mae > threshold:
        print("⚠️ Model performance degraded - retrain recommended")
        return True
    return False
```

### 4. API Integration

```python
# Flask example
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/predict/wait_time', methods=['POST'])
def predict_wait():
    data = request.json
    patient_df = pd.DataFrame([data])
    
    prediction = forecaster.predict(patient_df, data['department'])
    
    return jsonify({
        'predicted_wait_minutes': float(prediction[0]),
        'confidence': 'high' if mae < 15 else 'medium'
    })
```

## Troubleshooting

### Issue: "Not enough training data"
- **Solution:** Ensure at least 50 records per department
- Generate more synthetic data if needed

### Issue: "Poor model performance (R² < 0.5)"
- **Solution:** 
  - Check data quality (missing values, outliers)
  - Add more features
  - Adjust model hyperparameters
  - Increase training data

### Issue: "Prediction taking too long"
- **Solution:**
  - Batch predict instead of single records
  - Cache pre-trained models
  - Consider simpler models (Linear Regression)

## References

- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Pandas Time Series](https://pandas.pydata.org/docs/user_guide/timeseries.html)
- [Feature Engineering Guide](https://feature-engine.readthedocs.io/)

## License

Same as parent project
