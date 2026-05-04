#!/bin/bash
# Import alert rules into MSSQL using sqlcmd
# Usage: ./import_alert_rules.sh <server> <database> <user> <password>

SERVER=${1:-localhost}
DATABASE=${2:-auth_db}
USER=${3:-authuser}
PASSWORD=${4:-authpass}
SQLFILE="$(dirname "$0")/create_alert_rules.sql"

if ! command -v sqlcmd &> /dev/null; then
    echo "sqlcmd not found. Please install the SQL Server command-line tools."
    exit 1
fi

sqlcmd -S "$SERVER" -d "$DATABASE" -U "$USER" -P "$PASSWORD" -i "$SQLFILE"
RESULT=$?
if [ $RESULT -eq 0 ]; then
    echo "Alert rules imported successfully."
else
    echo "Failed to import alert rules."
    exit $RESULT
fi
