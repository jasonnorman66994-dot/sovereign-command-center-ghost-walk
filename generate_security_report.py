import mysql.connector
from fpdf import FPDF
from datetime import datetime
import smtplib
from email.message import EmailMessage

# Database connection
conn = mysql.connector.connect(
    host='localhost', user='authuser', password='authpass', database='auth_db'
)
cursor = conn.cursor(dictionary=True)

# Query summary data
cursor.execute("""
SELECT COUNT(*) as total_logins,
       SUM(result='failed') as failed_logins,
       SUM(result='success') as successful_logins,
       SUM(risk_score > 10) as high_risk,
       MAX(risk_score) as max_risk
FROM auth_logs
WHERE timestamp >= NOW() - INTERVAL 1 DAY
""")
sum_data = cursor.fetchone()

# Query top alerts
cursor.execute("""
SELECT * FROM security_alerts WHERE timestamp >= NOW() - INTERVAL 1 DAY ORDER BY severity DESC, timestamp DESC LIMIT 10
""")
alerts = cursor.fetchall()

# Generate PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font('Arial', 'B', 16)
pdf.cell(0, 10, 'Daily Security Report', ln=1, align='C')
pdf.set_font('Arial', '', 12)
pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=1)
pdf.ln(5)
pdf.cell(0, 10, f"Total Logins: {sum_data['total_logins']}", ln=1)
pdf.cell(0, 10, f"Failed Logins: {sum_data['failed_logins']}", ln=1)
pdf.cell(0, 10, f"Successful Logins: {sum_data['successful_logins']}", ln=1)
pdf.cell(0, 10, f"High Risk Events: {sum_data['high_risk']}", ln=1)
pdf.cell(0, 10, f"Max Risk Score: {sum_data['max_risk']}", ln=1)
pdf.ln(10)
pdf.set_font('Arial', 'B', 14)
pdf.cell(0, 10, 'Top Security Alerts', ln=1)
pdf.set_font('Arial', '', 12)
for alert in alerts:
    pdf.cell(0, 8, f"[{alert['timestamp']}] {alert['alert_type']} ({alert['severity']}): {alert['description']}", ln=1)
pdf.output('security_report.pdf')

# Email PDF
EMAIL_FROM = 'security@yourcompany.com'
EMAIL_TO = 'security@yourcompany.com'
EMAIL_SUBJECT = 'Daily Security Report'
EMAIL_PASS = 'yourpassword'  # Use app password or env var in production

msg = EmailMessage()
msg['Subject'] = EMAIL_SUBJECT
msg['From'] = EMAIL_FROM
msg['To'] = EMAIL_TO
msg.set_content('See attached daily security report.')
with open('security_report.pdf', 'rb') as f:
    msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename='security_report.pdf')

with smtplib.SMTP('smtp.yourcompany.com', 587) as smtp:
    smtp.starttls()
    smtp.login(EMAIL_FROM, EMAIL_PASS)
    smtp.send_message(msg)

print('Report generated and emailed.')
