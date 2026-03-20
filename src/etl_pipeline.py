"""
ETL (Extract Transform Load) Pipeline
Automated data processing and validation
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, Tuple, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    """Validate healthcare data quality"""
    
    @staticmethod
    def validate_completeness(df: pd.DataFrame, required_cols: List[str] = None) -> Dict:
        """
        Check for missing values
        """
        if required_cols is None:
            required_cols = df.columns.tolist()
        
        validation_results = {
            'total_records': len(df),
            'missing_by_column': df[required_cols].isnull().sum().to_dict(),
            'completeness_pct': 100 * (1 - df[required_cols].isnull().sum().sum() / (len(df) * len(required_cols)))
        }
        
        return validation_results
    
    @staticmethod
    def validate_ranges(df: pd.DataFrame, column: str, min_val: float = None, max_val: float = None) -> Dict:
        """
        Validate numeric fields are within expected ranges
        """
        issues = {
            'column': column,
            'below_min': 0,
            'above_max': 0,
            'invalid_values': []
        }
        
        if min_val is not None:
            below_min = df[df[column] < min_val]
            issues['below_min'] = len(below_min)
        
        if max_val is not None:
            above_max = df[df[column] > max_val]
            issues['above_max'] = len(above_max)
        
        issues['status'] = 'PASS' if (issues['below_min'] == 0 and issues['above_max'] == 0) else 'FAIL'
        
        return issues
    
    @staticmethod
    def validate_categories(df: pd.DataFrame, column: str, valid_values: List) -> Dict:
        """
        Validate categorical columns have valid values
        """
        if column not in df.columns:
            return {'status': 'FAIL', 'error': f'Column {column} not found'}
        
        invalid_count = len(df[~df[column].isin(valid_values)])
        
        return {
            'column': column,
            'valid_values': valid_values,
            'invalid_count': invalid_count,
            'status': 'PASS' if invalid_count == 0 else 'FAIL'
        }
    
    @staticmethod
    def generate_validation_report(df: pd.DataFrame) -> Dict:
        """
        Generate comprehensive data quality report
        """
        report = {
            'validation_timestamp': datetime.now().isoformat(),
            'total_records': len(df),
            'total_columns': len(df.columns)
        }
        
        # Completeness
        completeness = DataValidator.validate_completeness(df)
        report['completeness'] = completeness
        
        # Data type check
        report['data_types'] = df.dtypes.to_dict()
        
        # Duplicate records
        report['duplicate_records'] = len(df[df.duplicated()])
        
        # Numeric fields validation
        numeric_issues = []
        if 'wait_time_minutes' in df.columns:
            numeric_issues.append(DataValidator.validate_ranges(df, 'wait_time_minutes', 0, 600))
        if 'los_minutes' in df.columns:
            numeric_issues.append(DataValidator.validate_ranges(df, 'los_minutes', 0, 2000))
        if 'patient_satisfaction' in df.columns:
            numeric_issues.append(DataValidator.validate_ranges(df, 'patient_satisfaction', 1, 10))
        
        report['numeric_validation'] = numeric_issues
        
        # Categorical validation
        category_issues = []
        if 'department' in df.columns:
            category_issues.append(DataValidator.validate_categories(
                df, 'department', ['ED', 'IM', 'OBGYN', 'OPD', 'PED', 'SURG']
            ))
        if 'insurance_type' in df.columns:
            category_issues.append(DataValidator.validate_categories(
                df, 'insurance_type', ['Medicare', 'Medicaid', 'Private', 'Uninsured']
            ))
        
        report['categorical_validation'] = category_issues
        
        # Overall status
        report['overall_status'] = 'PASS' if completeness['completeness_pct'] > 95 else 'FAIL'
        
        return report


class DataTransformer:
    """Transform raw data into analytics-ready format"""
    
    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and standardize data
        """
        df = df.copy()
        
        # Convert date columns
        date_columns = ['visit_date', 'referral_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Ensure non-negative numeric fields
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in ['wait_time_minutes', 'los_minutes', 'referral_delay_days']:
                df[col] = np.maximum(df[col], 0)
        
        # Handle missing values
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        
        # Remove duplicates
        df = df.drop_duplicates(keep='first')
        
        logger.info(f"Data cleaning completed: {len(df)} records retained")
        
        return df
    
    @staticmethod
    def add_calculated_fields(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add derived/calculated fields
        """
        df = df.copy()
        
        # Time-based features
        if 'visit_date' in df.columns:
            df['visit_date'] = pd.to_datetime(df['visit_date'])
            df['week'] = df['visit_date'].dt.isocalendar().week
            df['month'] = df['visit_date'].dt.month
            df['day_of_week'] = df['visit_date'].dt.dayofweek
            df['quarter'] = df['visit_date'].dt.quarter
        
        # Calculate LOS in hours
        if 'los_minutes' in df.columns:
            df['los_hours'] = df['los_minutes'] / 60
        
        # Extract insurance reimbursement rate
        if 'insurance_type' in df.columns:
            reimbursement_map = {
                'Medicare': 0.65,
                'Medicaid': 0.55,
                'Private': 0.95,
                'Uninsured': 0.10
            }
            df['reimbursement_rate'] = df['insurance_type'].map(reimbursement_map)
        
        # Calculate cost effectiveness
        if 'total_cost' in df.columns and 'revenue' in df.columns:
            df['cost_per_visit'] = df['total_cost']
            df['revenue_per_visit'] = df['revenue']
        
        logger.info(f"Added {len(df.columns) - 9} calculated fields")
        
        return df
    
    @staticmethod
    def aggregate_data(df: pd.DataFrame, frequency: str = 'daily') -> pd.DataFrame:
        """
        Aggregate data by time frequency
        
        Parameters:
        - frequency: 'daily', 'weekly', 'monthly'
        """
        if 'visit_date' not in df.columns:
            return None
        
        df = df.copy()
        df['visit_date'] = pd.to_datetime(df['visit_date'])
        
        if frequency == 'daily':
            groupby_col = df['visit_date'].dt.date
        elif frequency == 'weekly':
            groupby_col = df['visit_date'].dt.to_period('W')
        elif frequency == 'monthly':
            groupby_col = df['visit_date'].dt.to_period('M')
        else:
            return None
        
        agg_dict = {}
        
        # Numeric columns - multiple aggregations
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            agg_dict[col] = ['sum', 'mean', 'std', 'min', 'max', 'count']
        
        # Categorical columns - count
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if col != 'visit_date':
                agg_dict[col] = 'nunique'
        
        aggregated = df.groupby(groupby_col).agg(agg_dict)
        
        logger.info(f"Aggregated {len(df)} records into {len(aggregated)} {frequency} periods")
        
        return aggregated


class ETLPipeline:
    """Main ETL orchestration"""
    
    def __init__(self, source_path: str):
        self.source_path = Path(source_path)
        self.validator = DataValidator()
        self.transformer = DataTransformer()
        self.pipeline_log = []
    
    def extract(self) -> pd.DataFrame:
        """Extract data from source"""
        try:
            if self.source_path.suffix == '.csv':
                df = pd.read_csv(self.source_path)
            elif self.source_path.suffix in ['.xlsx', '.xls']:
                df = pd.read_excel(self.source_path)
            else:
                raise ValueError(f"Unsupported file format: {self.source_path.suffix}")
            
            self.pipeline_log.append({
                'step': 'EXTRACT',
                'status': 'SUCCESS',
                'timestamp': datetime.now().isoformat(),
                'records_count': len(df)
            })
            
            logger.info(f"Extracted {len(df)} records from {self.source_path}")
            return df
            
        except Exception as e:
            self.pipeline_log.append({
                'step': 'EXTRACT',
                'status': 'FAILED',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            })
            logger.error(f"Extract failed: {str(e)}")
            raise
    
    def validate(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """Validate data quality"""
        try:
            validation_report = self.validator.generate_validation_report(df)
            
            self.pipeline_log.append({
                'step': 'VALIDATE',
                'status': validation_report['overall_status'],
                'timestamp': datetime.now().isoformat(),
                'completeness_pct': validation_report['completeness']['completeness_pct']
            })
            
            logger.info(f"Validation complete: {validation_report['overall_status']}")
            
            return df, validation_report
            
        except Exception as e:
            self.pipeline_log.append({
                'step': 'VALIDATE',
                'status': 'FAILED',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            })
            logger.error(f"Validation failed: {str(e)}")
            raise
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform data"""
        try:
            df = self.transformer.clean_data(df)
            df = self.transformer.add_calculated_fields(df)
            
            self.pipeline_log.append({
                'step': 'TRANSFORM',
                'status': 'SUCCESS',
                'timestamp': datetime.now().isoformat(),
                'records_count': len(df),
                'columns_count': len(df.columns)
            })
            
            logger.info(f"Transformation complete: {len(df)} records, {len(df.columns)} columns")
            
            return df
            
        except Exception as e:
            self.pipeline_log.append({
                'step': 'TRANSFORM',
                'status': 'FAILED',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            })
            logger.error(f"Transform failed: {str(e)}")
            raise
    
    def load(self, df: pd.DataFrame, output_path: str) -> bool:
        """Load data to destination"""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if output_path.suffix == '.csv':
                df.to_csv(output_path, index=False)
            elif output_path.suffix in ['.xlsx', '.xls']:
                df.to_excel(output_path, index=False)
            else:
                raise ValueError(f"Unsupported output format: {output_path.suffix}")
            
            self.pipeline_log.append({
                'step': 'LOAD',
                'status': 'SUCCESS',
                'timestamp': datetime.now().isoformat(),
                'output_path': str(output_path),
                'records_loaded': len(df)
            })
            
            logger.info(f"Loaded {len(df)} records to {output_path}")
            
            return True
            
        except Exception as e:
            self.pipeline_log.append({
                'step': 'LOAD',
                'status': 'FAILED',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            })
            logger.error(f"Load failed: {str(e)}")
            raise
    
    def run(self, output_path: str) -> Tuple[pd.DataFrame, Dict]:
        """
        Execute full ETL pipeline
        """
        logger.info("="*60)
        logger.info("ETL Pipeline Starting")
        logger.info("="*60)
        
        # Extract
        df = self.extract()
        
        # Validate
        df, validation_report = self.validate(df)
        
        # Transform
        df = self.transform(df)
        
        # Load
        self.load(df, output_path)
        
        logger.info("="*60)
        logger.info("ETL Pipeline Complete")
        logger.info("="*60)
        
        return df, {
            'validation_report': validation_report,
            'pipeline_log': self.pipeline_log
        }
    
    def get_pipeline_summary(self) -> Dict:
        """Return pipeline execution summary"""
        return {
            'execution_time': datetime.now().isoformat(),
            'steps_completed': [log['step'] for log in self.pipeline_log],
            'status': 'SUCCESS' if all(log['status'] in ['SUCCESS', 'PASS'] for log in self.pipeline_log) else 'FAILED',
            'log': self.pipeline_log
        }
