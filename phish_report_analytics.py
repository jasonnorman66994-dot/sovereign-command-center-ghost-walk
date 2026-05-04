import csv
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

TRACK_LOG = 'click_log.csv'
CHART_CLICKS_OVER_TIME = 'clicks_over_time.png'
CHART_TOP_USERS = 'top_users.png'

# Load data
clicks = []
with open(TRACK_LOG, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        clicks.append(row)

# DataFrame for analysis

if not clicks:
    print('No click data found.')
    exit(1)
df = pd.DataFrame(clicks)
df['timestamp'] = pd.to_datetime(df['timestamp'])
# Remove timezone if present
if pd.api.types.is_datetime64_any_dtype(df['timestamp']):
    try:
        df['timestamp'] = df['timestamp'].dt.tz_localize(None)
    except (AttributeError, TypeError):
        pass

# Clicks over time (hourly)
df.set_index('timestamp', inplace=True)
hourly = df.resample('h').size()
hourly.plot(title='Clicks Over Time (Hourly)', ylabel='Clicks', xlabel='Time')
plt.tight_layout()
plt.savefig(CHART_CLICKS_OVER_TIME)
plt.close()
print(f'Chart saved: {CHART_CLICKS_OVER_TIME}')

# Top users by clicks
top_users = df['email'].value_counts().head(10)
top_users.plot(kind='bar', title='Top 10 Users by Clicks', ylabel='Clicks', xlabel='User')
plt.tight_layout()
plt.savefig(CHART_TOP_USERS)
plt.close()
print(f'Chart saved: {CHART_TOP_USERS}')

# Time-based analysis CSV
hourly.to_csv('clicks_hourly.csv', header=['Clicks'])
print('Hourly click data exported to clicks_hourly.csv')

# Integration with other tools: Export to Excel
# Remove timezone info for Excel compatibility
df_no_tz = df.copy()
if 'timestamp' in df_no_tz.columns:
    df_no_tz['timestamp'] = df_no_tz['timestamp'].dt.tz_localize(None)
with pd.ExcelWriter('phish_campaign_report.xlsx') as writer:
    df_no_tz.reset_index().to_excel(writer, sheet_name='Raw Clicks', index=False)
    hourly.to_frame('Clicks').to_excel(writer, sheet_name='Clicks Over Time')
    top_users.to_frame('Clicks').to_excel(writer, sheet_name='Top Users')
print('Excel report exported to phish_campaign_report.xlsx')
