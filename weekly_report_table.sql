CREATE TABLE IF NOT EXISTS weekly_expense_reports (
    report_id SERIAL PRIMARY KEY,

    user_id INT NOT NULL,

    week_start DATE NOT NULL,
    week_end DATE NOT NULL,

    total_expenses NUMERIC(14,2) NOT NULL DEFAULT 0,

    total_transactions INT NOT NULL DEFAULT 0,

    average_transaction NUMERIC(14,2) NOT NULL DEFAULT 0,

    highest_category VARCHAR(100),

    highest_category_amount NUMERIC(14,2),

    category_totals JSONB NOT NULL DEFAULT '{}'::jsonb,

    daily_totals JSONB NOT NULL DEFAULT '{}'::jsonb,

    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_weekly_report_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    CONSTRAINT unique_user_week
        UNIQUE (user_id, week_start, week_end)
);