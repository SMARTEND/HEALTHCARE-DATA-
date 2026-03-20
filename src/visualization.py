"""
Advanced Visualization and Reporting Module
Interactive charts and statistical analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

class AdvancedVisualizer:
    """Create advanced interactive visualizations"""
    
    def __init__(self, style: str = 'seaborn-v0_8-darkgrid'):
        plt.style.use(style)
        sns.set_palette("husl")
    
    def create_kpi_distribution(self, df: pd.DataFrame, metric: str, output_path: str = None):
        """Create distribution plot for KPI"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f'{metric.replace("_", " ").title()} Distribution Analysis', fontsize=16)
        
        # Histogram
        axes[0, 0].hist(df[metric], bins=50, edgecolor='black', alpha=0.7)
        axes[0, 0].set_title('Distribution')
        axes[0, 0].set_xlabel(metric)
        axes[0, 0].set_ylabel('Frequency')
        
        # Box plot
        axes[0, 1].boxplot(df[metric])
        axes[0, 1].set_title('Box Plot')
        axes[0, 1].set_ylabel(metric)
        
        # Q-Q plot
        from scipy import stats
        stats.probplot(df[metric], dist="norm", plot=axes[1, 0])
        axes[1, 0].set_title('Q-Q Plot')
        
        # KDE plot
        df[metric].plot(kind='density', ax=axes[1, 1])
        axes[1, 1].set_title('Density Plot')
        axes[1, 1].set_xlabel(metric)
        
        plt.tight_layout()
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
        return fig
    
    def create_department_comparison(self, df: pd.DataFrame, metric: str, output_path: str = None):
        """Create interactive department comparison"""
        dept_stats = df.groupby('department')[metric].agg(['mean', 'std', 'count'])
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=dept_stats.index,
            y=dept_stats['mean'],
            error_y=dict(type='data', array=dept_stats['std']),
            name='Average',
            marker_color='indianred'
        ))
        
        fig.update_layout(
            title=f'Department Comparison: {metric.replace("_", " ").title()}',
            xaxis_title='Department',
            yaxis_title=metric,
            hovermode='x unified',
            height=500
        )
        
        if output_path:
            fig.write_html(output_path)
        return fig
    
    def create_trend_analysis(self, df: pd.DataFrame, metric: str, output_path: str = None):
        """Create trend analysis with rolling average"""
        if 'visit_date' not in df.columns:
            return None
        
        df = df.copy()
        df['visit_date'] = pd.to_datetime(df['visit_date'])
        daily_avg = df.groupby(df['visit_date'].dt.date)[metric].mean()
        rolling_avg = daily_avg.rolling(window=7).mean()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_avg.index, y=daily_avg.values,
            mode='markers', name='Daily Average',
            marker=dict(size=4, opacity=0.5)
        ))
        fig.add_trace(go.Scatter(
            x=rolling_avg.index, y=rolling_avg.values,
            mode='lines', name='7-Day Rolling Average',
            line=dict(width=3, color='red')
        ))
        
        fig.update_layout(
            title=f'{metric.replace("_", " ").title()} Trend Analysis',
            xaxis_title='Date',
            yaxis_title=metric,
            hovermode='x unified',
            height=500
        )
        
        if output_path:
            fig.write_html(output_path)
        return fig
    
    def create_correlation_heatmap(self, df: pd.DataFrame, output_path: str = None):
        """Create correlation heatmap"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        corr_matrix = df[numeric_cols].corr()
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f')
        plt.title('KPI Correlation Matrix')
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
        return plt.gcf()


class StatisticalAnalysis:
    """Perform advanced statistical analysis"""
    
    @staticmethod
    def anomaly_detection(df: pd.DataFrame, metric: str, threshold: float = 3.0):
        """Detect outliers using Z-score"""
        from scipy import stats
        z_scores = np.abs(stats.zscore(df[metric].dropna()))
        anomalies = df[z_scores > threshold]
        return anomalies, z_scores
    
    @staticmethod
    def forecasting(df: pd.DataFrame, metric: str, periods: int = 30):
        """Simple exponential smoothing forecast"""
        from scipy.optimize import minimize
        
        if 'visit_date' not in df.columns:
            return None
        
        df = df.copy()
        df['visit_date'] = pd.to_datetime(df['visit_date'])
        daily_series = df.groupby(df['visit_date'].dt.date)[metric].mean()
        
        # Exponential smoothing
        alpha = 0.3
        forecasts = [daily_series.iloc[0]]
        
        for i in range(1, len(daily_series)):
            forecast = alpha * daily_series.iloc[i-1] + (1 - alpha) * forecasts[-1]
            forecasts.append(forecast)
        
        # Project forward
        last_value = forecasts[-1]
        for i in range(periods):
            last_value = alpha * daily_series.iloc[-1] + (1 - alpha) * last_value
            forecasts.append(last_value)
        
        return pd.Series(forecasts, index=range(len(forecasts)))
