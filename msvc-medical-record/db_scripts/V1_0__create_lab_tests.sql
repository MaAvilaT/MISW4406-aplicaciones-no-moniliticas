CREATE TABLE IF NOT EXISTS lab_tests (
    id VARCHAR PRIMARY KEY,
    lab_id VARCHAR NOT NULL,
    lab_token VARCHAR NOT NULL,
    lab_document JSON NOT NULL,
    patient_uuid VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
