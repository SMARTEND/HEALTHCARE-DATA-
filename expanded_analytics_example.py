"""
Comprehensive Data Analytics Example
Demonstrates operational, financial, and clinical quality metrics
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from analytics import HealthcareDataLoader, KPICalculator
from financial_analytics import FinancialAnalytics, ProfitabilityAnalysis, BreakEvenAnalysis
from clinical_quality import ClinicalQualityMetrics, ComorbidityAnalysis, OutcomeTrajectory
from generate_data import generate_sample_data

def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")

def main():
    print_section("Comprehensive Healthcare Analytics - Expanded Data Analysis")
    
    # Step 1: Data Preparation
    print("\n[1] Preparing Expanded Dataset...")
    
    data_path = Path(__file__).parent / 'data' / 'patient_visits.csv'
    
    # Generate expanded data with financial and clinical metrics
    if not data_path.exists():
        print("  → Generating expanded synthetic dataset...")
        df = generate_sample_data(5000, data_path, expanded=True)
    else:
        print("  → Loading existing expanded dataset...")
        loader = HealthcareDataLoader()
        df = loader.load_patient_data()
        df = loader.preprocess_data(df)
    
    print(f"  ✓ Loaded {len(df):,} patient records")
    print(f"  ✓ Features: {len(df.columns)} columns")
    print(f"  ✓ Data period: {df['visit_date'].min()} to {df['visit_date'].max()}")
    
    # Step 2: Operational KPIs
    print_section("2 - Operational Performance Metrics")
    
    kpi_calc = KPICalculator()
    
    wait_stats = kpi_calc.calculate_wait_time_stats(df)
    print("\n  Wait Time Analysis:")
    print(f"    → Mean: {wait_stats['mean']:.1f} minutes")
    print(f"    → Median: {wait_stats['median']:.1f} minutes")
    print(f"    → 95th Percentile: {wait_stats['q95']:.1f} minutes")
    print(f"    → Patients waiting >60 min: {(df['wait_time_minutes'] > 60).sum():,}")
    
    los_stats = kpi_calc.calculate_los_stats(df)
    print("\n  Length of Stay Analysis:")
    print(f"    → Mean: {los_stats['mean']:.1f} minutes ({los_stats['mean']/60:.1f} hours)")
    print(f"    → Median: {los_stats['median']:.1f} minutes ({los_stats['median']/60:.1f} hours)")
    print(f"    → 95th Percentile: {los_stats['q95']:.1f} minutes ({los_stats['q95']/60:.1f} hours)")
    
    # Step 3: Financial Analysis
    print_section("3 - Financial Performance Analysis")
    
    fin_analytics = FinancialAnalytics()
    
    # Cost analysis
    print("\n  Cost Summary:")
    cost_summary = fin_analytics.cost_analysis(df, by_department=False)
    print(f"    → Total Visits: {cost_summary['total_visits']:,}")
    print(f"    → Total Cost: ${cost_summary['total_cost_sum']:,.2f}")
    print(f"    → Average Cost/Visit: ${cost_summary['avg_cost']:.2f}")
    print(f"    → Median Cost/Visit: ${cost_summary['median_cost']:.2f}")
    print(f"    → Cost Range: ${cost_summary['min_cost']:.2f} - ${cost_summary['max_cost']:.2f}")
    
    # Revenue analysis
    print("\n  Revenue & Profitability:")
    revenue_summary = fin_analytics.revenue_analysis(df)
    print(f"    → Total Revenue: ${revenue_summary['total_revenue']:,.2f}")
    print(f"    → Total Cost: ${revenue_summary['total_cost']:,.2f}")
    print(f"    → Total Profit: ${revenue_summary['total_profit']:,.2f}")
    print(f"    → Profit Margin: {revenue_summary['profit_margin']:.1f}%")
    
    # By insurance
    print("\n  Revenue by Insurance Type:")
    insurance_summary = fin_analytics.financial_summary_by_insurance(df)
    if insurance_summary is not None:
        for idx, row in insurance_summary.iterrows():
            print(f"    → {idx}: {int(row['patient_id_count']):,} visits, ${row['total_cost_mean']:.2f} avg cost")
    
    # Cost drivers
    print("\n  Cost Drivers Analysis:")
    cost_drivers = fin_analytics.cost_drivers_analysis(df)
    if cost_drivers:
        for component, percentage in cost_drivers['percentages'].items():
            print(f"    → {component}: {percentage:.1f}% of total cost")
        print(f"    → Top Driver: {cost_drivers['top_driver']}")
    
    # Department profitability
    print("\n  Department Profitability:")
    dept_profit = fin_analytics.department_performance(df)
    if dept_profit is not None:
        dept_names = df['department'].unique()
        for dept in dept_names:
            dept_data = fin_analytics.cost_analysis(df[df['department'] == dept], by_department=False)
            profit_margin = ((revenue_summary['total_revenue'] * len(df[df['department'] == dept]) / len(df) - 
                            dept_data['total_cost_sum']) / (revenue_summary['total_revenue'] * len(df[df['department'] == dept]) / len(df)) * 100) if (revenue_summary['total_revenue'] * len(df[df['department'] == dept]) / len(df)) > 0 else 0
            print(f"    → {dept}: ${dept_data['avg_cost']:.2f} avg cost, {int(len(df[df['department'] == dept])):,} visits")
    
    # Step 4: Clinical Quality Analysis
    print_section("4 - Clinical Quality & Patient Safety")
    
    quality_metrics = ClinicalQualityMetrics()
    
    # Readmission analysis
    print("\n  Readmission Analysis:")
    readmit = quality_metrics.readmission_analysis(df)
    print(f"    → Total Readmissions: {readmit['total_readmissions']:,}")
    print(f"    → Readmission Rate: {readmit['readmission_rate']:.2f}%")
    
    # Adverse events
    print("\n  Adverse Events:")
    adverse = quality_metrics.adverse_event_analysis(df)
    print(f"    → Total Events: {adverse['total_adverse_events']:,}")
    print(f"    → Event Rate: {adverse['adverse_event_rate']:.2f}%")
    
    # Mortality
    print("\n  Mortality:")
    mortality = quality_metrics.mortality_analysis(df)
    print(f"    → Total Deaths: {mortality['total_deaths']:,}")
    print(f"    → Mortality Rate: {mortality['mortality_rate']:.2f}%")
    
    # Patient satisfaction
    print("\n  Patient Satisfaction:")
    satisfaction = quality_metrics.patient_satisfaction_analysis(df)
    print(f"    → Mean Score: {satisfaction['mean_satisfaction']:.1f}/10")
    print(f"    → Very Satisfied (8-10): {satisfaction['very_satisfied']:,} ({satisfaction['very_satisfied']/len(df)*100:.1f}%)")
    print(f"    → Satisfied (6-8): {satisfaction['satisfied']:,} ({satisfaction['satisfied']/len(df)*100:.1f}%)")
    print(f"    → Dissatisfied (<6): {satisfaction['dissatisfied']:,} ({satisfaction['dissatisfied']/len(df)*100:.1f}%)")
    
    # Quality dashboard
    print("\n  Quality Indicators Dashboard:")
    dashboard = quality_metrics.quality_indicators_dashboard(df)
    for category, metrics in dashboard.items():
        print(f"\n    {category.upper()}:")
        for metric, value in metrics.items():
            if isinstance(value, float):
                if metric.endswith('rate') or metric.endswith('_pct'):
                    print(f"      • {metric}: {value:.2f}%")
                else:
                    print(f"      • {metric}: {value:.1f}")
            else:
                print(f"      • {metric}: {value:,}")
    
    # Step 5: Clinical Risk Stratification
    print_section("5 - Clinical Risk Stratification")
    
    print("\n  Risk Profile Distribution:")
    risk_df = quality_metrics.risk_stratification(df)
    risk_counts = risk_df['risk_category'].value_counts().sort_index()
    for category in ['Low', 'Medium', 'High', 'Critical']:
        count = risk_counts.get(category, 0)
        pct = count / len(df) * 100
        print(f"    → {category:10s}: {int(count):5,} patients ({pct:5.1f}%)")
    
    # Outcomes by risk
    print("\n  Outcomes by Risk Category:")
    outcomes_by_risk = quality_metrics.outcome_by_risk_group(df)
    if outcomes_by_risk is not None:
        print("\n    Metric Summary by Risk Level:")
        print(outcomes_by_risk.to_string())
    
    # Step 6: Comorbidity Impact
    print_section("6 - Comorbidity & Severity Analysis")
    
    comorbid = ComorbidityAnalysis()
    
    # High-risk patients
    print("\n  High-Risk Patients (3+ comorbidities):")
    high_risk = comorbid.high_risk_patients(df)
    if high_risk is not None and len(high_risk) > 0:
        print(f"    → Count: {len(high_risk):,} ({len(high_risk)/len(df)*100:.1f}% of total)")
        print(f"    → Readmission Rate: {high_risk['readmitted_30days'].mean()*100:.2f}%")
        print(f"    → Adverse Event Rate: {high_risk['adverse_event'].mean()*100:.2f}%")
        print(f"    → Mortality Rate: {high_risk['mortality_flag'].mean()*100:.2f}%")
    
    # Step 7: Outcome Trajectories
    print_section("7 - Severity vs. Outcomes")
    
    trajectory = OutcomeTrajectory()
    
    print("\n  Severity Score Impact (1=Minimal, 5=Critical):")
    severity_outcomes = trajectory.severity_vs_outcome(df)
    if severity_outcomes is not None:
        print("\n" + severity_outcomes.to_string())
    
    # Department scorecards
    print("\n  Department Quality Scorecard:")
    scorecard = trajectory.department_quality_scorecard(df)
    if scorecard is not None:
        print("\n" + scorecard.to_string())
    
    # Step 8: Key Insights and Recommendations
    print_section("8 - Key Insights & Recommendations")
    
    print("\n  OPERATIONAL:")
    print(f"    • Wait times average {wait_stats['mean']:.0f} minutes (target: <30)")
    print(f"      → {(df['wait_time_minutes'] > 60).sum():,} patients waiting >60 minutes")
    print(f"    • LOS average {los_stats['mean']/60:.1f} hours (target: <3)")
    
    print("\n  FINANCIAL:")
    print(f"    • Total costs: ${cost_summary['total_cost_sum']:,.0f}")
    print(f"    • Profit margin: {revenue_summary['profit_margin']:.1f}% (target: >15%)")
    if revenue_summary['profit_margin'] < 15:
        print(f"      → Need to reduce costs by {cost_summary['total_cost_sum'] * 0.15 / len(df) * (100 - revenue_summary['profit_margin']) / 100:.2f}/visit")
    
    print("\n  QUALITY:")
    print(f"    • Readmission rate: {readmit['readmission_rate']:.2f}% (benchmark: <7%)")
    print(f"    • Patient satisfaction: {satisfaction['mean_satisfaction']:.1f}/10 (target: >8.0)")
    if readmit['readmission_rate'] > 7:
        print(f"      → Investigate top readmission causes")
    
    print("\n  RESOURCE:")
    print(f"    • {len(high_risk):,} high-risk patients requiring intensive management")
    print(f"    • {mortality['total_deaths']} mortality events - review for preventability")
    
    print_section("Analysis Complete")
    print("\nAll metrics have been calculated. Review specific areas:\n")
    print("  • Financial metrics: Cost structures, insurance reimbursement effects")
    print("  • Quality metrics: Safety incidents, readmission drivers")
    print("  • Risk stratification: High-risk patient management")
    print("  • Department performance: Comparative analysis and benchmarking\n")


if __name__ == '__main__':
    main()
