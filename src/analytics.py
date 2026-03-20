"""
Advanced Healthcare Analytics Module
Data loading and preprocessing utilities
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthcareDataLoader:
    """Load and validate healthcare operational data"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / 'data'
        
    def load_patient_data(self, filename: str = 'patient_visits.csv') -> pd.DataFrame:
        """Load patient visit data"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        df = pd.read_csv(filepath)
        logger.info(f"Loaded {len(df)} patient records from {filename}")
        return df
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess data"""
        df = df.copy()
        
        # Convert date columns
        date_columns = ['visit_date', 'referral_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Handle missing values
        df.fillna(df.median(numeric_only=True), inplace=True)
        
        # Remove duplicates
        df.drop_duplicates(inplace=True)
        
        logger.info("Data preprocessing completed")
        return df


class KPICalculator:
    """Calculate healthcare KPIs"""
    
    @staticmethod
    def calculate_wait_time_stats(df: pd.DataFrame) -> dict:
        """Calculate wait time statistics"""
        wait_time = df['wait_time_minutes'] if 'wait_time_minutes' in df.columns else []
        
        return {
            'mean': wait_time.mean() if len(wait_time) > 0 else 0,
            'median': wait_time.median() if len(wait_time) > 0 else 0,
            'std': wait_time.std() if len(wait_time) > 0 else 0,
            'min': wait_time.min() if len(wait_time) > 0 else 0,
            'max': wait_time.max() if len(wait_time) > 0 else 0,
            'q75': wait_time.quantile(0.75) if len(wait_time) > 0 else 0,
            'q95': wait_time.quantile(0.95) if len(wait_time) > 0 else 0,
        }
    
    @staticmethod
    def calculate_los_stats(df: pd.DataFrame) -> dict:
        """Calculate Length of Stay statistics"""
        los = df['los_minutes'] if 'los_minutes' in df.columns else []
        
        return {
            'mean': los.mean() if len(los) > 0 else 0,
            'median': los.median() if len(los) > 0 else 0,
            'std': los.std() if len(los) > 0 else 0,
            'min': los.min() if len(los) > 0 else 0,
            'max': los.max() if len(los) > 0 else 0,
            'q75': los.quantile(0.75) if len(los) > 0 else 0,
            'q95': los.quantile(0.95) if len(los) > 0 else 0,
        }
    
    @staticmethod
    def department_performance(df: pd.DataFrame, metric: str = 'wait_time_minutes') -> pd.DataFrame:
        """Compare KPI performance across departments"""
        if 'department' not in df.columns or metric not in df.columns:
            return pd.DataFrame()
        
        return df.groupby('department')[metric].agg([
            'count', 'mean', 'median', 'std', 'min', 'max'
        ]).round(2)
    
    @staticmethod
    def monthly_trends(df: pd.DataFrame, metric: str = 'wait_time_minutes') -> pd.DataFrame:
        """Calculate monthly trends for KPI"""
        if 'visit_date' not in df.columns or metric not in df.columns:
            return pd.DataFrame()
        
        df = df.copy()
        df['year_month'] = pd.to_datetime(df['visit_date']).dt.to_period('M')
        
        return df.groupby('year_month')[metric].agg([
            'count', 'mean', 'median', 'std'
        ]).round(2)
