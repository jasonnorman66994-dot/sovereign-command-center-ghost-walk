# send_telegram_alert.py
"""
Python wrapper to automate sending alerts to Telegram via send_telegram_alert.js
Usage:
    python send_telegram_alert.py <payload_file.json>
"""
import subprocess
import sys
import os

NODE_SCRIPT = 'send_telegram_alert.js'

def send_telegram_alert(payload_file):
    if not os.path.exists(NODE_SCRIPT):
        print(f"❌ Node.js script '{NODE_SCRIPT}' not found.")
        sys.exit(1)
    cmd = ['node', NODE_SCRIPT, payload_file]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            errors='replace'
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        # Unicode-safe error printing
        try:
            print(f"❌ Error running Node.js script: {e.stderr}")
        except UnicodeEncodeError:
            print("[Error] Node.js script failed (Unicode in output, see log file for details)")
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python send_telegram_alert.py <payload_file.json>")
        sys.exit(1)
    payload_file = sys.argv[1]
    send_telegram_alert(payload_file)
