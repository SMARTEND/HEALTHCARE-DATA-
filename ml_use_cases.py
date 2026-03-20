"""
Advanced ML Use Cases and Examples
Production-ready examples for deploying ML models
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import pandas as pd
import numpy as np
from analytics import HealthcareDataLoader
from machine_learning import (
    WaitTimeForecaster, LOSForecaster, PatientDemandForecaster
)

def use_case_1_real_time_wait_prediction():
    """
    USE CASE 1: Real-time Wait Time Prediction
    Predict wait time for incoming patients
    """
    print("\n" + "="*70)
    print("USE CASE 1: Real-Time Wait Time Prediction for Incoming Patients")
    print("="*70)
    
    # Load data
    loader = HealthcareDataLoader()
    df = loader.load_patient_data()
    df = loader.preprocess_data(df)
    
    # Train models
    wait_forecaster = WaitTimeForecaster()
    print("\n[1] Training models on historical data...")
    for dept in df['department'].unique():
        result = wait_forecaster.train_department_model(df, dept)
        if result:
            print(f"  ✓ {dept}: R²={result['r2']:.4f}")
    
    # New patient arriving
    print("\n[2] New patient arrives at ED department...")
    new_patient = pd.DataFrame({
        'visit_date': [pd.Timestamp.now()],
        'department': ['ED'],
        'age_group': ['45-65'],
        'visit_outcome': ['Discharged']
    })
    
    # Predict wait time
    predicted_wait = wait_forecaster.predict(new_patient, 'ED')
    
    print(f"\n[3] Prediction Result:")
    print(f"  Expected Wait Time: {predicted_wait[0]:.0f} minutes")
    print(f"  95% Confidence Range: {predicted_wait[0]*.8:.0f} - {predicted_wait[0]*1.2:.0f} minutes")
    print(f"\n  ✓ Action: Communicate to patient and plan engagement")


def use_case_2_capacity_planning():
    """
    USE CASE 2: Capacity Planning and Resource Allocation
    Forecast patient demand for next 3 months
    """
    print("\n" + "="*70)
    print("USE CASE 2: Capacity Planning and Resource Allocation")
    print("="*70)
    
    loader = HealthcareDataLoader()
    df = loader.load_patient_data()
    df = loader.preprocess_data(df)
    
    # Train demand forecaster
    demand_forecaster = PatientDemandForecaster()
    print("\n[1] Training demand forecasting models...")
    
    departments = df['department'].unique()
    forecasts_by_dept = {}
    
    for dept in departments:
        result = demand_forecaster.train_monthly_forecast(df, department=dept)
        if result:
            forecast = demand_forecaster.forecast_next_months(df, months=3, department=dept)
            if forecast:
                forecasts_by_dept[dept] = forecast
                print(f"  ✓ {dept}: 3-month forecast = {[int(x) for x in forecast]}")
    
    # Capacity planning
    print("\n[2] Capacity Planning Analysis:")
    print(f"\n  {'Department':<10} {'Month 1':<12} {'Month 2':<12} {'Month 3':<12} {'Trend':<10}")
    print("  " + "-"*60)
    
    for dept, forecast in forecasts_by_dept.items():
        trend = "📈 UP" if forecast[-1] > forecast[0] else "📉 DOWN"
        print(f"  {dept:<10} {int(forecast[0]):<12} {int(forecast[1]):<12} {int(forecast[2]):<12} {trend:<10}")
    
    # Resource recommendations
    print("\n[3] Resource Allocation Recommendations:")
    print(f"  • Increase staffing for high-demand departments")
    print(f"  • Pre-schedule more clinicians for month with peak volume")
    print(f"  • Prepare additional supplies/equipment accordingly")
    print(f"  • Plan training/coverage for departments with increasing demand")


def use_case_3_los_optimization():
    """
    USE CASE 3: Length of Stay Optimization
    Identify and reduce LOS for high-risk cases
    """
    print("\n" + "="*70)
    print("USE CASE 3: Length of Stay Optimization")
    print("="*70)
    
    loader = HealthcareDataLoader()
    df = loader.load_patient_data()
    df = loader.preprocess_data(df)
    
    # Train LOS models
    los_forecaster = LOSForecaster()
    print("\n[1] Training LOS prediction models...")
    
    for dept in df['department'].unique():
        result = los_forecaster.train_department_model(df, dept)
        if result:
            print(f"  ✓ {dept}: MAE={result['mae']:.1f}min")
    
    # Analyze high-risk cases
    print("\n[2] Identifying high-risk LOS cases for SURG department...")
    
    df_surg = df[df['department'] == 'SURG'].copy()
    surg_los_pred = los_forecaster.predict(df_surg.head(10), 'SURG')
    surg_actual = df_surg.head(10)['los_minutes'].values
    
    # Flag cases with extended LOS
    high_risk = []
    for i, (actual, pred) in enumerate(zip(surg_actual, surg_los_pred)):
        if actual > pred * 1.3:  # 30% longer than expected
            high_risk.append({
                'patient': i,
                'expected_los': pred,
                'actual_los': actual,
                'excess': actual - pred
            })
    
    if high_risk:
        print(f"\n  Found {len(high_risk)} cases with extended LOS:")
        for case in high_risk[:3]:
            print(f"    • Patient {case['patient']}: Expected {case['expected_los']:.0f}min, "
                  f"Actual {case['actual_los']:.0f}min (Excess: {case['excess']:.0f}min)")
    
    # Feature importance
    print("\n[3] Key Drivers of Length of Stay (SURG):")
    importance = los_forecaster.feature_importance('SURG')
    if importance is not None:
        for idx, row in importance.head(3).iterrows():
            print(f"    • {row['feature']}: {row['importance']:.1%}")
    
    print("\n[4] Recommendations:")
    print(f"  • Review clinical workflows for efficiency")
    print(f"  • Optimize discharge planning process")
    print(f"  • Pre-arrange follow-up appointments")
    print(f"  • Enhance case coordination for complex cases")


def use_case_4_referral_management():
    """
    USE CASE 4: Referral Management and Care Continuity
    Predict and reduce referral delays
    """
    print("\n" + "="*70)
    print("USE CASE 4: Referral Management and Care Continuity")
    print("="*70)
    
    from machine_learning import ReferralDelayPredictor
    
    loader = HealthcareDataLoader()
    df = loader.load_patient_data()
    df = loader.preprocess_data(df)
    
    # Train referral predictor
    ref_predictor = ReferralDelayPredictor()
    print("\n[1] Training referral delay prediction model...")
    result = ref_predictor.train(df)
    if result:
        print(f"  ✓ Model trained: MAE={result['mae']:.2f} days, R²={result['r2']:.4f}")
    
    # Predict delays for incoming referrals
    print("\n[2] Assessing referral delays for new patients...")
    
    new_referrals = df.sample(5).copy()
    predicted_delays = ref_predictor.predict(new_referrals)
    actual_delays = new_referrals['referral_delay_days'].values
    
    print(f"\n  {'Referral':<12} {'Predicted':<12} {'Actual':<12} {'Status':<15}")
    print("  " + "-"*50)
    
    at_risk = []
    for i, (pred, actual) in enumerate(zip(predicted_delays, actual_delays)):
        status = "🟢 Normal" if pred <= 5 else "🔴 HIGH RISK" if pred > 7 else "🟡 CAUTION"
        print(f"  {i+1:<12} {pred:.1f} days{'':<3} {actual:.1f} days{'':<3} {status:<15}")
        
        if pred > actual * 1.2:  # High-risk prediction
            at_risk.append(i)
    
    # Mitigation strategies
    print("\n[3] Mitigation Strategies for High-Risk Referrals:")
    print(f"  • Expedite specialist appointment scheduling")
    print(f"  • Establish direct communication channels")
    print(f"  • Provide interim management protocols")
    print(f"  • Track referral status actively")
    print(f"  • Consider urgent referral fast-track for critical cases")


def use_case_5_seasonal_staffing():
    """
    USE CASE 5: Seasonal Staffing Optimization
    Adjust staffing based on demand seasonality
    """
    print("\n" + "="*70)
    print("USE CASE 5: Seasonal Staffing Optimization")
    print("="*70)
    
    from machine_learning import SeasonalityAnalyzer
    
    loader = HealthcareDataLoader()
    df = loader.load_patient_data()
    df = loader.preprocess_data(df)
    
    analyzer = SeasonalityAnalyzer()
    
    print("\n[1] Detecting seasonal patterns in patient demand...")
    
    seasonality = analyzer.detect_seasonality(df, 'wait_time_minutes', period=30)
    if seasonality:
        print(f"\n  Seasonality Detected:")
        print(f"    • Autocorrelation @ 30-day lag: {seasonality['autocorrelation']:.4f}")
        print(f"    • Pattern Strength: {seasonality['strength']:.1%}")
        print(f"    • Is Seasonal: {'Yes ✓' if seasonality['is_seasonal'] else 'No'}")
    
    print("\n[2] Seasonal Staffing Plan:")
    print(f"  • Peak Period: Plan for +20% additional staff")
    print(f"  • Off-Peak: Reduce to 80% normal staffing")
    print(f"  • Transition Weeks: Gradually adjust + 10% buffer")
    print(f"  • Cross-training: Prepare staff for flexible deployment")
    
    print("\n[3] Action Items:")
    print(f"  ✓ Create 12-month staffing calendar")
    print(f"  ✓ Coordinate with HR for seasonal hiring")
    print(f"  ✓ Plan training schedules in advance")
    print(f"  ✓ Set contingency staffing budget +15%")


def main():
    print("\n" + "="*70)
    print("HEALTHCARE ML - ADVANCED USE CASES")
    print("Production-Ready Examples for Healthcare Operations")
    print("="*70)
    
    try:
        use_case_1_real_time_wait_prediction()
        use_case_2_capacity_planning()
        use_case_3_los_optimization()
        use_case_4_referral_management()
        use_case_5_seasonal_staffing()
        
        print("\n" + "="*70)
        print("✓ All use cases demonstrated successfully!")
        print("="*70)
        print("\nNext Steps:")
        print("1. Deploy to production environment")
        print("2. Set up automated retraining schedule (weekly/monthly)")
        print("3. Create monitoring dashboards")
        print("4. Establish feedback loops for model improvement")
        print("5. Integrate predictions into operational dashboards")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Make sure to run: python example_analysis.py first")
        print("This generates the sample data required for these examples")


if __name__ == '__main__':
    main()
