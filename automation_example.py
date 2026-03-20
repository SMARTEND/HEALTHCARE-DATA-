"""
Automated Reporting and Scheduling Example
Demonstrates full automation pipeline with ETL, transformation, reporting, and scheduling
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import logging
import time

# Import automation modules
from src.etl_pipeline import ETLPipeline, DataValidator, DataTransformer
from src.reporting import ReportGenerator, ReportScheduler
from src.scheduler import SchedulerManager, JobDefinitions
from src.analytics import HealthcareDataLoader, KPICalculator
from src.visualization import AdvancedVisualizer
from src.clinical_quality import ClinicalQualityMetrics
from src.financial_analytics import FinancialAnalytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_etl_pipeline():
    """Example: Run complete ETL pipeline"""
    logger.info("="*60)
    logger.info("EXAMPLE 1: ETL Pipeline Execution")
    logger.info("="*60)
    
    # Create sample data first
    from src.generate_data import generate_sample_data
    sample_df = generate_sample_data(num_records=1000, expanded=True)
    source_path = './data/sample_healthcare_data.csv'
    Path(source_path).parent.mkdir(parents=True, exist_ok=True)
    sample_df.to_csv(source_path, index=False)
    logger.info(f"Created sample data: {source_path}")
    
    # Initialize ETL pipeline
    pipeline = ETLPipeline(source_path)
    
    # Run ETL
    output_path = './data/processed_healthcare_data.csv'
    df, results = pipeline.run(output_path)
    
    # Print results
    logger.info(f"\nETL Pipeline Results:")
    logger.info(f"  Total Records: {len(df)}")
    logger.info(f"  Total Columns: {len(df.columns)}")
    logger.info(f"  Completeness: {results['validation_report']['completeness']['completeness_pct']:.2f}%")
    logger.info(f"  Status: {results['validation_report']['overall_status']}")
    
    return df


def example_report_generation(df):
    """Example: Generate HTML and summary reports"""
    logger.info("="*60)
    logger.info("EXAMPLE 2: Report Generation")
    logger.info("="*60)
    
    # Initialize report generator
    generator = ReportGenerator()
    
    # Generate report data
    report_data = generator.generate_from_dataframe(
        df,
        "Healthcare Analytics - Daily Report",
        period_start=df['visit_date'].min() if 'visit_date' in df.columns else None,
        period_end=df['visit_date'].max() if 'visit_date' in df.columns else None
    )
    
    # Create output directory
    report_dir = Path('./reports')
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # Save reports
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    html_path = f'{report_dir}/daily_report_{timestamp}.html'
    summary_path = f'{report_dir}/daily_summary_{timestamp}.txt'
    csv_path = f'{report_dir}/daily_data_{timestamp}.csv'
    
    logger.info("\nGenerating reports...")
    generator.save_html_report(report_data, html_path)
    generator.save_summary_report(report_data, summary_path)
    generator.save_csv_report(report_data, csv_path)
    
    logger.info(f"  HTML Report: {html_path}")
    logger.info(f"  Summary Report: {summary_path}")
    logger.info(f"  Data Report: {csv_path}")
    
    # Print key metrics
    logger.info("\nKey Metrics from Report:")
    for kpi in report_data['kpi_summary']:
        logger.info(f"  {kpi['name']}: {kpi['value']:.2f} (Status: {kpi['status']})")
    
    return report_data


def example_quality_metrics(df):
    """Example: Calculate quality metrics"""
    logger.info("="*60)
    logger.info("EXAMPLE 3: Quality Metrics Calculation")
    logger.info("="*60)
    
    quality = ClinicalQualityMetrics()
    
    logger.info("\nCalculating quality metrics...")
    
    # Readmission analysis
    readmission = quality.readmission_analysis(df)
    logger.info(f"  30-Day Readmission Rate: {readmission['readmission_rate']:.2f}%")
    
    # Adverse events
    adverse = quality.adverse_event_analysis(df)
    logger.info(f"  Adverse Event Rate: {adverse['adverse_event_rate']:.2f}%")
    
    # Mortality
    mortality = quality.mortality_analysis(df)
    logger.info(f"  Mortality Rate: {mortality['mortality_rate']:.2f}%")
    
    # Satisfaction
    satisfaction = quality.patient_satisfaction_analysis(df)
    logger.info(f"  Average Patient Satisfaction: {satisfaction['avg_satisfaction']:.2f}/10")
    
    # Risk stratification
    risk_strat = quality.patient_risk_stratification(df)
    logger.info(f"\nRisk Stratification:")
    for risk_level, count in risk_strat['risk_distribution'].items():
        logger.info(f"  {risk_level}: {count} patients")
    
    return {
        'readmission': readmission,
        'adverse_events': adverse,
        'mortality': mortality,
        'satisfaction': satisfaction,
        'risk_stratification': risk_strat
    }


def example_financial_analysis(df):
    """Example: Financial analysis"""
    logger.info("="*60)
    logger.info("EXAMPLE 4: Financial Analysis")
    logger.info("="*60)
    
    finance = FinancialAnalytics()
    
    logger.info("\nPerforming financial analysis...")
    
    # Cost analysis
    costs = finance.cost_analysis(df)
    logger.info(f"  Total Cost: ${costs['total_cost']:,.2f}")
    logger.info(f"  Average Cost per Visit: ${costs['avg_cost_per_visit']:,.2f}")
    
    # Revenue analysis
    revenue = finance.revenue_analysis(df)
    logger.info(f"  Total Revenue: ${revenue['total_revenue']:,.2f}")
    logger.info(f"  Average Revenue per Visit: ${revenue['avg_revenue_per_visit']:,.2f}")
    
    # Profitability by department
    profitability = finance.department_profitability(df)
    logger.info(f"\nDepartment Profitability:")
    for dept, metrics in profitability['department_metrics'].items():
        profit_margin = (metrics.get('profit_margin', 0) * 100) if isinstance(metrics.get('profit_margin', 0), float) else metrics.get('profit_margin', 0)
        logger.info(f"  {dept}: Margin = {profit_margin:.2f}%")
    
    return {
        'costs': costs,
        'revenue': revenue,
        'profitability': profitability
    }


def example_kpi_analysis(df):
    """Example: Calculate operational KPIs"""
    logger.info("="*60)
    logger.info("EXAMPLE 5: KPI Analysis")
    logger.info("="*60)
    
    loader = HealthcareDataLoader()
    df_loaded = loader.load_data_from_dataframe(df)
    
    calculator = KPICalculator()
    
    logger.info("\nCalculating KPIs...")
    
    # Wait time statistics
    wait_stats = calculator.calculate_wait_time_stats(df_loaded)
    logger.info(f"  Average Wait Time: {wait_stats['average']:.2f} min")
    logger.info(f"  Median Wait Time: {wait_stats['median']:.2f} min")
    logger.info(f"  95th Percentile: {wait_stats['percentile_95']:.2f} min")
    
    # LOS statistics
    los_stats = calculator.calculate_los_stats(df_loaded)
    logger.info(f"  Average Length of Stay: {los_stats['average']:.2f} min")
    logger.info(f"  Median LOS: {los_stats['median']:.2f} min")
    
    # Department performance
    dept_perf = calculator.department_performance(df_loaded)
    logger.info(f"\nDepartment Performance:")
    for idx, row in dept_perf.iterrows():
        logger.info(f"  {row['department']}: " + 
                   f"Visits={int(row['visit_count'])}, " +
                   f"Avg Wait={row['avg_wait_time']:.1f}min, " +
                   f"Satisfaction={row['avg_satisfaction']:.1f}")
    
    return {
        'wait_time_stats': wait_stats,
        'los_stats': los_stats,
        'department_performance': dept_perf
    }


def example_scheduler_setup():
    """Example: Set up automated scheduler"""
    logger.info("="*60)
    logger.info("EXAMPLE 6: Automated Scheduler Setup")
    logger.info("="*60)
    
    # Initialize scheduler
    scheduler = SchedulerManager(timezone='UTC')
    
    # Data source paths
    data_source = './data/sample_healthcare_data.csv'
    output_dir = './reports/'
    
    logger.info("\nConfiguring scheduled jobs...")
    
    # Add ETL job - Daily at 2 AM
    scheduler.add_cron_job(
        func=JobDefinitions.etl_job(data_source, output_dir),
        job_id='daily_etl',
        hour=2,
        minute=0,
        day_of_week='*',
        description='Daily ETL Pipeline'
    )
    logger.info("  ✓ Daily ETL (2:00 AM)")
    
    # Add report generation - Daily at 10 AM
    scheduler.add_cron_job(
        func=JobDefinitions.report_generation_job(data_source, output_dir),
        job_id='daily_report',
        hour=10,
        minute=0,
        day_of_week='*',
        description='Daily Report Generation'
    )
    logger.info("  ✓ Daily Report (10:00 AM)")
    
    # Add quality check - Daily at 6 AM
    scheduler.add_cron_job(
        func=JobDefinitions.quality_metrics_job(data_source),
        job_id='daily_quality_check',
        hour=6,
        minute=0,
        day_of_week='*',
        description='Daily Quality Metrics'
    )
    logger.info("  ✓ Quality Check (6:00 AM)")
    
    # Add model retraining - Weekly on Sunday at 3 AM
    scheduler.add_cron_job(
        func=JobDefinitions.model_retrain_job(data_source),
        job_id='weekly_model_retrain',
        hour=3,
        minute=0,
        day_of_week='sun',
        description='Weekly Model Retraining'
    )
    logger.info("  ✓ Model Retraining (Sunday 3:00 AM)")
    
    # Add financial analysis - Daily at 7 AM
    scheduler.add_cron_job(
        func=JobDefinitions.financial_analysis_job(data_source),
        job_id='daily_financial',
        hour=7,
        minute=0,
        day_of_week='*',
        description='Daily Financial Analysis'
    )
    logger.info("  ✓ Financial Analysis (7:00 AM)")
    
    # Print scheduled jobs
    jobs_info = scheduler.get_jobs()
    logger.info(f"\nScheduler Configuration:")
    logger.info(f"  Total Jobs: {jobs_info['total_jobs']}")
    logger.info(f"  Timezone: UTC")
    logger.info(f"  Worker Threads: 5")
    
    logger.info(f"\nJob Definitions:")
    for job_id, job_info in jobs_info['job_definitions'].items():
        logger.info(f"  {job_id}: {job_info['schedule']} - {job_info['description']}")
    
    # NOTE: Do not start scheduler in example (infinite loop)
    # In production: scheduler.start()
    
    return scheduler


def example_scheduled_report_configuration():
    """Example: Configure scheduled report generation"""
    logger.info("="*60)
    logger.info("EXAMPLE 7: Scheduled Report Configuration")
    logger.info("="*60)
    
    report_scheduler = ReportScheduler()
    
    logger.info("\nConfiguring scheduled reports...")
    
    # Daily summary report
    report_scheduler.add_scheduled_report(
        'daily_summary',
        {
            'frequency': 'daily',
            'time': '08:00',
            'data_source': './data/processed_healthcare_data.csv',
            'output_dir': './reports/daily/',
            'report_type': 'html'
        }
    )
    logger.info("  ✓ Daily Summary Report")
    
    # Weekly detailed report
    report_scheduler.add_scheduled_report(
        'weekly_detailed',
        {
            'frequency': 'weekly',
            'time': '09:00',
            'data_source': './data/processed_healthcare_data.csv',
            'output_dir': './reports/weekly/',
            'report_type': 'pdf'
        }
    )
    logger.info("  ✓ Weekly Detailed Report")
    
    # Monthly financial report
    report_scheduler.add_scheduled_report(
        'monthly_financial',
        {
            'frequency': 'monthly',
            'time': '10:00',
            'data_source': './data/processed_healthcare_data.csv',
            'output_dir': './reports/monthly/',
            'report_type': 'html'
        }
    )
    logger.info("  ✓ Monthly Financial Report")
    
    # Print configuration
    logger.info(f"\nScheduled Reports:")
    for report_name, config in report_scheduler.get_scheduled_reports().items():
        logger.info(f"  {report_name}: {config['config']['frequency']} at {config['config']['time']}")
    
    return report_scheduler


def main():
    """Run all automation examples"""
    logger.info("\n" + "="*60)
    logger.info("HEALTHCARE ANALYTICS - AUTOMATION EXAMPLES")
    logger.info("="*60 + "\n")
    
    start_time = time.time()
    
    try:
        # 1. ETL Pipeline
        df = example_etl_pipeline()
        logger.info("")
        
        # 2. Report Generation
        report_data = example_report_generation(df)
        logger.info("")
        
        # 3. Quality Metrics
        quality_results = example_quality_metrics(df)
        logger.info("")
        
        # 4. Financial Analysis
        financial_results = example_financial_analysis(df)
        logger.info("")
        
        # 5. KPI Analysis
        kpi_results = example_kpi_analysis(df)
        logger.info("")
        
        # 6. Scheduler Configuration
        scheduler = example_scheduler_setup()
        logger.info("")
        
        # 7. Report Scheduling
        report_scheduler = example_scheduled_report_configuration()
        logger.info("")
        
        # Summary
        elapsed_time = time.time() - start_time
        logger.info("="*60)
        logger.info("AUTOMATION EXAMPLES COMPLETED SUCCESSFULLY")
        logger.info("="*60)
        logger.info(f"Total Execution Time: {elapsed_time:.2f} seconds")
        logger.info("\nGenerated Artifacts:")
        logger.info("  - Processed Data File: ./data/processed_healthcare_data.csv")
        logger.info("  - HTML Reports: ./reports/daily_report_*.html")
        logger.info("  - Summary Reports: ./reports/daily_summary_*.txt")
        logger.info("  - Scheduled Jobs: 5 configured in scheduler")
        logger.info("  - Scheduled Reports: 3 configured")
        
    except Exception as e:
        logger.error(f"Error in automation examples: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
