-- Healthcare Operations Database Schema (EXPANDED)
-- Complete schema for operational, financial, and clinical metrics

CREATE TABLE IF NOT EXISTS departments (
    department_id INT PRIMARY KEY AUTO_INCREMENT,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    department_code VARCHAR(10) NOT NULL,
    bed_count INT,
    annual_budget DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS patient_visits (
    visit_id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id VARCHAR(50) NOT NULL,
    department_id INT NOT NULL,
    visit_date DATE NOT NULL,
    visit_time TIME,
    registration_time DATETIME,
    triage_start_time DATETIME,
    triage_end_time DATETIME,
    wait_time_minutes INT,
    clinical_start_time DATETIME,
    clinical_end_time DATETIME,
    los_minutes INT,
    referral_date DATE,
    referral_delay_days INT,
    visit_outcome VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    INDEX idx_visit_date (visit_date),
    INDEX idx_department_id (department_id),
    INDEX idx_patient_id (patient_id)
);

-- Patient Demographics & Clinical
CREATE TABLE IF NOT EXISTS patient_details (
    detail_id INT PRIMARY KEY AUTO_INCREMENT,
    visit_id INT NOT NULL,
    gender CHAR(1),
    age_group VARCHAR(20),
    comorbidity_count INT,
    severity_score INT CHECK (severity_score >= 1 AND severity_score <= 5),
    insurance_type VARCHAR(50),
    readmitted_30days BOOLEAN DEFAULT FALSE,
    adverse_event BOOLEAN DEFAULT FALSE,
    mortality_flag BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (visit_id) REFERENCES patient_visits(visit_id),
    INDEX idx_severity (severity_score),
    INDEX idx_insurance (insurance_type)
);

-- Financial Metrics
CREATE TABLE IF NOT EXISTS visit_costs (
    cost_id INT PRIMARY KEY AUTO_INCREMENT,
    visit_id INT NOT NULL,
    direct_cost DECIMAL(10, 2),
    supply_cost DECIMAL(10, 2),
    lab_cost DECIMAL(10, 2),
    imaging_cost DECIMAL(10, 2),
    pharmacy_cost DECIMAL(10, 2),
    total_cost DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (visit_id) REFERENCES patient_visits(visit_id),
    INDEX idx_cost (total_cost)
);

CREATE TABLE IF NOT EXISTS visit_revenue (
    revenue_id INT PRIMARY KEY AUTO_INCREMENT,
    visit_id INT NOT NULL,
    insurance_type VARCHAR(50),
    revenue_amount DECIMAL(10, 2),
    profit_margin DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (visit_id) REFERENCES patient_visits(visit_id),
    INDEX idx_revenue (revenue_amount)
);

-- Clinical Quality Metrics
CREATE TABLE IF NOT EXISTS clinical_outcomes (
    outcome_id INT PRIMARY KEY AUTO_INCREMENT,
    visit_id INT NOT NULL,
    patient_satisfaction DECIMAL(3, 1),
    readmission_date DATE,
    adverse_event_description VARCHAR(500),
    mortality_type VARCHAR(50),
    complication_flags VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (visit_id) REFERENCES patient_visits(visit_id),
    INDEX idx_satisfaction (patient_satisfaction)
);

-- Resource Utilization
CREATE TABLE IF NOT EXISTS resource_utilization (
    utilization_id INT PRIMARY KEY AUTO_INCREMENT,
    visit_id INT NOT NULL,
    bed_hours DECIMAL(8, 2),
    nurse_hours DECIMAL(8, 2),
    physician_hours DECIMAL(8, 2),
    attending_physician_id INT,
    nurse_id INT,
    icu_admission BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (visit_id) REFERENCES patient_visits(visit_id),
    INDEX idx_physician (attending_physician_id),
    INDEX idx_nurse (nurse_id)
);

-- Procedures & Interventions
CREATE TABLE IF NOT EXISTS procedures (
    procedure_id INT PRIMARY KEY AUTO_INCREMENT,
    visit_id INT NOT NULL,
    procedure_type VARCHAR(100),
    procedure_code VARCHAR(20),
    surgery_performed BOOLEAN,
    ct_scan BOOLEAN,
    mri_scan BOOLEAN,
    ultrasound BOOLEAN,
    blood_transfusion BOOLEAN,
    procedure_cost DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (visit_id) REFERENCES patient_visits(visit_id),
    INDEX idx_procedure_type (procedure_type)
);

-- KPI Daily Summary
CREATE TABLE IF NOT EXISTS kpi_daily_summary (
    summary_id INT PRIMARY KEY AUTO_INCREMENT,
    summary_date DATE NOT NULL UNIQUE,
    total_visits INT,
    avg_wait_time DECIMAL(10, 2),
    avg_los DECIMAL(10, 2),
    avg_referral_delay DECIMAL(10, 2),
    avg_satisfaction DECIMAL(3, 1),
    readmission_count INT,
    adverse_event_count INT,
    total_cost DECIMAL(15, 2),
    total_revenue DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_summary_date (summary_date)
);

-- Department Performance
CREATE TABLE IF NOT EXISTS department_performance (
    performance_id INT PRIMARY KEY AUTO_INCREMENT,
    performance_date DATE NOT NULL,
    department_id INT NOT NULL,
    total_visits INT,
    avg_wait_time DECIMAL(10, 2),
    avg_los DECIMAL(10, 2),
    patient_satisfaction DECIMAL(3, 2),
    readmission_rate DECIMAL(5, 2),
    adverse_event_rate DECIMAL(5, 2),
    avg_cost DECIMAL(10, 2),
    avg_revenue DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    INDEX idx_performance_date (performance_date),
    INDEX idx_department_id (department_id),
    UNIQUE KEY unique_perf (performance_date, department_id)
);

-- Analytics Views

CREATE VIEW IF NOT EXISTS v_monthly_kpi_summary AS
SELECT 
    DATE_TRUNC('month', pv.visit_date) as month,
    COUNT(pv.visit_id) as total_visits,
    ROUND(AVG(pv.wait_time_minutes), 2) as avg_wait_time,
    ROUND(AVG(pv.los_minutes), 2) as avg_los,
    ROUND(AVG(pv.referral_delay_days), 2) as avg_referral_delay,
    ROUND(SUM(vc.total_cost), 2) as total_cost,
    ROUND(SUM(vr.revenue_amount), 2) as total_revenue,
    ROUND(AVG(co.patient_satisfaction), 1) as avg_satisfaction
FROM patient_visits pv
LEFT JOIN visit_costs vc ON pv.visit_id = vc.visit_id
LEFT JOIN visit_revenue vr ON pv.visit_id = vr.visit_id
LEFT JOIN clinical_outcomes co ON pv.visit_id = co.visit_id
GROUP BY DATE_TRUNC('month', pv.visit_date)
ORDER BY month DESC;

CREATE VIEW IF NOT EXISTS v_department_comparison AS
SELECT 
    d.department_name,
    COUNT(pv.visit_id) as total_visits,
    ROUND(AVG(pv.wait_time_minutes), 2) as avg_wait_time,
    ROUND(AVG(pv.los_minutes), 2) as avg_los,
    ROUND(AVG(pv.referral_delay_days), 2) as avg_referral_delay,
    ROUND(AVG(co.patient_satisfaction), 1) as avg_satisfaction,
    ROUND(AVG(vc.total_cost), 2) as avg_cost,
    ROUND(SUM(vc.total_cost), 2) as total_cost,
    ROUND(SUM(vr.revenue_amount), 2) as total_revenue
FROM patient_visits pv
JOIN departments d ON pv.department_id = d.department_id
LEFT JOIN visit_costs vc ON pv.visit_id = vc.visit_id
LEFT JOIN visit_revenue vr ON pv.visit_id = vr.visit_id
LEFT JOIN clinical_outcomes co ON pv.visit_id = co.visit_id
GROUP BY d.department_id, d.department_name
ORDER BY avg_los DESC;

CREATE VIEW IF NOT EXISTS v_quality_metrics AS
SELECT 
    d.department_name,
    COUNT(pv.visit_id) as total_visits,
    ROUND(100.0 * SUM(CASE WHEN pd.readmitted_30days THEN 1 ELSE 0 END) / COUNT(pv.visit_id), 2) as readmission_rate,
    ROUND(100.0 * SUM(CASE WHEN pd.adverse_event THEN 1 ELSE 0 END) / COUNT(pv.visit_id), 2) as adverse_event_rate,
    ROUND(100.0 * SUM(CASE WHEN pd.mortality_flag THEN 1 ELSE 0 END) / COUNT(pv.visit_id), 2) as mortality_rate,
    ROUND(AVG(co.patient_satisfaction), 1) as avg_satisfaction
FROM patient_visits pv
JOIN departments d ON pv.department_id = d.department_id
LEFT JOIN patient_details pd ON pv.visit_id = pd.detail_id
LEFT JOIN clinical_outcomes co ON pv.visit_id = co.visit_id
GROUP BY d.department_id, d.department_name;

CREATE VIEW IF NOT EXISTS v_financial_summary AS
SELECT 
    d.department_name,
    COUNT(pv.visit_id) as total_visits,
    ROUND(SUM(vc.total_cost), 2) as total_cost,
    ROUND(AVG(vc.total_cost), 2) as avg_cost_per_visit,
    ROUND(SUM(vr.revenue_amount), 2) as total_revenue,
    ROUND(AVG(vr.revenue_amount), 2) as avg_revenue_per_visit,
    ROUND(SUM(vr.revenue_amount) - SUM(vc.total_cost), 2) as total_profit,
    ROUND(100.0 * (SUM(vr.revenue_amount) - SUM(vc.total_cost)) / SUM(vr.revenue_amount), 2) as profit_margin_pct
FROM patient_visits pv
JOIN departments d ON pv.department_id = d.department_id
LEFT JOIN visit_costs vc ON pv.visit_id = vc.visit_id
LEFT JOIN visit_revenue vr ON pv.visit_id = vr.visit_id
GROUP BY d.department_id, d.department_name;
