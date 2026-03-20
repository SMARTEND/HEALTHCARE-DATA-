"""
Machine Learning Module for Healthcare Analytics
Predictive modeling and forecasting for patient metrics
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class SeasonalityAnalyzer:
    """Detect and analyze seasonal patterns in healthcare metrics"""
    
    @staticmethod
    def detect_seasonality(df: pd.DataFrame, metric: str, period: int = 30):
        """
        Detect seasonal patterns using autocorrelation
        
        Parameters:
        - df: DataFrame with time-indexed data
        - metric: Column name to analyze
        - period: Period to check for seasonality (days)
        """
        if 'visit_date' not in df.columns or metric not in df.columns:
            return None
        
        df = df.copy()
        df['visit_date'] = pd.to_datetime(df['visit_date'])
        daily_series = df.groupby(df['visit_date'].dt.date)[metric].mean()
        
        # Simple autocorrelation at specified lag
        if len(daily_series) < period * 2:
            return None
        
        lag_values = daily_series.iloc[:-period].values
        current_values = daily_series.iloc[period:].values
        
        correlation = np.corrcoef(lag_values, current_values)[0, 1]
        
        return {
            'period': period,
            'autocorrelation': correlation,
            'is_seasonal': correlation > 0.5,
            'strength': abs(correlation)
        }
    
    @staticmethod
    def extract_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
        """Extract temporal features from visit dates"""
        df = df.copy()
        df['visit_date'] = pd.to_datetime(df['visit_date'])
        
        df['day_of_week'] = df['visit_date'].dt.dayofweek
        df['week_of_year'] = df['visit_date'].dt.isocalendar().week
        df['month'] = df['visit_date'].dt.month
        df['quarter'] = df['visit_date'].dt.quarter
        df['day_of_month'] = df['visit_date'].dt.day
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        return df
    
    @staticmethod
    def extract_department_features(df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features"""
        df = df.copy()
        
        if 'department' in df.columns:
            dept_mapping = {dept: idx for idx, dept in enumerate(df['department'].unique())}
            df['department_code'] = df['department'].map(dept_mapping)
        
        if 'visit_outcome' in df.columns:
            outcome_mapping = {outcome: idx for idx, outcome in enumerate(df['visit_outcome'].unique())}
            df['outcome_code'] = df['visit_outcome'].map(outcome_mapping)
        
        if 'age_group' in df.columns:
            age_mapping = {'0-18': 0, '19-45': 1, '46-65': 2, '65+': 3}
            df['age_code'] = df['age_group'].map(age_mapping)
        
        return df


class WaitTimeForecaster:
    """Predict patient wait times using machine learning"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_names = None
        
    def prepare_features(self, df: pd.DataFrame):
        """Prepare features for modeling"""
        df = df.copy()
        
        # Extract temporal features
        analyzer = SeasonalityAnalyzer()
        df = analyzer.extract_temporal_features(df)
        df = analyzer.extract_department_features(df)
        
        # Select feature columns
        feature_cols = [col for col in df.columns 
                       if col in ['day_of_week', 'month', 'quarter', 'is_weekend',
                                 'department_code', 'age_code', 'day_of_month']]
        
        self.feature_names = feature_cols
        return df, feature_cols
    
    def train_department_model(self, df: pd.DataFrame, department: str, 
                               target: str = 'wait_time_minutes'):
        """Train separate model for each department"""
        df_dept = df[df['department'] == department].copy()
        
        if len(df_dept) < 50:
            return None
        
        df_prep, feature_cols = self.prepare_features(df_dept)
        
        X = df_prep[feature_cols].fillna(0)
        y = df_prep[target]
        
        if len(X) < 20:
            return None
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train ensemble model
        model = GradientBoostingRegressor(
            n_estimators=50,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Store model
        self.models[department] = {
            'model': model,
            'scaler': scaler,
            'features': feature_cols,
            'mae': mae,
            'r2': r2
        }
        
        return {
            'department': department,
            'mae': mae,
            'r2': r2,
            'training_samples': len(X_train)
        }
    
    def predict(self, df: pd.DataFrame, department: str):
        """Predict wait time for department"""
        if department not in self.models:
            return None
        
        model_info = self.models[department]
        model = model_info['model']
        scaler = model_info['scaler']
        features = model_info['features']
        
        df_prep, _ = self.prepare_features(df)
        X = df_prep[features].fillna(0)
        X_scaled = scaler.transform(X)
        
        predictions = model.predict(X_scaled)
        return np.maximum(predictions, 5)  # Minimum 5 minutes


class LOSForecaster:
    """Predict Length of Stay using machine learning"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        
    def prepare_features(self, df: pd.DataFrame):
        """Prepare features for modeling"""
        df = df.copy()
        
        analyzer = SeasonalityAnalyzer()
        df = analyzer.extract_temporal_features(df)
        df = analyzer.extract_department_features(df)
        
        feature_cols = [col for col in df.columns 
                       if col in ['day_of_week', 'month', 'quarter', 'is_weekend',
                                 'department_code', 'age_code', 'wait_time_minutes']]
        
        return df, feature_cols
    
    def train_department_model(self, df: pd.DataFrame, department: str,
                               target: str = 'los_minutes'):
        """Train LOS prediction model for department"""
        df_dept = df[df['department'] == department].copy()
        
        if len(df_dept) < 50:
            return None
        
        df_prep, feature_cols = self.prepare_features(df_dept)
        
        X = df_prep[feature_cols].fillna(0)
        y = df_prep[target]
        
        if len(X) < 20:
            return None
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train_scaled, y_train)
        
        y_pred = model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        self.models[department] = {
            'model': model,
            'scaler': scaler,
            'features': feature_cols,
            'mae': mae,
            'r2': r2
        }
        
        return {
            'department': department,
            'mae': mae,
            'r2': r2,
            'training_samples': len(X_train)
        }
    
    def predict(self, df: pd.DataFrame, department: str):
        """Predict LOS for department"""
        if department not in self.models:
            return None
        
        model_info = self.models[department]
        model = model_info['model']
        scaler = model_info['scaler']
        features = model_info['features']
        
        df_prep, _ = self.prepare_features(df)
        X = df_prep[features].fillna(0)
        X_scaled = scaler.transform(X)
        
        predictions = model.predict(X_scaled)
        return np.maximum(predictions, 30)  # Minimum 30 minutes
    
    def feature_importance(self, department: str):
        """Get feature importance for department"""
        if department not in self.models:
            return None
        
        model = self.models[department]['model']
        features = self.models[department]['features']
        importance = model.feature_importances_
        
        return pd.DataFrame({
            'feature': features,
            'importance': importance
        }).sort_values('importance', ascending=False)


class ReferralDelayPredictor:
    """Predict referral delays in patient care"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.features = None
    
    def prepare_features(self, df: pd.DataFrame):
        """Prepare features for referral delay prediction"""
        df = df.copy()
        
        analyzer = SeasonalityAnalyzer()
        df = analyzer.extract_temporal_features(df)
        df = analyzer.extract_department_features(df)
        
        feature_cols = [col for col in df.columns 
                       if col in ['month', 'quarter', 'department_code', 
                                 'wait_time_minutes', 'los_minutes']]
        
        return df, feature_cols
    
    def train(self, df: pd.DataFrame, target: str = 'referral_delay_days'):
        """Train referral delay prediction model"""
        df_prep, feature_cols = self.prepare_features(df)
        
        X = df_prep[feature_cols].fillna(0)
        y = df_prep[target]
        
        if len(X) < 50:
            return None
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.model = GradientBoostingRegressor(
            n_estimators=50,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        self.model.fit(X_train_scaled, y_train)
        self.features = feature_cols
        
        y_pred = self.model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        return {
            'mae': mae,
            'r2': r2,
            'training_samples': len(X_train)
        }
    
    def predict(self, df: pd.DataFrame):
        """Predict referral delays"""
        if self.model is None or self.features is None:
            return None
        
        df_prep, _ = self.prepare_features(df)
        X = df_prep[self.features].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        predictions = self.model.predict(X_scaled)
        return np.maximum(predictions, 0)  # Non-negative delays


class PatientDemandForecaster:
    """Forecast patient volume/demand"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
    
    def train_monthly_forecast(self, df: pd.DataFrame, department: str = None):
        """Train model to forecast monthly patient volume"""
        if department:
            df_dept = df[df['department'] == department].copy()
        else:
            df_dept = df.copy()
        
        if 'visit_date' not in df_dept.columns:
            return None
        
        df_dept['visit_date'] = pd.to_datetime(df_dept['visit_date'])
        
        # Create time series
        monthly_volume = df_dept.groupby(df_dept['visit_date'].dt.to_period('M')).size()
        
        if len(monthly_volume) < 6:
            return None
        
        # Create lagged features
        X_list = []
        y_list = []
        
        for i in range(3, len(monthly_volume)):
            X_list.append([
                monthly_volume.iloc[i-3],
                monthly_volume.iloc[i-2],
                monthly_volume.iloc[i-1],
                i % 12  # Month seasonality
            ])
            y_list.append(monthly_volume.iloc[i])
        
        if len(X_list) < 5:
            return None
        
        X = np.array(X_list)
        y = np.array(y_list)
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = LinearRegression()
        model.fit(X_scaled, y)
        
        y_pred = model.predict(X_scaled)
        mae = mean_absolute_error(y, y_pred)
        
        key = department if department else 'overall'
        self.models[key] = model
        self.scalers[key] = scaler
        
        return {'mae': mae, 'samples': len(X_list)}
    
    def forecast_next_months(self, df: pd.DataFrame, months: int = 3, department: str = None):
        """Forecast next N months of patient volume"""
        key = department if department else 'overall'
        
        if key not in self.models:
            return None
        
        model = self.models[key]
        scaler = self.scalers[key]
        
        if 'visit_date' not in df.columns:
            return None
        
        df = df.copy()
        df['visit_date'] = pd.to_datetime(df['visit_date'])
        
        if department:
            df_dept = df[df['department'] == department]
        else:
            df_dept = df
        
        monthly_volume = df_dept.groupby(df_dept['visit_date'].dt.to_period('M')).size()
        
        forecasts = list(monthly_volume.iloc[-3:].values)
        
        for i in range(months):
            features = [
                forecasts[-3],
                forecasts[-2],
                forecasts[-1],
                (len(monthly_volume) + i) % 12
            ]
            features_scaled = scaler.transform([features])
            forecast = model.predict(features_scaled)[0]
            forecasts.append(max(forecast, 0))
        
        return forecasts[-months:]
