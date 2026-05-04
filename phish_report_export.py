import csv
from collections import defaultdict
from datetime import datetime

TRACK_LOG = 'click_log.csv'
CSV_EXPORT = 'phish_click_report.csv'
HTML_EXPORT = 'phish_click_report.html'

# Read click log
clicks = []
with open(TRACK_LOG, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        clicks.append(row)

# Per-user stats
user_stats = defaultdict(lambda: {'clicks': 0, 'devices': set(), 'ips': set()})
for row in clicks:
    email = row['email']
    user_stats[email]['clicks'] += 1
    user_stats[email]['devices'].add(row['deviceId'])
    user_stats[email]['ips'].add(row['ip'])

# Export CSV summary
with open(CSV_EXPORT, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Email', 'Total Clicks', 'Unique Devices', 'Unique IPs'])
    for email, stats in user_stats.items():
        writer.writerow([email, stats['clicks'], len(stats['devices']), len(stats['ips'])])
print(f'CSV summary exported to {CSV_EXPORT}')

# Export HTML report
html = ['<h2>Phishing Simulation Click Report</h2>']
html.append(f'<p>Generated: {datetime.utcnow().isoformat()} UTC</p>')
html.append('<table border="1" cellpadding="5"><tr><th>Email</th><th>Total Clicks</th><th>Unique Devices</th><th>Unique IPs</th></tr>')
for email, stats in user_stats.items():
    html.append(f'<tr><td>{email}</td><td>{stats["clicks"]}</td><td>{len(stats["devices"])} ({", ".join(stats["devices"])} )</td><td>{len(stats["ips"])} ({", ".join(stats["ips"])} )</td></tr>')
html.append('</table>')
html.append('<h3>Raw Click Log</h3>')
html.append('<table border="1" cellpadding="3"><tr>' + ''.join(f'<th>{h}</th>' for h in clicks[0].keys()) + '</tr>')
for row in clicks:
    html.append('<tr>' + ''.join(f'<td>{row[h]}</td>' for h in clicks[0].keys()) + '</tr>')
html.append('</table>')
with open(HTML_EXPORT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(html))
print(f'HTML report exported to {HTML_EXPORT}')
