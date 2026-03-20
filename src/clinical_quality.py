"""
Clinical Quality and Patient Safety Metrics Module
Patient outcomes, safety, and quality indicators
"""

import pandas as pd
import numpy as np
from datetime import datetime


class ClinicalQualityMetrics:
    """Analyze clinical quality and patient safety metrics"""
    
    @staticmethod
    def readmission_analysis(df: pd.DataFrame, by_department: bool = True) -> dict:
        """
        Analyze 30-day readmission rates
        """
        if 'readmitted_30days' not in df.columns:
            return None
        
        analysis = {
            'total_readmissions': df['readmitted_30days'].sum(),
            'readmission_rate': df['readmitted_30days'].mean() * 100,
            'readmission_rate_std': df['readmitted_30days'].std() * 100
        }
        
        if by_department and 'department' in df.columns:
            dept_readmissions = df.groupby('department').agg({
                'readmitted_30days': ['sum', 'mean'],
                'patient_id': 'count'
            }).round(4)
            
            dept_readmissions.columns = ['_'.join(col).strip() for col in dept_readmissions.columns.values]
            analysis['by_department'] = dept_readmissions
        
        return analysis
    
    @staticmethod
    def adverse_event_analysis(df: pd.DataFrame) -> dict:
        """
        Analyze adverse events and safety incidents
        """
        if 'adverse_event' not in df.columns:
            return None
        
        analysis = {
            'total_adverse_events': df['adverse_event'].sum(),
            'adverse_event_rate': df['adverse_event'].mean() * 100,
            'total_visits': len(df)
        }
        
        # By department
        if 'department' in df.columns:
            dept_events = df.groupby('department').agg({
                'adverse_event': ['sum', 'mean'],
                'patient_id': 'count'
            }).round(4)
            analysis['by_department'] = dept_events
        
        # By severity
        if 'severity_score' in df.columns:
            severity_events = df.groupby('severity_score')['adverse_event'].agg(['sum', 'mean']).round(4)
            analysis['by_severity'] = severity_events
        
        return analysis
    
    @staticmethod
    def mortality_analysis(df: pd.DataFrame) -> dict:
        """
        Analyze mortality rates and outcomes
        """
        if 'mortality_flag' not in df.columns:
            return None
        
        analysis = {
            'total_deaths': df['mortality_flag'].sum(),
            'mortality_rate': df['mortality_flag'].mean() * 100,
            'total_visits': len(df)
        }
        
        # By department
        if 'department' in df.columns:
            dept_mortality = df.groupby('department').agg({
                'mortality_flag': ['sum', 'mean'],
                'patient_id': 'count',
                'los_minutes': 'mean' if 'los_minutes' in df.columns else None
            }).round(4)
            analysis['by_department'] = dept_mortality
        
        # By severity
        if 'severity_score' in df.columns:
            severity_mortality = df.groupby('severity_score')['mortality_flag'].agg(['sum', 'mean']).round(4)
            analysis['by_severity'] = severity_mortality
        
        # By comorbidity
        if 'comorbidity_count' in df.columns:
            comorbid_mortality = df.groupby('comorbidity_count')['mortality_flag'].agg(['sum', 'mean']).round(4)
            analysis['by_comorbidity'] = comorbid_mortality
        
        return analysis
    
    @staticmethod
    def patient_satisfaction_analysis(df: pd.DataFrame) -> dict:
        """
        Analyze patient satisfaction scores
        """
        if 'patient_satisfaction' not in df.columns:
            return None
        
        analysis = {
            'mean_satisfaction': df['patient_satisfaction'].mean(),
            'median_satisfaction': df['patient_satisfaction'].median(),
            'std_satisfaction': df['patient_satisfaction'].std(),
            'min_satisfaction': df['patient_satisfaction'].min(),
            'max_satisfaction': df['patient_satisfaction'].max(),
            'very_satisfied': (df['patient_satisfaction'] >= 8).sum(),
            'satisfied': ((df['patient_satisfaction'] >= 6) & (df['patient_satisfaction'] < 8)).sum(),
            'dissatisfied': (df['patient_satisfaction'] < 6).sum()
        }
        
        # By department
        if 'department' in df.columns:
            dept_satisfaction = df.groupby('department')['patient_satisfaction'].agg([
                'count', 'mean', 'median', 'std', 'min', 'max'
            ]).round(2)
            analysis['by_department'] = dept_satisfaction
        
        # Correlation with outcomes
        if 'readmitted_30days' in df.columns:
            satisfied = df[df['patient_satisfaction'] >= 8]
            dissatisfied = df[df['patient_satisfaction'] < 6]
            
            analysis['satisfaction_vs_readmission'] = {
                'very_satisfied_readmit_rate': satisfied['readmitted_30days'].mean() * 100 if len(satisfied) > 0 else 0,
                'dissatisfied_readmit_rate': dissatisfied['readmitted_30days'].mean() * 100 if len(dissatisfied) > 0 else 0
            }
        
        return analysis
    
    @staticmethod
    def quality_indicators_dashboard(df: pd.DataFrame) -> dict:
        """
        Comprehensive dashboard of quality indicators
        """
        indicators = {}
        
        # Patient Safety
        if 'adverse_event' in df.columns:
            indicators['patient_safety'] = {
                'adverse_event_rate': df['adverse_event'].mean() * 100,
                'events_count': df['adverse_event'].sum()
            }
        
        if 'mortality_flag' in df.columns:
            indicators['mortality'] = {
                'mortality_rate': df['mortality_flag'].mean() * 100,
                'mortality_count': df['mortality_flag'].sum()
            }
        
        # Care Quality
        if 'readmitted_30days' in df.columns:
            indicators['care_quality'] = {
                'readmission_rate': df['readmitted_30days'].mean() * 100,
                'readmission_count': df['readmitted_30days'].sum()
            }
        
        if 'los_minutes' in df.columns:
            indicators['efficiency'] = {
                'avg_los_hours': df['los_minutes'].mean() / 60,
                'total_patient_days': df['los_minutes'].sum() / (60 * 24)
            }
        
        if 'wait_time_minutes' in df.columns:
            indicators['access'] = {
                'avg_wait_time': df['wait_time_minutes'].mean(),
                'patients_wait_over_60min': (df['wait_time_minutes'] > 60).sum()
            }
        
        # Patient Experience
        if 'patient_satisfaction' in df.columns:
            indicators['patient_experience'] = {
                'avg_satisfaction': df['patient_satisfaction'].mean(),
                'very_satisfied_pct': (df['patient_satisfaction'] >= 8).sum() / len(df) * 100
            }
        
        return indicators
    
    @staticmethod
    def risk_stratification(df: pd.DataFrame) -> pd.DataFrame:
        """
        Stratify patients by risk factors
        """
        df = df.copy()
        
        risk_score = 0
        
        # Age risk
        if 'age_group' in df.columns:
            age_risk = df['age_group'].map({'0-18': 0, '19-45': 0, '46-65': 1, '65+': 2})
            df['age_risk'] = age_risk
            risk_score += age_risk
        
        # Severity risk
        if 'severity_score' in df.columns:
            df['severity_risk'] = (df['severity_score'] - 1) / 4 * 3  # Normalize to 0-3
            risk_score += df['severity_risk']
        
        # Comorbidity risk
        if 'comorbidity_count' in df.columns:
            df['comorbidity_risk'] = df['comorbidity_count'].clip(0, 5) / 5 * 2  # Normalize to 0-2
            risk_score += df['comorbidity_risk']
        
        # Create risk categories
        df['risk_category'] = pd.cut(risk_score, bins=[0, 2, 4, 6, float('inf')], 
                                      labels=['Low', 'Medium', 'High', 'Critical'])
        
        return df[['patient_id', 'department', 'age_risk', 'severity_risk', 'comorbidity_risk', 'risk_category']]
    
    @staticmethod
    def outcome_by_risk_group(df: pd.DataFrame) -> dict:
        """
        Analyze outcomes stratified by risk groups
        """
        df = df.copy()
        
        # Add risk stratification
        risk_df = ClinicalQualityMetrics.risk_stratification(df)
        df = df.join(risk_df[['risk_category']])
        
        if 'risk_category' not in df.columns:
            return None
        
        outcomes = df.groupby('risk_category').agg({
            'patient_id': 'count',
            'patient_satisfaction': 'mean' if 'patient_satisfaction' in df.columns else None,
            'readmitted_30days': 'mean' if 'readmitted_30days' in df.columns else None,
            'adverse_event': 'mean' if 'adverse_event' in df.columns else None,
            'mortality_flag': 'mean' if 'mortality_flag' in df.columns else None,
            'los_minutes': 'mean' if 'los_minutes' in df.columns else None,
            'wait_time_minutes': 'mean' if 'wait_time_minutes' in df.columns else None
        }).round(3)
        
        return outcomes


class ComorbidityAnalysis:
    """Analyze impact of comorbidities on outcomes"""
    
    @staticmethod
    def comorbidity_impact(df: pd.DataFrame) -> dict:
        """
        Analyze how comorbidities affect outcomes
        """
        if 'comorbidity_count' not in df.columns:
            return None
        
        analysis = {}
        
        for col in ['los_minutes', 'readmitted_30days', 'adverse_event', 'mortality_flag', 'patient_satisfaction']:
            if col in df.columns:
                impact = df.groupby('comorbidity_count')[col].agg(['mean', 'std', 'count']).round(2)
                analysis[col] = impact
        
        return analysis
    
    @staticmethod
    def high_risk_patients(df: pd.DataFrame) -> pd.DataFrame:
        """
        Identify high-risk patients with multiple comorbidities
        """
        if 'comorbidity_count' not in df.columns:
            return None
        
        high_risk = df[df['comorbidity_count'] >= 3][
            ['patient_id', 'department', 'comorbidity_count', 'severity_score', 
             'readmitted_30days', 'adverse_event', 'mortality_flag']
        ].copy()
        
        return high_risk.sort_values('comorbidity_count', ascending=False)


class OutcomeTrajectory:
    """Analyze patient outcome trajectories"""
    
    @staticmethod
    def severity_vs_outcome(df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze relationship between severity score and outcomes
        """
        if 'severity_score' not in df.columns:
            return None
        
        trajectory = df.groupby('severity_score').agg({
            'patient_id': 'count',
            'los_minutes': 'mean' if 'los_minutes' in df.columns else None,
            'wait_time_minutes': 'mean' if 'wait_time_minutes' in df.columns else None,
            'patient_satisfaction': 'mean' if 'patient_satisfaction' in df.columns else None,
            'readmitted_30days': 'mean' if 'readmitted_30days' in df.columns else None,
            'adverse_event': 'mean' if 'adverse_event' in df.columns else None,
            'mortality_flag': 'mean' if 'mortality_flag' in df.columns else None,
            'total_cost': 'mean' if 'total_cost' in df.columns else None
        }).round(3)
        
        return trajectory
    
    @staticmethod
    def department_quality_scorecard(df: pd.DataFrame) -> pd.DataFrame:
        """
        Create quality scorecard for each department
        """
        if 'department' not in df.columns:
            return None
        
        scorecard = df.groupby('department').agg({
            'patient_id': 'count',
            'patient_satisfaction': 'mean' if 'patient_satisfaction' in df.columns else None,
            'readmitted_30days': 'mean' if 'readmitted_30days' in df.columns else None,
            'adverse_event': 'mean' if 'adverse_event' in df.columns else None,
            'mortality_flag': 'mean' if 'mortality_flag' in df.columns else None,
            'los_minutes': 'mean' if 'los_minutes' in df.columns else None,
            'wait_time_minutes': 'mean' if 'wait_time_minutes' in df.columns else None
        }).round(3)
        
        scorecard.columns = ['visits', 'satisfaction', 'readmit_rate', 'adverse_event_rate', 'mortality_rate', 'avg_los', 'avg_wait']
        
        return scorecard
