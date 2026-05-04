#!/usr/bin/env python3
"""
Test Alert Payload Generator
Generates various threat scenarios for testing the alerting pipeline

Usage:
  python test_payloads.py --severity critical --scenario mfa_fatigue
  python test_payloads.py --scenario all  # generates 5 different scenarios
"""

import json
import uuid
import argparse
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class AlertPayloadGenerator:
    """Generate test alert payloads for different threat scenarios"""
    
    BASE_PAYLOAD = {
        "alert_type": "identity_compromise",
        "severity": "critical",
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "user": {
            "email": "user@company.com",
            "user_id": str(uuid.uuid4()),
            "display_name": "Test User",
            "department": "Engineering",
            "role": "Software Engineer",
            "privileged_access": False
        },
        "event": {
            "event_type": "test_event",
            "description": "Test alert for validation",
            "source_ip": "192.168.1.100",
            "asn": "AS12345",
            "geo_location": "Test Location",
            "client_app": "Browser",
            "auth_method": "Password",
            "risk_level": "high",
            "risk_detections": ["Test detection"],
            "correlation_id": str(uuid.uuid4()),
            "session_id": f"session-{uuid.uuid4().hex[:8]}"
        },
        "technical_indicators": {
            "mfa_fatigue_count": 0,
            "legacy_protocol_used": False,
            "oauth_app_detected": False,
            "oauth_app_scopes": [],
            "hidden_inbox_rules_detected": False,
            "impossible_travel_detected": False,
            "token_replay_detected": False,
            "new_device_registration": False,
            "unfamiliar_signin_properties": False
        },
        "recommended_actions": [
            "Revoke all active sessions",
            "Block the account",
            "Reset password"
        ],
        "investigation_links": {
            "signin_logs": "https://entra.microsoft.com/#view/signin",
            "oauth_apps": "https://entra.microsoft.com/#view/apps",
            "inbox_rules": "https://admin.exchange.microsoft.com/#/mailboxes",
            "sentinel_query": "https://portal.azure.com/#blade/sentinel",
            "user_profile": "https://entra.microsoft.com/#view/profile"
        },
        "assigned_to": {
            "analyst": "@test_analyst",
            "team": "Security Operations Center"
        },
        "metadata": {
            "pipeline_version": "1.0.0",
            "source_system": "Sentinel",
            "environment": "test"
        }
    }
    
    @staticmethod
    def scenario_mfa_fatigue() -> Dict[str, Any]:
        """MFA Fatigue Attack Scenario"""
        payload = json.loads(json.dumps(AlertPayloadGenerator.BASE_PAYLOAD))
        payload.update({
            "severity": "critical",
            "timestamp_utc": datetime.utcnow().isoformat() + "Z"
        })
        payload["user"]["display_name"] = "CEO, Executive"
        payload["user"]["privileged_access"] = True
        payload["event"].update({
            "event_type": "mfa_fatigue_attack",
            "description": "User received 23 MFA push prompts in 4 minutes. Possible MFA fatigue attack.",
            "source_ip": "185.220.100.44",
            "asn": "AS20860",
            "geo_location": "Bucharest, Romania",
            "client_app": "Browser",
            "auth_method": "MFA Push",
            "risk_level": "high",
            "risk_detections": [
                "Repeated MFA prompts",
                "Multiple failed authentications",
                "Unusual geographic location",
                "First time login from this region"
            ]
        })
        payload["technical_indicators"].update({
            "mfa_fatigue_count": 23,
            "unfamiliar_signin_properties": True
        })
        return payload
    
    @staticmethod
    def scenario_oauth_abuse() -> Dict[str, Any]:
        """OAuth Abuse / Risky App Consent"""
        payload = json.loads(json.dumps(AlertPayloadGenerator.BASE_PAYLOAD))
        payload.update({
            "severity": "high",
            "timestamp_utc": datetime.utcnow().isoformat() + "Z"
        })
        payload["event"].update({
            "event_type": "oauth_abuse",
            "description": "User granted consent to third-party app requesting Mail.ReadWrite and offline_access scopes.",
            "source_ip": "203.0.113.50",
            "asn": "AS15169",
            "geo_location": "Mountain View, USA",
            "client_app": "OAuth App - 'CloudSync Pro'",
            "auth_method": "OAuth Consent",
            "risk_level": "high",
            "risk_detections": [
                "OAuth app with risky scopes",
                "Mail.ReadWrite permission",
                "offline_access requested",
                "Unknown publisher"
            ]
        })
        payload["technical_indicators"].update({
            "oauth_app_detected": True,
            "oauth_app_scopes": ["Mail.ReadWrite", "offline_access", "Calendar.ReadWrite"]
        })
        return payload
    
    @staticmethod
    def scenario_impossible_travel() -> Dict[str, Any]:
        """Impossible Travel - Geographic Anomaly"""
        payload = json.loads(json.dumps(AlertPayloadGenerator.BASE_PAYLOAD))
        payload.update({
            "severity": "critical",
            "timestamp_utc": datetime.utcnow().isoformat() + "Z"
        })
        payload["event"].update({
            "event_type": "impossible_travel",
            "description": "Sign-in from Tokyo, Japan 30 minutes after login from London, UK (geographically impossible in that timeframe).",
            "source_ip": "210.201.80.10",
            "asn": "AS2914",
            "geo_location": "Tokyo, Japan",
            "client_app": "Browser",
            "auth_method": "MFA Push",
            "risk_level": "high",
            "risk_detections": [
                "Impossible travel detected",
                "Geographic inconsistency",
                "Login from 5400 miles away in 30 minutes"
            ]
        })
        payload["technical_indicators"].update({
            "impossible_travel_detected": True
        })
        payload["user"]["display_name"] = "Global Manager"
        return payload
    
    @staticmethod
    def scenario_legacy_protocol() -> Dict[str, Any]:
        """Legacy Protocol Use - IMAP/POP3 Login"""
        payload = json.loads(json.dumps(AlertPayloadGenerator.BASE_PAYLOAD))
        payload.update({
            "severity": "medium",
            "timestamp_utc": datetime.utcnow().isoformat() + "Z"
        })
        payload["event"].update({
            "event_type": "legacy_protocol_login",
            "description": "User authenticated using IMAP protocol. Legacy protocols should be disabled.",
            "source_ip": "192.0.2.123",
            "asn": "AS12389",
            "geo_location": "Internal Network",
            "client_app": "IMAP",
            "auth_method": "Basic Auth",
            "risk_level": "medium",
            "risk_detections": [
                "Legacy protocol use detected",
                "IMAP protocol not disabled",
                "Basic authentication"
            ]
        })
        payload["technical_indicators"].update({
            "legacy_protocol_used": True
        })
        return payload
    
    @staticmethod
    def scenario_token_replay() -> Dict[str, Any]:
        """Token Replay / Session Hijacking"""
        payload = json.loads(json.dumps(AlertPayloadGenerator.BASE_PAYLOAD))
        payload.update({
            "severity": "high",
            "timestamp_utc": datetime.utcnow().isoformat() + "Z"
        })
        payload["event"].update({
            "event_type": "token_replay",
            "description": "Session token replayed from different IP and device. Possible AiTM or session hijacking attack.",
            "source_ip": "198.51.100.89",
            "asn": "AS54001",
            "geo_location": "Sao Paulo, Brazil",
            "client_app": "Browser",
            "auth_method": "Token Replay",
            "risk_level": "high",
            "risk_detections": [
                "Token replay pattern detected",
                "Session from different device",
                "Possible AiTM attack"
            ]
        })
        payload["technical_indicators"].update({
            "token_replay_detected": True,
            "new_device_registration": True
        })
        return payload
    
    @staticmethod
    def scenario_low_severity() -> Dict[str, Any]:
        """Low Severity - Informational"""
        payload = json.loads(json.dumps(AlertPayloadGenerator.BASE_PAYLOAD))
        payload.update({
            "severity": "low",
            "timestamp_utc": datetime.utcnow().isoformat() + "Z"
        })
        payload["event"].update({
            "event_type": "new_sign_in_property",
            "description": "User signed in from a new device/location. This is the first sign-in from this device.",
            "source_ip": "203.0.113.200",
            "asn": "AS15169",
            "geo_location": "San Francisco, USA",
            "client_app": "Browser",
            "auth_method": "MFA Push",
            "risk_level": "low",
            "risk_detections": [
                "New device sign-in",
                "First sign-in from this device"
            ]
        })
        payload["technical_indicators"].update({
            "new_device_registration": True
        })
        return payload
    
    @staticmethod
    def generate_scenario(scenario_name: str) -> Dict[str, Any]:
        """Generate a specific scenario by name"""
        scenarios = {
            'mfa_fatigue': AlertPayloadGenerator.scenario_mfa_fatigue,
            'oauth_abuse': AlertPayloadGenerator.scenario_oauth_abuse,
            'impossible_travel': AlertPayloadGenerator.scenario_impossible_travel,
            'legacy_protocol': AlertPayloadGenerator.scenario_legacy_protocol,
            'token_replay': AlertPayloadGenerator.scenario_token_replay,
            'low_severity': AlertPayloadGenerator.scenario_low_severity,
        }
        
        if scenario_name not in scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}. Available: {', '.join(scenarios.keys())}")
        
        return scenarios[scenario_name]()


def main():
    parser = argparse.ArgumentParser(
        description='Generate test alert payloads for validation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_payloads.py --scenario mfa_fatigue
  python test_payloads.py --scenario all > payloads.json
  python test_payloads.py --scenario oauth_abuse --output alert.json
        """
    )
    
    parser.add_argument(
        '--scenario',
        choices=['mfa_fatigue', 'oauth_abuse', 'impossible_travel', 'legacy_protocol', 'token_replay', 'low_severity', 'all'],
        default='mfa_fatigue',
        help='Threat scenario to generate'
    )
    
    parser.add_argument(
        '--output',
        '-o',
        type=str,
        help='Output file (default: print to stdout)'
    )
    
    parser.add_argument(
        '--pretty',
        '-p',
        action='store_true',
        default=True,
        help='Pretty print JSON (default: True)'
    )
    
    args = parser.parse_args()
    
    if args.scenario == 'all':
        payloads = {
            'mfa_fatigue': AlertPayloadGenerator.scenario_mfa_fatigue(),
            'oauth_abuse': AlertPayloadGenerator.scenario_oauth_abuse(),
            'impossible_travel': AlertPayloadGenerator.scenario_impossible_travel(),
            'legacy_protocol': AlertPayloadGenerator.scenario_legacy_protocol(),
            'token_replay': AlertPayloadGenerator.scenario_token_replay(),
            'low_severity': AlertPayloadGenerator.scenario_low_severity(),
        }
        output = payloads
    else:
        output = AlertPayloadGenerator.generate_scenario(args.scenario)
    
    json_str = json.dumps(output, indent=2 if args.pretty else None)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(json_str)
        print(f"✅ Payload written to {args.output}")
    else:
        print(json_str)


if __name__ == '__main__':
    main()
