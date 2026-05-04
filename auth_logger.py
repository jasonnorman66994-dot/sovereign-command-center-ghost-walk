# auth_logger.py
import hashlib
import requests
from datetime import datetime

def log_auth_attempt(user_id, email, method, result, failure_reason=None, session_id=None, user_agent=None, ip=None):
    geo = get_geo_location(ip)
    fingerprint = hashlib.md5(
        (user_agent or '').encode()
    ).hexdigest()
    import mysql.connector
    db = mysql.connector.connect(host="localhost", user="authuser", password="authpass", database="auth_db")
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO auth_logs 
        (user_id, email, ip_address, user_agent, method, result, failure_reason, 
         country, city, latitude, longitude, device_fingerprint, session_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id,
        email,
        ip,
        user_agent,
        method,
        result,
        failure_reason,
        geo.get('country', 'Unknown'),
        geo.get('city', 'Unknown'),
        geo.get('latitude'),
        geo.get('longitude'),
        fingerprint,
        session_id
    ))
    db.commit()
    cursor.close()
    db.close()
def get_geo_location(ip):
    try:
        response = requests.get(f'https://ipapi.co/{ip}/json/')
        return response.json()
    except:
        return {}
