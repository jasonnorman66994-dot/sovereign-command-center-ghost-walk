-- PostgreSQL migration: create alerts table for SvelteKit dashboard
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    timestamp_utc TIMESTAMP NOT NULL,
    user_email TEXT NOT NULL,
    geo_location JSONB
);
