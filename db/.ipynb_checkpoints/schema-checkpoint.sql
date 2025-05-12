-- Employee Data
CREATE TABLE IF NOT EXISTS employee_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    middle_name TEXT,
    last_name TEXT,
    sex TEXT,
    grade TEXT,
    qualification TEXT,
    position TEXT,
    gross_salary REAL,
    dob DATE,
    doe DATE,
    nir_number TEXT,
    county_of_assignment TEXT,
    department TEXT,
    category TEXT
);

-- Attendance
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER,
    days_present INTEGER,
    days_absent INTEGER,
    absence_with_excuse INTEGER,
    recommended_action TEXT,
    comment TEXT,
    FOREIGN KEY(id) REFERENCES employee_data(id)
);

-- Reclassification
CREATE TABLE IF NOT EXISTS reclassification (
    id INTEGER,
    current_position TEXT,
    department_from TEXT,
    department_to TEXT,
    qualification TEXT,
    reason TEXT,
    new_position TEXT,
    FOREIGN KEY(id) REFERENCES employee_data(id)
);
