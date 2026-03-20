"""
Financial and Cost Analysis Module
Healthcare Economics and ROI Analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime


class FinancialAnalytics:
    """Analyze healthcare financial metrics and economics"""
    
    @staticmethod
    def cost_analysis(df: pd.DataFrame, by_department: bool = True) -> pd.DataFrame:
        """
        Analyze costs by department or overall
        
        Returns:
        - DataFrame with cost statistics
        """
        if 'total_cost' not in df.columns:
            return None
        
        if by_department and 'department' in df.columns:
            analysis = df.groupby('department').agg({
                'total_cost': ['count', 'sum', 'mean', 'median', 'std', 'min', 'max'],
                'direct_cost': 'mean',
                'supply_cost': 'mean',
                'lab_cost': 'mean',
                'imaging_cost': 'mean',
                'pharmacy_cost': 'mean'
            }).round(2)
            return analysis
        else:
            return {
                'total_visits': len(df),
                'total_cost_sum': df['total_cost'].sum(),
                'avg_cost': df['total_cost'].mean(),
                'median_cost': df['total_cost'].median(),
                'cost_std': df['total_cost'].std(),
                'min_cost': df['total_cost'].min(),
                'max_cost': df['total_cost'].max()
            }
    
    @staticmethod
    def revenue_analysis(df: pd.DataFrame) -> dict:
        """Analyze revenue by insurance type and outcomes"""
        if 'revenue' not in df.columns:
            return None
        
        analysis = {
            'total_revenue': df['revenue'].sum(),
            'avg_revenue_per_visit': df['revenue'].mean(),
            'total_cost': df['total_cost'].sum() if 'total_cost' in df.columns else 0,
            'total_profit': (df['revenue'].sum() - df['total_cost'].sum()) if 'total_cost' in df.columns else 0,
            'profit_margin': ((df['revenue'].sum() - df['total_cost'].sum()) / df['revenue'].sum() * 100) if 'total_cost' in df.columns else 0
        }
        
        # By insurance type
        if 'insurance_type' in df.columns:
            insurance_analysis = df.groupby('insurance_type').agg({
                'revenue': ['count', 'sum', 'mean'],
                'total_cost': 'mean' if 'total_cost' in df.columns else None,
                'profit_margin': 'mean' if 'profit_margin' in df.columns else None
            }).round(2)
            analysis['by_insurance'] = insurance_analysis
        
        return analysis
    
    @staticmethod
    def roi_by_intervention(df: pd.DataFrame) -> dict:
        """Calculate ROI for different interventions/procedures"""
        roi_analysis = {}
        
        # ICU admission ROI
        if 'icu_admission' in df.columns:
            icu_patients = df[df['icu_admission'] == 1]
            non_icu = df[df['icu_admission'] == 0]
            
            if len(icu_patients) > 0:
                roi_analysis['icu_admission'] = {
                    'avg_los_icu': icu_patients['los_minutes'].mean() if 'los_minutes' in icu_patients.columns else 0,
                    'avg_los_non_icu': non_icu['los_minutes'].mean() if 'los_minutes' in non_icu.columns else 0,
                    'avg_cost_icu': icu_patients['total_cost'].mean() if 'total_cost' in icu_patients.columns else 0,
                    'avg_cost_non_icu': non_icu['total_cost'].mean() if 'total_cost' in non_icu.columns else 0,
                    'readmit_rate_icu': icu_patients['readmitted_30days'].mean() if 'readmitted_30days' in icu_patients.columns else 0,
                    'readmit_rate_non_icu': non_icu['readmitted_30days'].mean() if 'readmitted_30days' in non_icu.columns else 0
                }
        
        # Surgery ROI
        if 'surgery_performed' in df.columns:
            surgery = df[df['surgery_performed'] == 1]
            non_surgery = df[df['surgery_performed'] == 0]
            
            if len(surgery) > 0:
                roi_analysis['surgery'] = {
                    'count': len(surgery),
                    'avg_cost': surgery['total_cost'].mean() if 'total_cost' in surgery.columns else 0,
                    'avg_los': surgery['los_minutes'].mean() if 'los_minutes' in surgery.columns else 0,
                    'readmit_rate': surgery['readmitted_30days'].mean() if 'readmitted_30days' in surgery.columns else 0,
                    'satisfaction': surgery['patient_satisfaction'].mean() if 'patient_satisfaction' in surgery.columns else 0
                }
        
        # Imaging ROI
        if 'ct_scan' in df.columns and 'mri_scan' in df.columns:
            imaging = df[(df['ct_scan'] == 1) | (df['mri_scan'] == 1)]
            roi_analysis['imaging_procedures'] = {
                'ct_scans': df['ct_scan'].sum(),
                'mri_scans': df['mri_scan'].sum(),
                'avg_imaging_cost': imaging['imaging_cost'].mean() if 'imaging_cost' in imaging.columns and len(imaging) > 0 else 0,
                'total_imaging_cost': imaging['imaging_cost'].sum() if 'imaging_cost' in imaging.columns and len(imaging) > 0 else 0
            }
        
        return roi_analysis
    
    @staticmethod
    def cost_effectiveness(df: pd.DataFrame, metric: str = 'patient_satisfaction') -> dict:
        """
        Analyze cost-effectiveness of interventions
        
        Parameters:
        - metric: Outcome variable (satisfaction, readmission rate, etc.)
        """
        if 'total_cost' not in df.columns or metric not in df.columns:
            return None
        
        # Quartile analysis
        df = df.copy()
        df['cost_quartile'] = pd.qcut(df['total_cost'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
        
        effectiveness = df.groupby('cost_quartile').agg({
            'total_cost': 'mean',
            metric: ['mean', 'std'],
            'los_minutes': 'mean' if 'los_minutes' in df.columns else None,
            'wait_time_minutes': 'mean' if 'wait_time_minutes' in df.columns else None
        }).round(2)
        
        return effectiveness
    
    @staticmethod
    def resource_utilization(df: pd.DataFrame) -> dict:
        """
        Analyze resource utilization (beds, staff, equipment)
        """
        utilization = {}
        
        # Bed utilization
        if 'bed_hours' in df.columns:
            utilization['beds'] = {
                'total_hours': df['bed_hours'].sum(),
                'avg_hours_per_visit': df['bed_hours'].mean(),
                'occupancy_value': df['bed_hours'].sum()  # Can compare to available bed-hours
            }
        
        # Nursing hours
        if 'nurse_hours' in df.columns:
            utilization['nursing'] = {
                'total_hours': df['nurse_hours'].sum(),
                'avg_hours_per_visit': df['nurse_hours'].mean(),
                'cost_per_hour': 45  # Assumption
            }
        
        # Physician hours
        if 'physician_hours' in df.columns:
            utilization['physicians'] = {
                'total_hours': df['physician_hours'].sum(),
                'avg_hours_per_visit': df['physician_hours'].mean(),
                'cost_per_hour': 125  # Assumption
            }
        
        # Equipment usage
        equipment_cols = ['ct_scan', 'mri_scan', 'blood_transfusion', 'icu_admission']
        equipment_usage = {}
        for col in equipment_cols:
            if col in df.columns:
                equipment_usage[col] = df[col].sum()
        
        if equipment_usage:
            utilization['equipment'] = equipment_usage
        
        return utilization
    
    @staticmethod
    def financial_summary_by_insurance(df: pd.DataFrame) -> pd.DataFrame:
        """
        Detailed financial summary by insurance type
        """
        if 'insurance_type' not in df.columns:
            return None
        
        summary = df.groupby('insurance_type').agg({
            'patient_id': 'count',
            'total_cost': ['sum', 'mean', 'std'],
            'revenue': ['sum', 'mean'],
            'profit_margin': ['mean', 'sum'],
            'los_minutes': 'mean' if 'los_minutes' in df.columns else None,
            'readmitted_30days': 'sum' if 'readmitted_30days' in df.columns else None,
            'patient_satisfaction': 'mean' if 'patient_satisfaction' in df.columns else None
        }).round(2)
        
        summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
        return summary
    
    @staticmethod
    def cost_drivers_analysis(df: pd.DataFrame) -> dict:
        """
        Identify main cost drivers
        """
        cost_cols = ['direct_cost', 'supply_cost', 'lab_cost', 'imaging_cost', 'pharmacy_cost']
        available_cols = [col for col in cost_cols if col in df.columns]
        
        if not available_cols:
            return None
        
        total_by_type = {}
        for col in available_cols:
            total_by_type[col] = df[col].sum()
        
        total_cost_all = sum(total_by_type.values())
        
        percentages = {
            col: (total_by_type[col] / total_cost_all * 100) if total_cost_all > 0 else 0
            for col in total_by_type
        }
        
        return {
            'totals': total_by_type,
            'percentages': percentages,
            'top_driver': max(percentages, key=percentages.get) if percentages else None
        }


class BreakEvenAnalysis:
    """Break-even and volume analysis"""
    
    @staticmethod
    def calculate_breakeven_volume(fixed_costs: float, contribution_per_visit: float) -> float:
        """
        Calculate break-even volume
        
        fixed_costs: Monthly overhead (e.g., $500,000)
        contribution_per_visit: Revenue - Variable costs per visit
        """
        if contribution_per_visit <= 0:
            return float('inf')
        
        return fixed_costs / contribution_per_visit
    
    @staticmethod
    def sensitivity_analysis(df: pd.DataFrame, variable: str, change_percent: float = 10.0) -> dict:
        """
        Sensitivity analysis: how does 10% change in variable affect profit?
        
        Parameters:
        - variable: Column name to vary (e.g., 'total_cost', 'los_minutes')
        - change_percent: Percent change to simulate
        """
        if variable not in df.columns:
            return None
        
        base_profit = (df['revenue'].sum() - df['total_cost'].sum()) if 'revenue' in df.columns and 'total_cost' in df.columns else 0
        
        # Simulate increase
        df_increase = df.copy()
        df_increase[variable] = df_increase[variable] * (1 + change_percent/100)
        new_profit_increase = (df_increase['revenue'].sum() - df_increase['total_cost'].sum()) if 'revenue' in df_increase.columns and 'total_cost' in df_increase.columns else 0
        
        # Simulate decrease
        df_decrease = df.copy()
        df_decrease[variable] = df_decrease[variable] * (1 - change_percent/100)
        new_profit_decrease = (df_decrease['revenue'].sum() - df_decrease['total_cost'].sum()) if 'revenue' in df_decrease.columns and 'total_cost' in df_decrease.columns else 0
        
        return {
            'base_profit': base_profit,
            'profit_if_increase_%': new_profit_increase,
            'profit_if_decrease_%': new_profit_decrease,
            'impact_increase': new_profit_increase - base_profit,
            'impact_decrease': new_profit_decrease - base_profit,
            'elasticity': ((new_profit_increase - base_profit) / base_profit * 100 / change_percent) if base_profit != 0 else 0
        }


class ProfitabilityAnalysis:
    """Department and visit profitability analysis"""
    
    @staticmethod
    def department_profitability(df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze profitability by department
        """
        if 'department' not in df.columns or 'revenue' not in df.columns:
            return None
        
        profitability = df.groupby('department').agg({
            'patient_id': 'count',
            'revenue': ['sum', 'mean'],
            'total_cost': ['sum', 'mean'] if 'total_cost' in df.columns else None,
            'profit_margin': ['sum', 'mean', 'min', 'max'] if 'profit_margin' in df.columns else None,
            'los_minutes': 'mean' if 'los_minutes' in df.columns else None
        }).round(2)
        
        profitability.columns = ['_'.join(col).strip() for col in profitability.columns.values]
        return profitability
    
    @staticmethod
    def identify_unprofitable_cases(df: pd.DataFrame, threshold_percentile: float = 25.0) -> pd.DataFrame:
        """
        Identify cases in bottom X percentile of profitability
        """
        if 'profit_margin' not in df.columns:
            return None
        
        threshold = df['profit_margin'].quantile(threshold_percentile / 100)
        unprofitable = df[df['profit_margin'] < threshold].copy()
        
        return unprofitable.sort_values('profit_margin')[
            ['patient_id', 'department', 'total_cost', 'revenue', 'profit_margin', 'los_minutes']
        ]
    
    @staticmethod
    def case_mix_analysis(df: pd.DataFrame) -> dict:
        """
        Analyze case mix (severity distribution) and profitability
        """
        if 'severity_score' not in df.columns:
            return None
        
        analysis = df.groupby('severity_score').agg({
            'patient_id': 'count',
            'total_cost': 'mean' if 'total_cost' in df.columns else None,
            'revenue': 'mean' if 'revenue' in df.columns else None,
            'profit_margin': 'mean' if 'profit_margin' in df.columns else None,
            'los_minutes': 'mean' if 'los_minutes' in df.columns else None,
            'patient_satisfaction': 'mean' if 'patient_satisfaction' in df.columns else None
        }).round(2)
        
        return analysis
