#!/usr/bin/env python3
"""
Identity Threat Alert Telegram Bot Formatter
Converts JSON payloads to SOC-friendly Telegram messages

Usage:
  from telegram_formatter import format_telegram_alert
  message = format_telegram_alert(payload_dict)
  
Or as CLI:
  python telegram_formatter.py payload.json
"""

import json
import sys
from typing import Dict, Any, Optional


def escape_telegram_markdown(text: Optional[str]) -> str:
    """
    Escape Telegram MarkdownV2 special characters.
    MarkdownV2 requires escaping: _ * [ ] ( ) ~ ` > # + - = | { } . !
    """
    if text is None:
        return ""
    
    text = str(text)
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def get_severity_emoji(severity: str) -> str:
    """Map severity level to emoji indicator"""
    emoji_map = {
        'low': '🟢',
        'medium': '🟡',
        'high': '🟠',
        'critical': '🔴'
    }
    return emoji_map.get(severity.lower(), '⚪')


def format_risk_detections(detections: list) -> str:
    """Format risk detections as a bulleted list"""
    if not detections:
        return "• No specific indicators detected"
    
    formatted = []
    for detection in detections[:5]:  # Limit to 5 for Telegram readability
        formatted.append(f"• {escape_telegram_markdown(detection)}")
    
    if len(detections) > 5:
        formatted.append(f"• \\+{len(detections) - 5} more indicators")
    
    return '\n'.join(formatted)


def format_investigation_links(links: Dict[str, str]) -> str:
    """Format investigation links as inline buttons"""
    formatted = []
    
    link_labels = {
        'signin_logs': 'Sign\\-in Logs',
        'oauth_apps': 'OAuth Apps',
        'inbox_rules': 'Inbox Rules',
        'sentinel_query': 'Sentinel Query',
        'user_profile': 'User Profile'
    }
    
    for key, label in link_labels.items():
        if key in links and links[key]:
            # Format as markdown link: [text](url)
            formatted.append(f"[{label}]({links[key]})")
    
    return ' | '.join(formatted)


def format_telegram_alert(payload: Dict[str, Any]) -> str:
    """
    Convert Identity Threat Alert JSON payload to Telegram MarkdownV2 message.
    
    Args:
        payload: Dictionary containing the alert payload
        
    Returns:
        Formatted message string safe for Telegram MarkdownV2
    """
    user = payload.get('user', {})
    event = payload.get('event', {})
    tech = payload.get('technical_indicators', {})
    links = payload.get('investigation_links', {})
    assigned = payload.get('assigned_to', {})
    severity = payload.get('severity', 'medium')
    
    severity_emoji = get_severity_emoji(severity)
    
    # Build message parts
    message_parts = [
        f"{severity_emoji} *IDENTITY SECURITY ALERT*",
        "Potential account compromise detected\\.",
        "",
        f"👤 *User:* {escape_telegram_markdown(user.get('email', 'N/A'))}",
        f"🆔 *User ID:* {escape_telegram_markdown(user.get('user_id', 'N/A'))}",
        f"🏢 *Department:* {escape_telegram_markdown(user.get('department', 'N/A'))}",
        f"🔐 *Role:* {escape_telegram_markdown(user.get('role', 'N/A'))}",
        "",
        "\\-\\-\\-",
        "",
        f"⚠️ *Event Type:* {escape_telegram_markdown(event.get('event_type', 'N/A'))}",
        f"{escape_telegram_markdown(event.get('description', 'N/A'))}",
        "",
        f"🕒 *Timestamp:* {escape_telegram_markdown(payload.get('timestamp_utc', 'N/A'))}",
        f"🌐 *Source IP:* {escape_telegram_markdown(event.get('source_ip', 'N/A'))}",
        f"🏢 *ASN / Location:* {escape_telegram_markdown(event.get('asn', 'N/A'))} / {escape_telegram_markdown(event.get('geo_location', 'N/A'))}",
        f"📱 *Client App:* {escape_telegram_markdown(event.get('client_app', 'N/A'))}",
        f"🔐 *Auth Method:* {escape_telegram_markdown(event.get('auth_method', 'N/A'))}",
        "",
        "\\-\\-\\-",
        "",
        "*🧩 Risk Indicators:*",
        format_risk_detections(event.get('risk_detections', [])),
        "",
        "\\-\\-\\-",
        "",
        "*🛑 Immediate Response Actions:*",
    ]
    
    # Add recommended actions with numbering
    actions = payload.get('recommended_actions', [])
    for i, action in enumerate(actions[:6], 1):  # Limit to 6 actions
        message_parts.append(f"{i}\\. {escape_telegram_markdown(action)}")
    
    if len(actions) > 6:
        message_parts.append(f"\\+ {len(actions) - 6} additional actions")
    
    message_parts.extend([
        "",
        "\\-\\-\\-",
        "",
        "*🛠️ Investigation Links:*",
        format_investigation_links(links),
        "",
        "\\-\\-\\-",
        "",
        f"*📣 Severity:* {severity_emoji} {escape_telegram_markdown(severity.upper())}",
        f"*👮 Assigned To:* {escape_telegram_markdown(assigned.get('analyst', 'N/A'))}"
    ])
    
    return '\n'.join(message_parts)


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python telegram_formatter.py <payload.json>")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r') as f:
            payload = json.load(f)
        
        message = format_telegram_alert(payload)
        print(message)
        
    except FileNotFoundError:
        print(f"Error: File '{sys.argv[1]}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
