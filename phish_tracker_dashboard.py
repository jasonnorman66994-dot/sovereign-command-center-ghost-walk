from flask import Flask, request, redirect, render_template_string
import csv
import os
from datetime import datetime

app = Flask(__name__)
TRACK_LOG = 'click_log.csv'

# Ensure log file exists
if not os.path.exists(TRACK_LOG):
    with open(TRACK_LOG, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'deviceId', 'email', 'ip', 'user_agent', 'redirect'])

@app.route('/track')
def track():
    deviceId = request.args.get('cid', 'unknown')
    email = request.args.get('email', 'unknown')
    redirect_url = request.args.get('redirect', 'https://microsoft.com')
    ip = request.remote_addr
    ua = request.headers.get('User-Agent', '')
    with open(TRACK_LOG, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.utcnow().isoformat(), deviceId, email, ip, ua, redirect_url])
    return redirect(redirect_url)

@app.route('/dashboard')
def dashboard():
    rows = []
    with open(TRACK_LOG, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    html = '''
    <h2>Phishing Simulation Click Dashboard</h2>
    <table border="1" cellpadding="5">
      <tr><th>Timestamp</th><th>Device ID</th><th>Email</th><th>IP</th><th>User Agent</th><th>Redirect</th></tr>
      {% for r in rows %}
      <tr><td>{{r['timestamp']}}</td><td>{{r['deviceId']}}</td><td>{{r['email']}}</td><td>{{r['ip']}}</td><td>{{r['user_agent']}}</td><td>{{r['redirect']}}</td></tr>
      {% endfor %}
    </table>
    <p>Total Clicks: {{rows|length}}</p>
    '''
    return render_template_string(html, rows=rows)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
