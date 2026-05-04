
# sovereign-command-center-ghost-walk

## Identity Threat Alert System - Production Ready

## Environment Status: Locked and Hardened

- Status: Locked and Hardened
- Ghost-Walk history rewrite: complete
- Repository history baseline: clean orphan root commit (post-secret scrub)
- Production release tag: v2.0-stable-final
- Deployment safety guardrails: fail-fast alerting readiness checks for Slack and Telegram are enforced in GitHub Actions workflows

A comprehensive, SOC-friendly alerting solution for detecting and responding to identity compromise, MFA-bypass, and endpoint threats. Built for Sentinel, SOAR platforms, and Telegram bot integration.

---

## 📦 Components

### 1. **JSON Schema** (`schema.json`)

Production-grade JSON Schema (Draft 7) for alert payload validation.

**Features:**

 Strict schema validation with required fields
 Rich field descriptions and enum constraints
 Email and URL format validation
 UUID correlation IDs
 Example payload included

### 2. **OpenAPI Specification** (`openapi.yaml`)

Complete OpenAPI 3.0.3 spec for alert ingestion API.

**Endpoints:**
`POST /alerts` - Ingest identity threat alert

### 3. **TypeScript Interfaces** (`types.ts`)

Production-ready TypeScript types for type-safe alert generation.

**Exports:**
`IdentityThreatAlert` - Main alert type
`AlertSeverity`, `AlertType`, `SourceSystem` - Union types
Utility functions: `getSeverityEmoji()`, `escapeTelegramMarkdown()`, `formatTimestamp()`

### 4. **Telegram Formatters**

**Python** (`telegram_formatter.py`)  SOC-friendly Telegram MarkdownV2 formatter
**JavaScript** (`telegram-formatter.js`)  Node.js/Lambda/Azure Functions version

### 5. **Sentinel KQL Rule** (`sentinel-correlation-rule.kql`)

Multi-event correlation rule detecting:
✅ MFA Fatigue (10+ failed prompts in 5min)
✅ Impossible Travel (geographic inconsistency)
✅ OAuth Abuse (risky scope requests)
✅ Legacy Protocol Use (IMAP/POP3/SMTP)
✅ Token Replay / AiTM patterns
✅ Defender for Endpoint device alerts

### 6. **Validation** (`validate.js`)

AJV-based JSON Schema validation with strict mode and format checking.

---

## 🚀 Quick Start

### Setup

```bash
npm install
```

### Validate Schema (AJV)

```bash
npm run validate
```

### Preview API Docs

```bash
# ReDoc (recommended)
npm run start:redoc

# Swagger UI
npm run start:swagger
```

### Test Formatters

```bash
# Python - converts schema example to Telegram message
python telegram_formatter.py schema.json

# JavaScript - same
node telegram-formatter.js schema.json
```

---

## 📋 Alert Structure

The system uses a unified JSON alert payload with these sections:

- **alert_type** - Classification (identity_compromise, identity_endpoint_compromise)
- **severity** - Level (low, medium, high, critical) with emoji (🟢🟡🟠🔴)
- **timestamp_utc** - ISO 8601 UTC timestamp
- **user** - Email, ID, department, role, privileged access flag
- **event** - Event type, description, source IP, ASN, geo location, client app, auth method, risk detections
- **technical_indicators** - MFA count, legacy protocol use, OAuth abuse, device alerts
- **recommended_actions** - Prioritized IR response steps
- **investigation_links** - URLs to sign-in logs, OAuth apps, inbox rules, Sentinel query, user profile
- **assigned_to** - On-call analyst and team name
- **metadata** - Pipeline version, source system, environment

---

## 🔗 Integration Patterns

### Pattern 1: Sentinel Analytics Rule → SOAR → Telegram

```text
Sentinel KQL Rule (sentinel-correlation-rule.kql)
  ↓
  Emits customDetails (JSON payload)
  ↓
Sentinel Automation Rule Trigger
  ↓
Azure Logic Apps Playbook
  ├─ Parse JSON
  ├─ Enrich (VirusTotal, AbuseIPDB, Entra ID)
  ├─ Format alert (telegram-formatter.js)
  └─ Send to Telegram Bot API
```

### Pattern 2: Azure Functions → Telegram

```text
HTTP Trigger
  ↓
Parse JSON payload
  ↓
format_telegram_alert(payload)
  ↓
POST to https://api.telegram.org/bot{TOKEN}/sendMessage
```

### Pattern 3: Lambda / Cloud Functions → Telegram

```text
SNS/Pub-Sub Trigger
  ↓
Node.js handler
  ↓
const { formatTelegramAlert } = require('./telegram-formatter')
  ↓
Send Telegram message
```

---

## 🔒 Security Best Practices

1. **Secrets Management**
   -Store `BOT_TOKEN`, `CHAT_ID` in Azure Key Vault / AWS Secrets Manager
   -Never commit credentials to git

2. **Schema Validation**
   -Always validate incoming payloads against schema.json
    Reject non-conformant alerts (strict mode enforced)

3. **Telegram Markdown Escaping**
   -All user-controlled text must be escaped via `escapeTelegramMarkdown()`
   -Prevents markdown injection and rendering errors

4. **Access Control**
    Restrict Telegram bot to authorized security team only
    Use attestation for Sentinel rule triggers
   -Implement IP whitelisting where possible

5 **Data Retention & Audit**
  Log all alerts to Log Analytics for compliance
 Retain for regulatory requirements (SOX, HIPAA, PCI-DSS, etc.)
**Rate Limiting**
 Telegram API: ~30 messages/sec per bot
  Implement exponential backoff for retries
  Queue high-volume alerts if necessary

---

## 📖 Validation

### Validate Schema

```bash
npm run validate```
**Output:** ```
🔍 Validating Identity Threat Alert Payload...
✅ Schema example is VALID!
📋 Alert Type: identity_compromise
📣 Severity: critical
👤 User: ceo@company.com
⚠️ Event Type: mfa_fatigue_attack
🧩 Risk Detections: 3 found
```

### Custom Validation

```bash
npm run validate my-alert.json
```

---

## 🛠️ Deployment Examples

### Azure Logic Apps

1.Create new Automation Rule in Sentinel
2 Trigger: "When Microsoft Sentinel Incident is created"
3 Add action: "Send to Logic App"
4 In Logic App:
Parse JSON (body: @{triggerBody()?['customDetails']})
   ↓
Compose (use telegram-formatter.js)
   ↓
HTTP POST to Telegram

```### AWS Lambda

```python

import json
import os
import requests
from telegram_formatter import format_telegram_alert

def lambda_handler(event, context):
    try:
        payload = json.loads(event.get('body', '{}'))
        message = format_telegram_alert(payload)
        
        response = requests.post(
            f'https://api.telegram.org/bot{os.environ["BOT_TOKEN"]}/sendMessage',
            json={
                'chat_id': os.environ['CHAT_ID'],
                'text': message,
                'parse_mode': 'MarkdownV2'
            },
            timeout=10
        )
        
        return {
            'statusCode': 200 if response.ok else 500,
            'body': json.dumps({'message': 'Alert sent' if response.ok else response.text})
        }
    except Exception as e:
        print(f'Error: {str(e)}')
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
```

### Azure Functions (Python)

```python
import azure.functions as func
import json
from telegram_formatter import format_telegram_alert

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        payload = req.get_json()
        message = format_telegram_alert(payload)
        
        # Send to Telegram using requests library
        import requests
        requests.post(
            f'https://api.telegram.org/bot{...}/sendMessage',
            json={'chat_id': '...', 'text': message, 'parse_mode': 'MarkdownV2'}
        )
        
        return func.HttpResponse('OK', status_code=200)
    except Exception as e:
        return func.HttpResponse(str(e), status_code=500)
```

---

## 🧪 Testing

### Unit Test Example (Jest)

```javascript
const { formatTelegramAlert, escapeTelegramMarkdown } = require('./telegram-formatter');

describe('telegram-formatter', () => {
  test('escapes markdown special characters', () => {
    expect(escapeTelegramMarkdown('hello_world')).toBe('hello\\_world');
    expect(escapeTelegramMarkdown('a*b')).toBe('a\\*b');
  });

  test('formats alert with severity emoji', () => {
    const alert = {
      severity: 'critical',
      user: { email: 'test@example.com' },
      // ... other required fields
    };
    const msg = formatTelegramAlert(alert);
    expect(msg).toContain('🔴');
  });
});
```

---

## 📊 Monitoring & Observability

Monitor your alerting pipeline:

1. **Success Rate** - % of alerts reaching Telegram (target: 99.9%)
2. **Latency** - Time from Sentinel detection to Telegram delivery (target: <30s)
3. **Alert Volume** - Alerts/hour, trend analysis
4. **Schema Violations** - Invalid payloads (should be 0%)
5. **Formatter Errors** - Markdown escaping failures

Log to Application Insights / CloudWatch with custom dimensions:

- `alert_type`, `severity`, `source_system`, `timestamp`

---

## 🔄 Version Management

Update process:

1. Modify `schema.json` first
2. Regenerate `types.ts` (or update manually)
3. Test all formatters
4. Update metadata `pipeline_version`
5. Test end-to-end
6. Deploy

---

## 📞 Troubleshooting

| Issue | Solution |
|-------|----------|

|Telegram markdown render errors | Use `escapeTelegramMarkdown()` on all inputs |
|Schema validation fails | Check required fields, formats (email, uuid, uri) |
|Links not clickable in Telegram | Use proper markdown: `[text](url)` |
|High latency | Check SOAR playbook complexity, network latency |
|Missing alerts | Verify Sentinel rule enabled, custom details populated |

---

## 📝 Files Reference

- `schema.json` - JSON Schema (Draft 7) with example
- `openapi.yaml` - OpenAPI 3.0.3 specification
- `types.ts` - TypeScript interfaces
- `telegram_formatter.py` - Python formatter
- `telegram-formatter.js` - Node.js formatter
- `sentinel-correlation-rule.kql` - Sentinel KQL rule
- `validate.js` - AJV validation script
- `package.json` - NPM dependencies
- `README.md` - This file

---

## 📄 License

Provided as-is for security operations use. Follow your organization's policies.

---

## 🎯 Next Steps

1. ✅ Review alert structure and schema
2. ✅ Deploy Sentinel KQL correlation rule
3. ✅ Create Azure Logic App playbook
4. ✅ Get Telegram bot token from @BotFather
5. ✅ Test end-to-end with schema example payload
6. ✅ Deploy to production
7. ✅ Monitor success rate and latency
8. ✅ Tune MFA fatigue threshold if needed

---

**Version:** 1.0.0  
**Last Updated:** 2026-04-25  
**Maintained By:** Security Operations Center
