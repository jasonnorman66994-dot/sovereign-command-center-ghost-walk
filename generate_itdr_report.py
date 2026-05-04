import sys
import datetime
import uuid
import argparse

TEMPLATE_PATH = "OmniSOC_ITDR_Report_Template.md"

FILLIN = {
    "date": datetime.date.today().strftime("%B %d, %Y"),
    "status": "SUCCESS",
    "identity": "user@example.com",
    "report_id": str(uuid.uuid4())[:8],
    "summary": "Automated ITDR simulation completed. All phases executed, alerts delivered, and logs archived.",
    "credential_compromise": "Detected and contained.",
    "mfa_abuse": "Simulated MFA fatigue, auto-suppression triggered.",
    "session_hijacking": "No active session hijacking detected.",
    "bec_ato": "BEC/ATO rules simulated, no real compromise.",
    "timeline": "| 09:00 | Simulation started | Automation triggered |\n| 09:05 | Phishing simulation | Lure sent |\n| 09:10 | Alert delivered | Telegram/Email |\n| 09:15 | Remediation workflow | Multi-approver |\n| 09:20 | Forensic archiving | Logs moved |",
    "outcome": "All events processed, executive report generated, environment reset."
}

def fill_template(template_path, output_path, overrides):
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    for key, value in overrides.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Report generated: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Auto-fill ITDR report template.")
    parser.add_argument('--identity', type=str, help='Target identity (email)', default=FILLIN["identity"])
    parser.add_argument('--status', type=str, help='Simulation status', default=FILLIN["status"])
    parser.add_argument('--summary', type=str, help='Executive summary', default=FILLIN["summary"])
    parser.add_argument('--output', type=str, help='Output file', default='OmniSOC_ITDR_Report_Auto.md')
    args = parser.parse_args()
    overrides = FILLIN.copy()
    overrides["identity"] = args.identity
    overrides["status"] = args.status
    overrides["summary"] = args.summary
    fill_template(TEMPLATE_PATH, args.output, overrides)

if __name__ == "__main__":
    main()
