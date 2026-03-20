"""
Automated Reporting System
Generate dynamic HTML/PDF reports using Jinja2 templates
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import logging
from jinja2 import Environment, FileSystemLoader, Template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportTemplate:
    """Template management for reports"""
    
    @staticmethod
    def create_html_template() -> str:
        """Create default HTML report template"""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ report_title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            color: #333;
            background-color: #f5f5f5;
        }
        .header {
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .header h1 {
            margin: 0;
        }
        .meta {
            font-size: 12px;
            opacity: 0.9;
        }
        .section {
            background-color: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        table th {
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
        }
        table td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }
        table tr:hover {
            background-color: #f9f9f9;
        }
        .metric {
            display: inline-block;
            background: linear-gradient(135deg, #3498db, #2c3e50);
            color: white;
            padding: 20px;
            margin: 10px;
            border-radius: 5px;
            min-width: 200px;
            text-align: center;
        }
        .metric-label {
            font-size: 12px;
            opacity: 0.9;
        }
        .metric-value {
            font-size: 28px;
            font-weight: bold;
            margin: 10px 0;
        }
        .status-pass {
            color: #27ae60;
            font-weight: bold;
        }
        .status-fail {
            color: #e74c3c;
            font-weight: bold;
        }
        .alert {
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 12px;
            margin: 10px 0;
        }
        .footer {
            text-align: center;
            color: #7f8c8d;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #bdc3c7;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ report_title }}</h1>
        <div class="meta">
            Generated: {{ generated_date }}<br>
            Report Period: {{ period_start }} to {{ period_end }}
        </div>
    </div>

    {% if executive_summary %}
    <div class="section">
        <h2>Executive Summary</h2>
        {% for key, value in executive_summary.items() %}
        <div class="metric">
            <div class="metric-label">{{ key }}</div>
            <div class="metric-value">{{ "%.2f"|format(value) if value is number else value }}</div>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if kpi_summary %}
    <div class="section">
        <h2>Key Performance Indicators</h2>
        <table>
            <tr>
                <th>KPI</th>
                <th>Value</th>
                <th>Status</th>
                <th>Target</th>
            </tr>
            {% for kpi in kpi_summary %}
            <tr>
                <td>{{ kpi.name }}</td>
                <td>{{ "%.2f"|format(kpi.value) if kpi.value is number else kpi.value }}</td>
                <td><span class="status-{{ kpi.status.lower() }}">{{ kpi.status }}</span></td>
                <td>{{ "%.2f"|format(kpi.target) if kpi.target is number else kpi.target }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endif %}

    {% if department_performance %}
    <div class="section">
        <h2>Department Performance</h2>
        <table>
            <tr>
                <th>Department</th>
                <th>Patient Count</th>
                <th>Avg Wait Time (min)</th>
                <th>Avg LOS (min)</th>
                <th>Satisfaction</th>
            </tr>
            {% for dept in department_performance %}
            <tr>
                <td>{{ dept.department }}</td>
                <td>{{ dept.patient_count }}</td>
                <td>{{ "%.1f"|format(dept.avg_wait_time) }}</td>
                <td>{{ "%.1f"|format(dept.avg_los) }}</td>
                <td>{{ "%.1f"|format(dept.satisfaction) }}/10</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endif %}

    {% if financial_summary %}
    <div class="section">
        <h2>Financial Summary</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            {% for key, value in financial_summary.items() %}
            <tr>
                <td>{{ key }}</td>
                <td>${{ "%.2f"|format(value) if value is number else value }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endif %}

    {% if quality_metrics %}
    <div class="section">
        <h2>Quality Metrics</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value (%)</th>
                <th>Status</th>
            </tr>
            {% for metric in quality_metrics %}
            <tr>
                <td>{{ metric.name }}</td>
                <td>{{ "%.2f"|format(metric.value) }}</td>
                <td><span class="status-{{ metric.status.lower() }}">{{ metric.status }}</span></td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endif %}

    {% if alerts %}
    <div class="section">
        <h2>Alerts & Warnings</h2>
        {% for alert in alerts %}
        <div class="alert">
            <strong>{{ alert.type }}:</strong> {{ alert.message }}
        </div>
        {% endfor %}
    </div>
    {% endif %}

    <div class="footer">
        <p>This report was automatically generated. For questions, contact the Analytics Team.</p>
    </div>
</body>
</html>
"""
    
    @staticmethod
    def create_summary_template() -> str:
        """Create summary email template"""
        return """
Healthcare Analytics - Daily Summary Report
{% if generated_date %}Generated: {{ generated_date }}{% endif %}

---EXECUTIVE SUMMARY---
{% if executive_summary %}
{% for key, value in executive_summary.items() %}
{{ key }}: {{ "%.2f"|format(value) if value is number else value }}
{% endfor %}
{% endif %}

---KEY METRICS---
{% if kpi_summary %}
{% for kpi in kpi_summary %}
{{ kpi.name }}: {{ "%.2f"|format(kpi.value) if kpi.value is number else kpi.value }} (Target: {{ kpi.target }}, Status: {{ kpi.status }})
{% endfor %}
{% endif %}

---ALERTS---
{% if alerts %}
{% for alert in alerts %}
[{{ alert.type }}] {{ alert.message }}
{% endfor %}
{% else %}
No critical alerts.
{% endif %}

---DEPARTMENT PERFORMANCE---
{% if department_performance %}
{% for dept in department_performance %}
{{ dept.department }}: {{ dept.patient_count }} patients, Avg Wait: {{ "%.1f"|format(dept.avg_wait_time) }}min, Satisfaction: {{ "%.1f"|format(dept.satisfaction) }}/10
{% endfor %}
{% endif %}
"""


class ReportGenerator:
    """Generate analytics reports with data"""
    
    def __init__(self):
        self.template = ReportTemplate()
    
    def generate_from_dataframe(self, df: pd.DataFrame, report_title: str, 
                               period_start: str = None, period_end: str = None) -> Dict:
        """Generate report data from analytics dataframe"""
        
        # Executive summary metrics
        executive_summary = {
            'Total Visits': len(df),
            'Unique Patients': df['patient_id'].nunique() if 'patient_id' in df.columns else 0,
            'Avg Wait Time (min)': df['wait_time_minutes'].mean() if 'wait_time_minutes' in df.columns else 0,
            'Avg LOS (min)': df['los_minutes'].mean() if 'los_minutes' in df.columns else 0,
        }
        
        # KPI summary
        kpi_summary = []
        
        if 'wait_time_minutes' in df.columns:
            avg_wait = df['wait_time_minutes'].mean()
            kpi_summary.append({
                'name': 'Average Wait Time',
                'value': avg_wait,
                'target': 30,
                'status': 'PASS' if avg_wait <= 30 else 'FAIL'
            })
        
        if 'los_minutes' in df.columns:
            avg_los = df['los_minutes'].mean()
            kpi_summary.append({
                'name': 'Average Length of Stay',
                'value': avg_los,
                'target': 240,
                'status': 'PASS' if avg_los <= 240 else 'FAIL'
            })
        
        if 'patient_satisfaction' in df.columns:
            avg_satisfaction = df['patient_satisfaction'].mean()
            kpi_summary.append({
                'name': 'Patient Satisfaction',
                'value': avg_satisfaction,
                'target': 8.0,
                'status': 'PASS' if avg_satisfaction >= 8.0 else 'FAIL'
            })
        
        # Department performance
        department_performance = []
        if 'department' in df.columns:
            for dept in df['department'].unique():
                dept_data = df[df['department'] == dept]
                department_performance.append({
                    'department': dept,
                    'patient_count': len(dept_data),
                    'avg_wait_time': dept_data['wait_time_minutes'].mean() if 'wait_time_minutes' in dept_data.columns else 0,
                    'avg_los': dept_data['los_minutes'].mean() if 'los_minutes' in dept_data.columns else 0,
                    'satisfaction': dept_data['patient_satisfaction'].mean() if 'patient_satisfaction' in dept_data.columns else 0,
                })
        
        # Financial summary
        financial_summary = {}
        if 'total_cost' in df.columns:
            financial_summary['Total Cost'] = df['total_cost'].sum()
        if 'revenue' in df.columns:
            financial_summary['Total Revenue'] = df['revenue'].sum()
            financial_summary['Net Profit'] = df['revenue'].sum() - df['total_cost'].sum() if 'total_cost' in df.columns else 0
        
        # Quality metrics
        quality_metrics = []
        if 'adverse_event' in df.columns:
            adverse_pct = (df['adverse_event'].sum() / len(df)) * 100
            quality_metrics.append({
                'name': 'Adverse Event Rate',
                'value': adverse_pct,
                'status': 'PASS' if adverse_pct < 2.0 else 'FAIL'
            })
        
        if 'readmitted_30days' in df.columns:
            readmit_pct = (df['readmitted_30days'].sum() / len(df)) * 100
            quality_metrics.append({
                'name': '30-Day Readmission Rate',
                'value': readmit_pct,
                'status': 'PASS' if readmit_pct < 8.0 else 'FAIL'
            })
        
        # Generate alerts
        alerts = []
        for kpi in kpi_summary:
            if kpi['status'] == 'FAIL':
                alerts.append({
                    'type': 'WARNING',
                    'message': f"{kpi['name']} is {kpi['value']:.2f}, exceeds target of {kpi['target']}"
                })
        
        if period_start is None:
            period_start = df['visit_date'].min() if 'visit_date' in df.columns else 'Unknown'
        if period_end is None:
            period_end = df['visit_date'].max() if 'visit_date' in df.columns else 'Unknown'
        
        report_data = {
            'report_title': report_title,
            'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'period_start': str(period_start),
            'period_end': str(period_end),
            'executive_summary': executive_summary,
            'kpi_summary': kpi_summary,
            'department_performance': department_performance,
            'financial_summary': financial_summary,
            'quality_metrics': quality_metrics,
            'alerts': alerts
        }
        
        logger.info(f"Generated report data: {len(kpi_summary)} KPIs, {len(alerts)} alerts")
        
        return report_data
    
    def render_html(self, report_data: Dict) -> str:
        """Render HTML report from data"""
        html_template = self.template.create_html_template()
        template = Template(html_template)
        return template.render(**report_data)
    
    def render_summary(self, report_data: Dict) -> str:
        """Render summary text report"""
        summary_template = self.template.create_summary_template()
        template = Template(summary_template)
        return template.render(**report_data)
    
    def save_html_report(self, report_data: Dict, output_path: str) -> bool:
        """Save HTML report to file"""
        try:
            html_content = self.render_html(report_data)
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Saved HTML report: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save HTML report: {str(e)}")
            raise
    
    def save_summary_report(self, report_data: Dict, output_path: str) -> bool:
        """Save summary text report"""
        try:
            summary_content = self.render_summary(report_data)
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            
            logger.info(f"Saved summary report: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save summary report: {str(e)}")
            raise
    
    def save_csv_report(self, report_data: Dict, output_path: str) -> bool:
        """Export report data to CSV"""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create CSV-friendly data
            export_data = {
                'Report Title': [report_data['report_title']],
                'Generated Date': [report_data['generated_date']],
                'Period Start': [report_data['period_start']],
                'Period End': [report_data['period_end']]
            }
            
            df = pd.DataFrame(export_data)
            df.to_csv(output_path, index=False)
            
            logger.info(f"Saved CSV report: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save CSV report: {str(e)}")
            raise


class ReportScheduler:
    """Schedule report generation"""
    
    def __init__(self):
        self.scheduled_reports = {}
    
    def add_scheduled_report(self, report_name: str, schedule_config: Dict) -> None:
        """
        Add report to schedule
        
        Config example:
        {
            'frequency': 'daily',  # or 'weekly', 'monthly'
            'time': '09:00',  # in 24h format
            'data_source': 'path_to_data',
            'output_dir': 'path_to_output',
            'report_type': 'html'
        }
        """
        self.scheduled_reports[report_name] = {
            'config': schedule_config,
            'last_run': None,
            'status': 'SCHEDULED'
        }
        logger.info(f"Added scheduled report: {report_name}")
    
    def get_scheduled_reports(self) -> Dict:
        """Return all scheduled reports"""
        return self.scheduled_reports
    
    def update_report_status(self, report_name: str, status: str, error_msg: str = None) -> None:
        """Update report execution status"""
        if report_name in self.scheduled_reports:
            self.scheduled_reports[report_name]['status'] = status
            self.scheduled_reports[report_name]['last_run'] = datetime.now().isoformat()
            if error_msg:
                self.scheduled_reports[report_name]['last_error'] = error_msg
            logger.info(f"Updated {report_name} status: {status}")
