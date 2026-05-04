# Slack alert function
send_slack_alert() {
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"$1\"}" "${SLACK_WEBHOOK_URL}"
}
#!/bin/bash
# security_monitor.sh - Run via cron every minute
MYSQL_USER="authuser"
MYSQL_PASS="authpass"
MYSQL_DB="auth_db"

# Check for brute force attacks
BRUTE_FORCE=$(mysql -u$MYSQL_USER -p$MYSQL_PASS -D$MYSQL_DB -sse "
    SELECT COUNT(DISTINCT ip_address)
    FROM auth_logs
    WHERE result = 'failed'
    AND timestamp >= NOW() - INTERVAL 15 MINUTE
    HAVING COUNT(*) >= 5
")

if [ "$BRUTE_FORCE" -gt 0 ]; then
    MSG="ALERT: Brute force attack detected from $BRUTE_FORCE IP(s)"
    echo "$MSG" | mail -s "CRITICAL: Brute Force Attack" security@yourcompany.com
    send_slack_alert "$MSG"
fi

# Check for impossible travel
IMPOSSIBLE_TRAVEL=$(mysql -u$MYSQL_USER -p$MYSQL_PASS -D$MYSQL_DB -sse "
    SELECT COUNT(*) FROM (
        SELECT a1.email
        FROM auth_logs a1
        JOIN auth_logs a2 ON a1.email = a2.email
        WHERE a1.result = 'success'
          AND a2.result = 'success'
          AND a1.timestamp >= NOW() - INTERVAL 1 HOUR
          AND a2.timestamp > a1.timestamp
          AND a2.timestamp <= a1.timestamp + INTERVAL 2 HOUR
          AND a1.country != a2.country
    ) AS impossible
")

if [ "$IMPOSSIBLE_TRAVEL" -gt 0 ]; then
    MSG="ALERT: Impossible travel detected for $IMPOSSIBLE_TRAVEL user(s)"
    echo "$MSG" | mail -s "HIGH: Impossible Travel" security@yourcompany.com
    send_slack_alert "$MSG"
fi

# Check for cookie hijacking
COOKIE_HIJACK=$(mysql -u$MYSQL_USER -p$MYSQL_PASS -D$MYSQL_DB -sse "
    SELECT COUNT(DISTINCT cookie_id)
    FROM cookie_logs
    WHERE last_seen_at >= NOW() - INTERVAL 30 MINUTE
      AND cookie_id IN (
        SELECT cookie_id
        FROM cookie_logs
        GROUP BY cookie_id
        HAVING COUNT(DISTINCT last_seen_ip) > 1
      )
")

if [ "$COOKIE_HIJACK" -gt 0 ]; then
    MSG="ALERT: Cookie hijacking detected for $COOKIE_HIJACK cookie(s)"
    echo "$MSG" | mail -s "HIGH: Cookie Hijacking" security@yourcompany.com
    send_slack_alert "$MSG"
fi
