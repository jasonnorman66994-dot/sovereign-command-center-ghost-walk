# 🎯 Identity Threat Alert System - Complete Reference

> **Production-ready SOC alerting solution for identity compromise, MFA-bypass, and endpoint threats**

---

## 📦 What You Have

### Core Validation & Documentation (4 files)

1. **schema.json** — JSON Schema (Draft 7) with strict validation

- 10+ required fields
- Type constraints, format validation
- Example payload included
- Use: CI/CD, data contracts, validation

1. **openapi.yaml** — OpenAPI 3.0.3 API specification

- POST /alerts endpoint documented
- RequestBody validation
- Use: Generate SDKs, API docs

1. **types.ts** — TypeScript interfaces

- Type-safe alert generation
- 10+ exported types + utilities
- IDE autocompletion
- Use: Node.js, Next.js, Lambda

1. **README.md** — Full documentation

- Integration patterns
- Deployment guides

1. **sentinel-correlation-rule.kql** — Sentinel analytics rule

### Formatters (2 files)

- Markdown escaping

1. **telegram-formatter.js** — Node.js Telegram formatter

- CommonJS + ES6 exports
- Zero dependencies
- Same functionality as Python
- Use: Lambda, Cloud Functions, Azure Functions

### SOAR/Automation (2 files)

1. **soar-playbook-logic.json** — Detailed SOAR playbook steps

- 11 sequential steps from trigger to response
- Enrichment (VirusTotal, AbuseIPDB, Entra ID)
- Error handling with fallbacks
- Use: Blueprint for Logic Apps, SOAR platforms

1. **DEPLOYMENT.md** — Step-by-step deployment guide

- 5-minute quick start
- Integration checklist
- 3 deployment models (minimal, standard, enterprise)
- Testing scenarios
- SLA & monitoring metrics

### Testing & Examples (3 files)

1. **example-alert-filled.json** — Realistic alert example

- CEO MFA fatigue attack scenario
- Use: Testing formatters, validators

1 **test_payloads.py** — Test payload generator

6 threat scenarios: MFA fatigue, OAuth abuse, impossible travel, legacy protocol, token replay, low severity
 CLI: `python test_payloads.py --scenario mfa_fatigue`
 Generate all scenarios: `python test_payloads.py --scenario all`

1 **validate.js** — Schema validation CLI
 Strict AJV validation
-Custom payload testing
-CLI: `npm run validate`

### Build & Configuration (2 files)

1 **package.json** — NPM dependencies & scripts

-ajv, ajv-formats (validation)
 redoc-cli, http-server (docs)
 Scripts: validate, redoc, swagger

1.**This file** — Complete reference and index

---

## 🚀 Quick Start (5 minutes)

### 1. Install

```bash
npm install

### 2. Validate

```bash
npm run validate
# ✅ Schema example is VALID!
```text

### 3. Test Formatters

```bash
python test_payloads.py --scenario mfa_fatigue > test_alert.json
python telegram_formatter.py test_alert.json
# Shows formatted Telegram message
```bash

### 4. Deploy Rule

- Copy `sentinel-correlation-rule.kql` into Sentinel Analytics Rules
- Configure and enable

### 5. Create Playbook

- Follow steps in `soar-playbook-logic.json`
- Deploy to Azure Logic Apps or SOAR platform

---

## 🔄 Alert Flow

```text
THREAT DETECTED

  └─ Correlates: MFA + Travel + OAuth + Protocol + Token + Device
customDetails JSON (matches schema.json)
  ↓
SOAR Playbook (soar-playbook-logic.json)
  ├─ Parse JSON (types.ts)
  ├─ Enrich (VirusTotal, AbuseIPDB, Entra ID)
  ├─ Format message (telegram_formatter.py)
  └─ Send to Telegram (Telegram Bot API)
  ↓
SOC TEAM RECEIVES ALERT
```

---

## 🛠️ Common Tasks

### Task: Generate Test Alert

```bash
python test_payloads.py --scenario oauth_abuse --output my-alert.json
```

### Task: Validate Alert

```bash
npm run validate my-alert.json
```

### Task: Format Alert for Telegram

```bash
python telegram_formatter.py my-alert.json

### Task: View API Docs

```bash
npm run start:redoc
# Opens http://localhost:8080 with ReDoc
```

### Task: Deploy to Sentinel

1. Open Sentinel → Analytics Rules → Create new
2. Configure: Alert name, Severity, Enabled
3. Create

4. Save and enable

---

## 📊 Alert Structure at a Glance

   "display_name": "User Name",                // string (required)
  "role": "Role",                             // string (required)
   "privileged_access": true                   // boolean (required)
  },
  
  "event": {
    "event_type": "mfa_fatigue_attack",         // string
    "source_ip": "185.221.102.44",              // IPv4 or IPv6
    "asn": "AS20860",                           // string
    "geo_location": "Bucharest, Romania",       // string
    "client_app": "Browser",                    // string
    "auth_method": "MFA Push",                  // string
    "risk_level": "high",                       // enum: low, medium, high
    "risk_detections": [...],                   // array of strings
    "correlation_id": "uuid",                   // UUID format
    "session_id": "session-123"                 // string
  },
  
  "technical_indicators": {
    "mfa_fatigue_count": 17,                    // integer
    "legacy_protocol_used": false,              // boolean
    "oauth_app_detected": true,                 // boolean
    "oauth_app_scopes": ["Mail.ReadWrite"],    // array
    "impossible_travel_detected": false,        // boolean
    "token_replay_detected": false              // boolean
    // ... more boolean indicators
  },
  
  "recommended_actions": [                      // array of strings
    "Revoke all active sessions",
    "Block the account",
    "Reset password"
  ],
  
  "investigation_links": {
    "signin_logs": "https://...",              // URL
    "oauth_apps": "https://...",               // URL
    "inbox_rules": "https://...",              // URL
    "sentinel_query": "https://...",           // URL
    "user_profile": "https://..."              // URL
  },
  
  "assigned_to": {
    "analyst": "@analyst_name",                // string
    "team": "Security Operations Center"       // string
  },
  
  "metadata": {
  
```bash
# MFA Fatigue
python test_payloads.py --scenario mfa_fatigue --output mfa-alert.json
npm run validate mfa-alert.json
python telegram_formatter.py mfa-alert.json

# OAuth Abuse
python test_payloads.py --scenario oauth_abuse

# Impossible Travel
python test_payloads.py --scenario impossible_travel

# Legacy Protocol
python test_payloads.py --scenario legacy_protocol

# Token Replay
python test_payloads.py --scenario token_replay

# Low Severity
python test_payloads.py --scenario low_severity

# All scenarios
python test_payloads.py --scenario all > all-scenarios.json
```

---

## 📞 File Dependencies

schema.json
├─ Used by: validate.js, OpenAPI docs
├─ Required for: CI/CD validation
└─ Example: Included in file

openapi.yaml
├─ Uses: schema.json (referenced)
├─ Used by: ReDoc, SwaggerUI
└─ Purpose: API documentation

types.ts
├─ Mirrors: schema.json structure
├─ Used by: TypeScript projects
└─ Manual sync: Update after schema changes

telegram_formatter.py

4.**Deploy** — Follow DEPLOYMENT.md 5-minute setup
5.**Monitor** — Check Application Insights for metrice
6.**Tune** — Adjust thresholds based on your environment

---

## 📚 File Manifest (Quick Reference)

| File | Type | Purpose | Size |
|------|------|---------|------|

| schema.json | JSON | Validation schema | ~5 KB |
| openapi.yaml | YAML | API spec | ~3 KB |
| types.ts | TypeScript | Type definitions | ~4 KB |
| telegram_formatter.py | Python | Message formatter | ~6 KB |
| telegram-formatter.js | JavaScript | Message formatter | ~5 KB |
| sentinel-correlation-rule.kql | KQL | Detection rule | ~7 KB |
| soar-playbook-logic.json | JSON | Playbook steps | ~8 KB |
| example-alert-filled.json | JSON | Example alert | ~2 KB |
| test_payloads.py | Python | Test generator | ~8 KB |
| validate.js | JavaScript | Validator | ~2 KB |
| DEPLOYMENT.md | Markdown | Deploy guide | ~10 KB |
| README.md | Markdown | Full docs | ~12 KB |
| package.json | JSON | NPM config | ~1 KB |
| **TOTAL** | — | **14 files** | **~73 KB** |

## 💡 Pro Tips

1. **Start minimal** — Deploy Model 1 first, add complexity gradually
2. **Test early** — Use `test_payloads.py` to validate before production
3. **Monitor metrics** — Track success rate, latency, alert volume
4. **Rotate secrets** — Quarterly API key rotation in Key Vault
5. **Document changes** — Update DEPLOYMENT.md when modifying rules
6. **Backup configs** — Version control your SOAR playbooks
7. **Use schema** — Never bypass JSON schema validation

---

## 🆘 Getting Help

- **Schema validation fails**: Check field types and required fields
- **Formatter errors**: Ensure inputs match schema exactly
- **Slow delivery**: Monitor SOAR playbook complexity
- **Telegram not working**: Verify bot token and chat ID in Key Vault
- **Sentinel rule issues**: Check KQL query syntax and table availability

---
