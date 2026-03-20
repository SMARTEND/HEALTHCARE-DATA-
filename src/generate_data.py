"""
Generate synthetic healthcare data for testing and development
Includes operational, financial, and clinical metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

def generate_sample_data(num_records: int = 5000, output_path: str = None, expanded: bool = True):
    """
    Generate synthetic healthcare patient visit data
    
    Parameters:
    - num_records: Number of patient visits to generate
    - output_path: Where to save the CSV file
    - expanded: Include extended metrics (cost, satisfaction, clinical, etc.)
    """
    
    np.random.seed(42)
    
    # Departments
    departments = ['ED', 'IM', 'OBGYN', 'OPD', 'PED', 'SURG']
    
    # Date range
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)
    
    # Base data
    data = {
        'patient_id': [f'P{i:05d}' for i in range(num_records)],
        'department': np.random.choice(departments, num_records),
        'visit_date': [start_date + timedelta(days=np.random.randint(0, 365)) 
                       for _ in range(num_records)],
        'wait_time_minutes': np.random.normal(40, 15, num_records).astype(int),
        'los_minutes': np.random.normal(181, 80, num_records).astype(int),
        'referral_delay_days': np.random.normal(4.5, 2.5, num_records).astype(int),
        'age_group': np.random.choice(['0-18', '19-45', '46-65', '65+'], num_records),
        'visit_outcome': np.random.choice(['Discharged', 'Admitted', 'Transferred'], num_records)
    }
    
    # Ensure non-negative values
    data['wait_time_minutes'] = np.maximum(data['wait_time_minutes'], 5)
    data['los_minutes'] = np.maximum(data['los_minutes'], 30)
    data['referral_delay_days'] = np.maximum(data['referral_delay_days'], 0)
    
    # Extended metrics
    if expanded:
        # Patient demographics and clinical
        data['gender'] = np.random.choice(['M', 'F'], num_records)
        data['comorbidity_count'] = np.random.poisson(1.5, num_records)  # 0-5 comorbidities
        data['severity_score'] = np.random.normal(3, 1, num_records).clip(1, 5).astype(int)  # 1-5
        
        # Patient satisfaction (1-10 scale)
        # Lower scores for high wait times and long LOS
        base_satisfaction = 8 - (data['wait_time_minutes'].astype(float) / 50)
        data['patient_satisfaction'] = (base_satisfaction + np.random.normal(0, 0.5, num_records)).clip(1, 10).round(1)
        
        # Clinical outcomes
        data['readmitted_30days'] = np.random.binomial(1, 0.08, num_records)  # 8% readmission rate
        data['adverse_event'] = np.random.binomial(1, 0.02, num_records)  # 2% adverse events
        data['mortality_flag'] = np.random.binomial(1, 0.01, num_records)  # 1% mortality
        
        # Insurance and demographics
        data['insurance_type'] = np.random.choice(['Medicare', 'Medicaid', 'Private', 'Uninsured'], num_records, p=[0.35, 0.25, 0.35, 0.05])
        
        # Cost metrics (realistic ranges by department)
        dept_cost_multiplier = {
            'ED': 1.0,
            'IM': 1.2,
            'OBGYN': 1.8,
            'OPD': 0.6,
            'PED': 1.0,
            'SURG': 3.5
        }
        
        base_cost = np.random.normal(3000, 1000, num_records)
        data['direct_cost'] = np.array([
            base_cost[i] * dept_cost_multiplier.get(dept, 1.0) * (1 + data['los_minutes'][i]/200)
            for i, dept in enumerate(data['department'])
        ]).clip(500, 50000)
        
        # Add in-hospital costs (supplies, medications)
        data['supply_cost'] = (data['los_minutes'] / 60) * np.random.normal(50, 20, num_records).clip(10, 500)
        data['lab_cost'] = np.random.uniform(0, 2000, num_records)
        data['imaging_cost'] = np.random.uniform(0, 3000, num_records)
        data['pharmacy_cost'] = (data['los_minutes'] / 60) * np.random.normal(30, 15, num_records).clip(0, 500)
        
        # Total cost
        data['total_cost'] = (data['direct_cost'] + data['supply_cost'] + 
                             data['lab_cost'] + data['imaging_cost'] + 
                             data['pharmacy_cost'])
        
        # Revenue (based on insurance type and severity)
        insurance_reimbursement = {
            'Medicare': 0.65,
            'Medicaid': 0.55,
            'Private': 0.95,
            'Uninsured': 0.10
        }
        
        data['revenue'] = np.array([
            data['total_cost'][i] * insurance_reimbursement.get(ins_type, 0.7) * (1 + data['severity_score'][i]/10)
            for i, ins_type in enumerate(data['insurance_type'])
        ])
        
        # Profit margin
        data['profit_margin'] = data['revenue'] - data['total_cost']
        
        # Resource utilization
        data['bed_hours'] = data['los_minutes'] / 60
        data['nurse_hours'] = (data['los_minutes'] / 60) * np.random.normal(0.5, 0.1, num_records).clip(0.2, 2)
        data['physician_hours'] = (data['los_minutes'] / 60) * np.random.normal(0.2, 0.05, num_records).clip(0.05, 1)
        
        # Equipment and procedure flags
        data['icu_admission'] = (data['severity_score'] > 3).astype(int) * np.random.binomial(1, 0.6, num_records)
        data['surgery_performed'] = ((data['department'] == 'SURG') * np.random.binomial(1, 0.8, num_records)).astype(int)
        data['ct_scan'] = np.random.binomial(1, 0.15, num_records)
        data['mri_scan'] = np.random.binomial(1, 0.08, num_records)
        data['blood_transfusion'] = np.random.binomial(1, 0.05, num_records)
        
        # Staff allocation
        data['attending_physician_id'] = np.random.randint(1, 31, num_records)  # 30 physicians
        data['nurse_id'] = np.random.randint(1, 101, num_records)  # 100 nurses
        
        # Operational flags
        data['handoff_count'] = np.random.poisson(2, num_records)  # inter-department transitions
        data['delay_reason'] = np.random.choice(
            ['None', 'Equipment', 'Staff', 'Lab_Result', 'Specialist', 'Bed_Availability'],
            num_records,
            p=[0.6, 0.1, 0.1, 0.1, 0.05, 0.05]
        )
    
    df = pd.DataFrame(data)
    
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Sample data generated: {output_path}")
        print(f"Records: {len(df)}")
        print(f"Columns: {len(df.columns)}")
        if expanded:
            print(f"Extended metrics included: Cost, Satisfaction, Clinical, Infrastructure")
    
    return df


if __name__ == '__main__':
    output_path = Path(__file__).parent.parent / 'data' / 'patient_visits.csv'
    df = generate_sample_data(5000, output_path, expanded=True)
    print(f"\nGenerated {len(df)} records")
    print(f"\nData shape: {df.shape}")
    print(f"\nColumns ({len(df.columns)}):")
    for col in df.columns:
        print(f"  • {col}")
    print(f"\nFirst few records:")
    print(df.head())
    print(f"\nData summary:")
    print(df.describe())
