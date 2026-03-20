"""
Task Scheduler
APScheduler-based job orchestration for automated tasks
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Callable
import pytz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SchedulerManager:
    """Manage automated task scheduling"""
    
    def __init__(self, timezone: str = 'UTC'):
        """
        Initialize scheduler
        
        Parameters:
        - timezone: Timezone string (e.g., 'UTC', 'US/Eastern', 'Asia/Dubai')
        """
        self.scheduler = BackgroundScheduler(
            executors={
                'default': ThreadPoolExecutor(max_workers=5),
                'processpool': ProcessPoolExecutor(max_workers=2)
            },
            timezone=pytz.timezone(timezone)
        )
        
        self.jobs = {}
        self.job_history = []
        self.timezone = timezone
    
    def add_cron_job(self, func: Callable, job_id: str, hour: int = 0, minute: int = 0,
                     day_of_week: str = '*', description: str = '') -> None:
        """
        Add job with cron schedule
        
        Parameters:
        - func: Function to execute
        - job_id: Unique job identifier
        - hour: Hour (0-23)
        - minute: Minute (0-59)
        - day_of_week: 'mon-sun' or '*' for daily
        - description: Job description
        """
        try:
            job = self.scheduler.add_job(
                func,
                trigger=CronTrigger(hour=hour, minute=minute, day_of_week=day_of_week),
                id=job_id,
                name=description or job_id,
                replace_existing=True,
                executor='default'
            )
            
            self.jobs[job_id] = {
                'function': func.__name__,
                'schedule': f'{hour:02d}:{minute:02d} {day_of_week}',
                'description': description,
                'status': 'SCHEDULED',
                'next_run': job.next_run_time,
                'created_at': datetime.now().isoformat()
            }
            
            logger.info(f"Added cron job: {job_id} - {description}")
            
        except Exception as e:
            logger.error(f"Failed to add job {job_id}: {str(e)}")
            raise
    
    def add_interval_job(self, func: Callable, job_id: str, seconds: int = None,
                        minutes: int = None, hours: int = None, days: int = None,
                        description: str = '') -> None:
        """
        Add job with interval schedule
        
        Parameters:
        - func: Function to execute
        - job_id: Unique job identifier
        - seconds/minutes/hours/days: Interval duration
        - description: Job description
        """
        try:
            job = self.scheduler.add_job(
                func,
                trigger='interval',
                seconds=seconds,
                minutes=minutes,
                hours=hours,
                days=days,
                id=job_id,
                name=description or job_id,
                replace_existing=True
            )
            
            interval_str = f"{days}d" if days else f"{hours}h" if hours else f"{minutes}m" if minutes else f"{seconds}s"
            
            self.jobs[job_id] = {
                'function': func.__name__,
                'schedule': f'every {interval_str}',
                'description': description,
                'status': 'SCHEDULED',
                'next_run': job.next_run_time,
                'created_at': datetime.now().isoformat()
            }
            
            logger.info(f"Added interval job: {job_id} - {description}")
            
        except Exception as e:
            logger.error(f"Failed to add job {job_id}: {str(e)}")
            raise
    
    def remove_job(self, job_id: str) -> bool:
        """Remove scheduled job"""
        try:
            self.scheduler.remove_job(job_id)
            
            if job_id in self.jobs:
                self.jobs[job_id]['status'] = 'REMOVED'
            
            logger.info(f"Removed job: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {str(e)}")
            return False
    
    def pause_job(self, job_id: str) -> bool:
        """Pause scheduled job"""
        try:
            self.scheduler.pause_job(job_id)
            
            if job_id in self.jobs:
                self.jobs[job_id]['status'] = 'PAUSED'
            
            logger.info(f"Paused job: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause job {job_id}: {str(e)}")
            return False
    
    def resume_job(self, job_id: str) -> bool:
        """Resume paused job"""
        try:
            self.scheduler.resume_job(job_id)
            
            if job_id in self.jobs:
                self.jobs[job_id]['status'] = 'SCHEDULED'
            
            logger.info(f"Resumed job: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume job {job_id}: {str(e)}")
            return False
    
    def start(self) -> None:
        """Start the scheduler"""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("Scheduler started")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
            raise
    
    def shutdown(self) -> None:
        """Shutdown the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                logger.info("Scheduler shutdown")
        except Exception as e:
            logger.error(f"Failed to shutdown scheduler: {str(e)}")
    
    def get_jobs(self) -> Dict:
        """Get all scheduled jobs with status"""
        active_jobs = {}
        
        for scheduled_job in self.scheduler.get_jobs():
            active_jobs[scheduled_job.id] = {
                'name': scheduled_job.name,
                'next_run_time': scheduled_job.next_run_time.isoformat() if scheduled_job.next_run_time else None,
                'trigger': str(scheduled_job.trigger)
            }
        
        return {
            'total_jobs': len(self.jobs),
            'active_jobs': active_jobs,
            'job_definitions': self.jobs
        }
    
    def get_next_run_times(self, num_runs: int = 5) -> Dict:
        """Get next run times for all jobs"""
        next_runs = {}
        
        for scheduled_job in self.scheduler.get_jobs():
            run_times = []
            current = scheduled_job.next_run_time
            
            for _ in range(num_runs):
                if current:
                    run_times.append(current.isoformat())
                    # Estimate next run (simplified)
                    current = current + timedelta(hours=1)
            
            next_runs[scheduled_job.id] = run_times
        
        return next_runs
    
    def log_job_execution(self, job_id: str, status: str, duration_seconds: float = 0,
                         error_msg: str = None) -> None:
        """Log job execution history"""
        log_entry = {
            'job_id': job_id,
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'duration_seconds': duration_seconds,
            'error': error_msg
        }
        
        self.job_history.append(log_entry)
        
        if job_id in self.jobs:
            self.jobs[job_id]['last_execution'] = datetime.now().isoformat()
            self.jobs[job_id]['last_status'] = status
        
        logger.info(f"Job {job_id} - {status} ({duration_seconds:.2f}s)")
    
    def get_job_history(self, job_id: str = None, limit: int = 100) -> List[Dict]:
        """Get job execution history"""
        history = self.job_history
        
        if job_id:
            history = [h for h in history if h['job_id'] == job_id]
        
        return history[-limit:]
    
    def get_scheduler_status(self) -> Dict:
        """Get overall scheduler status"""
        return {
            'running': self.scheduler.running,
            'timezone': self.timezone,
            'total_jobs': len(self.scheduler.get_jobs()),
            'jobs': self.get_jobs(),
            'last_activity': datetime.now().isoformat() if self.job_history else None,
            'total_executions': len(self.job_history)
        }


class JobDefinitions:
    """Standard job definitions for healthcare analytics"""
    
    @staticmethod
    def etl_job(data_source: str, output_path: str) -> Callable:
        """Daily ETL job"""
        def execute():
            from etl_pipeline import ETLPipeline
            
            logger.info(f"Starting ETL: {data_source} -> {output_path}")
            pipeline = ETLPipeline(data_source)
            df, results = pipeline.run(output_path)
            logger.info(f"ETL complete: {len(df)} records processed")
            return results
        
        return execute
    
    @staticmethod
    def data_validation_job(data_path: str) -> Callable:
        """Data quality validation job"""
        def execute():
            from etl_pipeline import DataValidator
            import pandas as pd
            
            logger.info(f"Starting data validation: {data_path}")
            df = pd.read_csv(data_path)
            validator = DataValidator()
            report = validator.generate_validation_report(df)
            
            if report['overall_status'] != 'PASS':
                logger.warning(f"Data quality issues detected")
            
            return report
        
        return execute
    
    @staticmethod
    def model_retrain_job(data_path: str) -> Callable:
        """ML model retraining job"""
        def execute():
            from machine_learning import (
                WaitTimeForecaster, LOSForecaster, 
                ReferralDelayPredictor, PatientDemandForecaster
            )
            import pandas as pd
            
            logger.info("Starting model retraining")
            df = pd.read_csv(data_path)
            
            # Retrain models
            models = {
                'wait_time': WaitTimeForecaster(),
                'los': LOSForecaster(),
                'referral_delay': ReferralDelayPredictor(),
                'patient_demand': PatientDemandForecaster()
            }
            
            results = {}
            for name, model in models.items():
                try:
                    model.train(df)
                    results[name] = 'SUCCESS'
                    logger.info(f"Retrained: {name}")
                except Exception as e:
                    results[name] = f"FAILED: {str(e)}"
                    logger.error(f"Failed to retrain {name}: {str(e)}")
            
            return results
        
        return execute
    
    @staticmethod
    def report_generation_job(data_path: str, output_dir: str) -> Callable:
        """Daily report generation job"""
        def execute():
            from reporting import ReportGenerator
            import pandas as pd
            
            logger.info("Starting report generation")
            df = pd.read_csv(data_path)
            
            generator = ReportGenerator()
            report_data = generator.generate_from_dataframe(
                df, 
                "Daily Healthcare Analytics Report"
            )
            
            # Save reports
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            generator.save_html_report(
                report_data,
                f"{output_dir}/report_html_{timestamp}.html"
            )
            
            generator.save_summary_report(
                report_data,
                f"{output_dir}/report_summary_{timestamp}.txt"
            )
            
            logger.info("Report generation complete")
            return report_data
        
        return execute
    
    @staticmethod
    def quality_metrics_job(data_path: str) -> Callable:
        """Quality metrics calculation job"""
        def execute():
            from clinical_quality import ClinicalQualityMetrics
            import pandas as pd
            
            logger.info("Starting quality metrics calculation")
            df = pd.read_csv(data_path)
            
            quality = ClinicalQualityMetrics()
            
            metrics = {
                'readmission': quality.readmission_analysis(df),
                'adverse_events': quality.adverse_event_analysis(df),
                'mortality': quality.mortality_analysis(df),
                'satisfaction': quality.patient_satisfaction_analysis(df)
            }
            
            logger.info("Quality metrics calculated")
            return metrics
        
        return execute
    
    @staticmethod
    def financial_analysis_job(data_path: str) -> Callable:
        """Financial analysis job"""
        def execute():
            from financial_analytics import FinancialAnalytics
            import pandas as pd
            
            logger.info("Starting financial analysis")
            df = pd.read_csv(data_path)
            
            finance = FinancialAnalytics()
            analysis = {
                'costs': finance.cost_analysis(df),
                'revenue': finance.revenue_analysis(df),
                'profitability': finance.department_profitability(df)
            }
            
            logger.info("Financial analysis complete")
            return analysis
        
        return execute
