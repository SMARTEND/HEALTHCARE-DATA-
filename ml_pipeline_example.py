"""
ML Pipeline Example: Complete Machine Learning Workflow
Demonstrates all predictive models and forecasting capabilities
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from analytics import HealthcareDataLoader
from machine_learning import (
    SeasonalityAnalyzer,
    WaitTimeForecaster,
    LOSForecaster,
    ReferralDelayPredictor,
    PatientDemandForecaster
)
from generate_data import generate_sample_data

def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def main():
    print_section("Healthcare Machine Learning Pipeline")
    
    # Step 1: Data Preparation
    print("\n[1] Preparing Data...")
    
    data_path = Path(__file__).parent / 'data' / 'patient_visits.csv'
    
    # Generate data if not exists
    if not data_path.exists():
        print("  → Generating synthetic dataset...")
        df = generate_sample_data(5000, data_path)
    else:
        print("  → Loading existing dataset...")
        loader = HealthcareDataLoader()
        df = loader.load_patient_data()
        df = loader.preprocess_data(df)
    
    print(f"  ✓ Loaded {len(df):,} patient records")
    print(f"  ✓ Date range: {df['visit_date'].min()} to {df['visit_date'].max()}")
    print(f"  ✓ Departments: {', '.join(df['department'].unique())}")
    
    # Step 2: Seasonality Analysis
    print_section("2 - Seasonal Pattern Detection")
    
    analyzer = SeasonalityAnalyzer()
    
    # Analyze wait time seasonality
    seasonality_wait = analyzer.detect_seasonality(df, 'wait_time_minutes', period=30)
    if seasonality_wait:
        print("\n  Wait Time Seasonality (30-day period):")
        print(f"    → Autocorrelation: {seasonality_wait['autocorrelation']:.4f}")
        print(f"    → Is Seasonal: {'Yes' if seasonality_wait['is_seasonal'] else 'No'}")
        print(f"    → Pattern Strength: {seasonality_wait['strength']:.2%}")
    
    # Analyze LOS seasonality
    seasonality_los = analyzer.detect_seasonality(df, 'los_minutes', period=30)
    if seasonality_los:
        print("\n  Length of Stay Seasonality (30-day period):")
        print(f"    → Autocorrelation: {seasonality_los['autocorrelation']:.4f}")
        print(f"    → Is Seasonal: {'Yes' if seasonality_los['is_seasonal'] else 'No'}")
        print(f"    → Pattern Strength: {seasonality_los['strength']:.2%}")
    
    # Step 3: Wait Time Prediction
    print_section("3 - Wait Time Prediction Models")
    
    wait_forecaster = WaitTimeForecaster()
    
    print("\n  Training department-specific models...")
    wait_results = []
    
    for dept in df['department'].unique():
        result = wait_forecaster.train_department_model(df, dept)
        if result:
            wait_results.append(result)
            print(f"\n  {dept} Department:")
            print(f"    → MAE: {result['mae']:.2f} minutes")
            print(f"    → R² Score: {result['r2']:.4f}")
            print(f"    → Training Samples: {result['training_samples']}")
    
    # Step 4: Length of Stay Prediction
    print_section("4 - Length of Stay (LOS) Prediction Models")
    
    los_forecaster = LOSForecaster()
    
    print("\n  Training department-specific models...")
    los_results = []
    
    for dept in df['department'].unique():
        result = los_forecaster.train_department_model(df, dept)
        if result:
            los_results.append(result)
            print(f"\n  {dept} Department:")
            print(f"    → MAE: {result['mae']:.2f} minutes")
            print(f"    → R² Score: {result['r2']:.4f}")
            print(f"    → Training Samples: {result['training_samples']}")
    
    # Feature Importance for ED
    if 'ED' in los_forecaster.models:
        print("\n  Feature Importance - ED Department (LOS):")
        importance = los_forecaster.feature_importance('ED')
        if importance is not None:
            for idx, row in importance.head(5).iterrows():
                print(f"    → {row['feature']}: {row['importance']:.4f}")
    
    # Step 5: Referral Delay Prediction
    print_section("5 - Referral Delay Prediction")
    
    referral_predictor = ReferralDelayPredictor()
    
    print("\n  Training global referral delay model...")
    referral_result = referral_predictor.train(df)
    
    if referral_result:
        print(f"  ✓ Model trained successfully")
        print(f"    → MAE: {referral_result['mae']:.2f} days")
        print(f"    → R² Score: {referral_result['r2']:.4f}")
        print(f"    → Training Samples: {referral_result['training_samples']}")
    
    # Step 6: Patient Demand Forecasting
    print_section("6 - Patient Volume Forecasting")
    
    demand_forecaster = PatientDemandForecaster()
    
    # Overall forecast
    print("\n  Training overall demand model...")
    result_overall = demand_forecaster.train_monthly_forecast(df)
    if result_overall:
        print(f"  ✓ Overall monthly forecast model trained")
        print(f"    → MAE: {result_overall['mae']:.1f} patients/month")
        
        forecast_next = demand_forecaster.forecast_next_months(df, months=3)
        if forecast_next:
            print(f"\n  Next 3 months forecast:")
            for i, forecast in enumerate(forecast_next, 1):
                print(f"    → Month {i}: {int(forecast):,} patients")
    
    # Department forecasts
    print("\n  Training department-specific demand models...")
    for dept in df['department'].unique():
        result = demand_forecaster.train_monthly_forecast(df, department=dept)
        if result:
            print(f"\n  {dept} Department:")
            print(f"    → MAE: {result['mae']:.1f} patients/month")
            
            forecast_dept = demand_forecaster.forecast_next_months(df, months=3, department=dept)
            if forecast_dept:
                print(f"    → Next 3 months: {[int(x) for x in forecast_dept]}")
    
    # Step 7: Predictive Examples
    print_section("7 - Sample Predictions")
    
    # Get sample records for each department
    for dept in df['department'].unique()[:2]:  # Show first 2 departments
        df_dept_sample = df[df['department'] == dept].head(5).copy()
        
        if len(df_dept_sample) > 0:
            print(f"\n  {dept} Department - Sample Predictions:")
            
            # Wait time
            wait_pred = wait_forecaster.predict(df_dept_sample, dept)
            if wait_pred is not None:
                actual_wait = df_dept_sample['wait_time_minutes'].values
                print(f"    Wait Time Predictions:")
                for i, (actual, pred) in enumerate(zip(actual_wait[:3], wait_pred[:3]), 1):
                    error = abs(actual - pred)
                    print(f"      • Record {i}: Actual={actual:.0f}min, Predicted={pred:.0f}min (Error={error:.0f}min)")
            
            # LOS
            los_pred = los_forecaster.predict(df_dept_sample, dept)
            if los_pred is not None:
                actual_los = df_dept_sample['los_minutes'].values
                print(f"    LOS Predictions:")
                for i, (actual, pred) in enumerate(zip(actual_los[:3], los_pred[:3]), 1):
                    error = abs(actual - pred)
                    print(f"      • Record {i}: Actual={actual:.0f}min, Predicted={pred:.0f}min (Error={error:.0f}min)")
    
    # Referral delay predictions
    referral_pred = referral_predictor.predict(df.head(5))
    if referral_pred is not None:
        print(f"\n  Referral Delay Predictions (Sample):")
        actual_ref = df.head(5)['referral_delay_days'].values
        for i, (actual, pred) in enumerate(zip(actual_ref, referral_pred), 1):
            error = abs(actual - pred)
            print(f"    • Record {i}: Actual={actual:.0f}days, Predicted={pred:.0f}days (Error={error:.0f}days)")
    
    # Step 8: Summary Report
    print_section("8 - ML Pipeline Summary")
    
    print(f"\n  Models Trained:")
    print(f"    ✓ Wait Time Models: {len(wait_results)} departments")
    print(f"    ✓ LOS Models: {len(los_results)} departments")
    print(f"    ✓ Referral Delay Model: 1 global")
    print(f"    ✓ Demand Forecasting Models: {len(demand_forecaster.models)}")
    
    print(f"\n  Model Performance (Average):")
    if wait_results:
        avg_wait_mae = np.mean([r['mae'] for r in wait_results])
        avg_wait_r2 = np.mean([r['r2'] for r in wait_results])
        print(f"    • Wait Time: MAE={avg_wait_mae:.2f}min, R²={avg_wait_r2:.4f}")
    
    if los_results:
        avg_los_mae = np.mean([r['mae'] for r in los_results])
        avg_los_r2 = np.mean([r['r2'] for r in los_results])
        print(f"    • LOS: MAE={avg_los_mae:.2f}min, R²={avg_los_r2:.4f}")
    
    print(f"\n  Use Cases:")
    print(f"    • Predict expected wait times for patients")
    print(f"    • Forecast length of stay for capacity planning")
    print(f"    • Identify and reduce referral delays")
    print(f"    • Forecast patient demand by department")
    print(f"    • Optimize resource allocation")
    
    print_section("ML Pipeline Complete!")
    print(f"\nAll models trained and ready for predictions.\n")


if __name__ == '__main__':
    main()
