"""
Healthcare Analytics Package
Advanced analytics for healthcare operational performance analysis
"""

__version__ = '3.0.0'
__author__ = 'Mohammad Alshehri'

from .analytics import HealthcareDataLoader, KPICalculator
from .visualization import AdvancedVisualizer, StatisticalAnalysis
from .machine_learning import (
    SeasonalityAnalyzer,
    WaitTimeForecaster,
    LOSForecaster,
    ReferralDelayPredictor,
    PatientDemandForecaster
)
from .financial_analytics import (
    FinancialAnalytics,
    BreakEvenAnalysis,
    ProfitabilityAnalysis
)
from .clinical_quality import (
    ClinicalQualityMetrics,
    ComorbidityAnalysis,
    OutcomeTrajectory
)
from .etl_pipeline import (
    ETLPipeline,
    DataValidator,
    DataTransformer
)
from .reporting import (
    ReportGenerator,
    ReportTemplate,
    ReportScheduler
)
from .scheduler import (
    SchedulerManager,
    JobDefinitions
)

__all__ = [
    # Core Analytics
    'HealthcareDataLoader',
    'KPICalculator',
    
    # Visualization
    'AdvancedVisualizer',
    'StatisticalAnalysis',
    
    # Machine Learning
    'SeasonalityAnalyzer',
    'WaitTimeForecaster',
    'LOSForecaster',
    'ReferralDelayPredictor',
    'PatientDemandForecaster',
    
    # Financial
    'FinancialAnalytics',
    'BreakEvenAnalysis',
    'ProfitabilityAnalysis',
    
    # Clinical Quality
    'ClinicalQualityMetrics',
    'ComorbidityAnalysis',
    'OutcomeTrajectory',
    
    # ETL & Data Processing
    'ETLPipeline',
    'DataValidator',
    'DataTransformer',
    
    # Reporting
    'ReportGenerator',
    'ReportTemplate',
    'ReportScheduler',
    
    # Automation & Scheduling
    'SchedulerManager',
    'JobDefinitions'
]
