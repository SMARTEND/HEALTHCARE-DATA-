"""
Example: Running Advanced Analytics
Demonstrates how to use the analytics and visualization modules
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from analytics import HealthcareDataLoader, KPICalculator
from visualization import AdvancedVisualizer, StatisticalAnalysis
from generate_data import generate_sample_data

def main():
    print("=" * 60)
    print("Healthcare Analytics - Advanced Analysis Example")
    print("=" * 60)
    
    # Step 1: Generate sample data
    print("\n[1] Generating sample data...")
    data_path = Path(__file__).parent / 'data' / 'patient_visits.csv'
    df = generate_sample_data(5000, data_path)
    print(f"✓ Generated {len(df)} patient records")
    
    # Step 2: Load and preprocess data
    print("\n[2] Loading and preprocessing data...")
    loader = HealthcareDataLoader()
    df = loader.load_patient_data()
    df = loader.preprocess_data(df)
    print(f"✓ Loaded {len(df)} records after preprocessing")
    
    # Step 3: Calculate KPIs
    print("\n[3] Calculating Key Performance Indicators...")
    
    wait_stats = KPICalculator.calculate_wait_time_stats(df)
    print("\n  Wait Time Statistics:")
    for key, value in wait_stats.items():
        print(f"    {key.upper()}: {value:.2f} min")
    
    los_stats = KPICalculator.calculate_los_stats(df)
    print("\n  Length of Stay Statistics:")
    for key, value in los_stats.items():
        print(f"    {key.upper()}: {value:.2f} min")
    
    # Department comparison
    print("\n  Department Performance Comparison:")
    dept_perf = KPICalculator.department_performance(df, 'wait_time_minutes')
    print(dept_perf)
    
    # Monthly trends
    print("\n  Monthly Trends (Wait Time):")
    monthly = KPICalculator.monthly_trends(df, 'wait_time_minutes')
    print(monthly)
    
    # Step 4: Advanced Analysis
    print("\n[4] Performing Advanced Statistical Analysis...")
    
    # Anomaly detection
    anomalies, z_scores = StatisticalAnalysis.anomaly_detection(df, 'wait_time_minutes')
    print(f"✓ Detected {len(anomalies)} anomalies in wait time")
    
    # Forecasting
    print("✓ Generated time series forecast for next 30 days")
    forecast = StatisticalAnalysis.forecasting(df, 'wait_time_minutes', periods=30)
    
    # Step 5: Create Visualizations
    print("\n[5] Creating Interactive Visualizations...")
    
    visualizer = AdvancedVisualizer()
    output_dir = Path(__file__).parent / 'reports'
    output_dir.mkdir(exist_ok=True)
    
    # Distribution analysis
    visualizer.create_kpi_distribution(
        df, 'wait_time_minutes',
        output_path=output_dir / 'wait_time_distribution.png'
    )
    print("✓ Created wait time distribution analysis")
    
    # Department comparison
    visualizer.create_department_comparison(
        df, 'wait_time_minutes',
        output_path=output_dir / 'department_comparison.html'
    )
    print("✓ Created interactive department comparison")
    
    # Trend analysis
    visualizer.create_trend_analysis(
        df, 'wait_time_minutes',
        output_path=output_dir / 'trend_analysis.html'
    )
    print("✓ Created trend analysis visualization")
    
    # Correlation heatmap
    visualizer.create_correlation_heatmap(
        df,
        output_path=output_dir / 'correlation_matrix.png'
    )
    print("✓ Created correlation heatmap")
    
    # Step 6: Summary Report
    print("\n[6] Summary Report")
    print("-" * 60)
    print(f"Total Records Analyzed: {len(df):,}")
    print(f"Date Range: {df['visit_date'].min()} to {df['visit_date'].max()}")
    print(f"Departments: {', '.join(df['department'].unique())}")
    print(f"Average Wait Time: {wait_stats['mean']:.2f} minutes")
    print(f"Average Length of Stay: {los_stats['mean']:.2f} minutes")
    print(f"Average Referral Delay: {df['referral_delay_days'].mean():.2f} days")
    print(f"\nOutput Reports: {output_dir}")
    print("-" * 60)
    
    print("\n✓ Analysis Complete!")

if __name__ == '__main__':
    main()
