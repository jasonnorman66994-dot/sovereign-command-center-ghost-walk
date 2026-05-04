ALTER TABLE alerts
    ADD slack_channel_id VARCHAR(64) NOT NULL DEFAULT '';
CREATE INDEX idx_slack_channel_id ON alerts (slack_channel_id);
