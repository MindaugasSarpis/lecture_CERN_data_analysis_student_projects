CREATE TABLE IF NOT EXISTS tasks (
    task_id BIGINT DEFAULT nextval('serial'),
    run_date DATE,
    category TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT,
    pages INTEGER,
    records INTEGER,
    error TEXT,
    PRIMARY KEY (task_id)
);