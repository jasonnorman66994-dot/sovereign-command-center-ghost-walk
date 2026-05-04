# Identity Threat Alert System - Deployment Guide

## 📋 File Manifest

| File | Purpose | Language |
| ------ | --------- | ---------- |
| `schema.json` | JSON Schema (Draft 7) for validation | JSON |
| `openapi.yaml` | OpenAPI 3.0.3 specification | YAML |
| `types.ts` | TypeScript interfaces for type safety | TypeScript |
| `telegram_formatter.py` | Telegram message formatter | Python |
| `telegram-formatter.js` | Telegram message formatter | JavaScript/Node.js |
| `sentinel-correlation-rule.kql` | Multi-event detection rule | KQL |
| `soar-playbook-logic.json` | SOAR/Logic Apps playbook steps | JSON |
| `example-alert-filled.json` | Example alert with realistic data | JSON |
| `validate.js` | Schema validation CLI | Node.js |
| `package.json` | NPM dependencies and scripts | JSON |
| `README.md` | Full documentation | Markdown |

---

## 🚀 5-Minute Setup

### Prerequisites

- Node.js >= 14
- Python >= 3.8 (optional, for Python formatter)
- Azure Sentinel workspace
- Telegram bot token (get from @BotFather)

### Step 1: Install & Validate

```bash
cd /path/to/workspace
npm install
npm run validate
```

**Expected Output:**

```bash
✅ Schema example is VALID!
```

### Step 2: Deploy Sentinel Rule

1. Open Azure Sentinel
2. Analytics Rules → Create rule
3. Paste contents of `sentinel-correlation-rule.kql`
4. Configure:
   - Query: (paste entire KQL)
   - Alert name: "Multi-Event Identity Threat Correlation"
   - Severity: High
   - Enabled: Yes
5. Click Create

### Step 3: Create SOAR Playbook

1. Azure Logic Apps → Create blank logic app
2. Trigger: "When Microsoft Sentinel incident is created"
3. Actions: Follow steps in `soar-playbook-logic.json`
4. Store secrets in Key Vault:
   - `telegram-bot-token`
   - `telegram-soc-chat-id`
5. Link to Sentinel automation rule

### Step 4: Test End-to-End

```bash
# Test formatter with example data
python telegram_formatter.py example-alert-filled.json

# Or with Node.js
node telegram-formatter.js example-alert-filled.json
```

### Step 5: Go Live

1. Enable the Sentinel rule
2. Link Logic App playbook
3. Monitor Telegram for incoming alerts
4. Check Application Insights / Log Analytics logs

---

## 🔌 Integration Checklist

### Sentinel Configuration

- [ ] KQL rule deployed and enabled
- [ ] customDetails populated with parsed JSON
- [ ] Rule testing shows correct detection
- [ ] Automation rule linked to SOAR playbook

### SOAR/Logic Apps Setup

- [ ] Trigger configured for Sentinel incidents
- [ ] JSON parsing with schema validation
- [ ] API keys stored in Key Vault
- [ ] Telegram formatter integrated
- [ ] Error handling and retries configured
- [ ] Log Analytics logging enabled

### Telegram Bot

- [ ] Bot token stored securely
- [ ] Chat ID restricted to authorized team
- [ ] Test message received successfully
- [ ] MarkdownV2 parsing working

### Monitoring (Pipeline)

- [ ] Application Insights alerts configured
- [ ] Log Analytics dashboard created
- [ ] Success rate tracked (target: 99.9%)
- [ ] Latency monitored (target: <30s)
- [ ] Alert volume tracked daily

---

## 📞 Quick Reference: Common Deployments

### Deployment A: Minimal (Sentinel → Telegram Only)

```text
1. Deploy KQL rule (sentinel-correlation-rule.kql)
2. Create Azure Function with HTTP trigger
3. Input: Sentinel webhook
4. Action: formatTelegramAlert()
5. Output: POST to Telegram API
```

**Pros:** Simple, fast  
**Cons:** No enrichment, no ticketing

### Deployment B: Standard (Sentinel → Logic Apps → Telegram + Jira)

```text
1. Deploy KQL rule
2. Create Logic App playbook (soar-playbook-logic.json)
3. Enrich IP, user data
4. Format message
5. Send Telegram + create ticket
```

**Pros:** Enriched alerts, ticketing, audit trail  
**Cons:** More complexity, latency

### Deployment C: Enterprise (Sentinel → SOAR → Multiple Destinations)

```text
1. Deploy KQL rule
2. Connect to enterprise SOAR (Cortex XSOAR, Splunk SOAR, etc.)
3. Use playbook logic as blueprint
4. Send to: Telegram, Slack, email, ServiceNow, Datadog
```

**Pros:** Centralized, flexible, scalable  
**Cons:** Requires SOAR platform

---

## 🧪 Testing Scenarios

### Test 1: Validate Schema

```bash
npm run validate
# Should pass ✅
```

### Test 2: Custom Alert Validation

```bash
npm run validate example-alert-filled.json
# Should pass ✅
```

### Test 3: Telegram Formatting

```bash
python telegram_formatter.py example-alert-filled.json
# Should show formatted message with emojis
```

### Test 4: End-to-End (Manual)

1. Trigger a test alert in Sentinel
2. Check Telegram receives message
3. Verify message contains all expected fields
4. Click investigation links (should work)
5. Check Log Analytics for audit entry

---

## 🔐 Security Hardening

### Secrets

- [ ] Never commit credentials to git
- [ ] Use Azure Key Vault / AWS Secrets Manager
- [ ] Rotate API keys quarterly
- [ ] Use managed identity where possible

### Access Control

- [ ] Restrict Sentinel rule trigger to authorized users
- [ ] Telegram bot access limited to SOC team only
- [ ] SOAR playbook execution requires audit logging
- [ ] API calls have IP whitelisting

### Data Protection

- [ ] TLS 1.2+ for all API calls
- [ ] Telegram bot uses HTTPS only
- [ ] Log Analytics retention: min 90 days
- [ ] Sensitive data (passwords, tokens) redacted from logs

### Monitoring

- [ ] Alert on failed schema validation
- [ ] Alert on formatter errors
- [ ] Alert on Telegram delivery failures
- [ ] Monitor API rate limit usage

---

## 📊 SLA & Metrics

| Metric | Target | Alert Threshold |
| -------- | -------- | ----------------- |
| Detection Latency | <10s | >20s |
| SOAR Processing | <15s | >30s |
| Telegram Delivery | <5s | >10s |
| **End-to-End** | **<30s** | **>60s** |
| Success Rate | 99.9% | <99% |
| Message Quality | 100% formatted correctly | >1 parse error/day |

---

## 📝 Maintenance Schedule

### Weekly

- [ ] Check alert volume and trends
- [ ] Review and resolve any formatting errors
- [ ] Test Telegram bot connectivity

### Monthly

- [ ] Review MFA fatigue threshold (adjust if needed)
- [ ] Analyze false positives
- [ ] Update example payloads if schema changes
- [ ] Rotate API keys

### Quarterly

- [ ] Full end-to-end test with all integrations
- [ ] Update documentation
- [ ] Review and update KQL rule performance
- [ ] Security audit of credentials

---

## 🆘 Troubleshooting

### "Schema validation fails"

1. Check `schema.json` is valid JSON
2. Verify all required fields present
3. Check field types match schema
4. Validate UUIDs and email formats

### "Telegram message formatting errors"

1. Ensure `escapeTelegramMarkdown()` called on all text
2. Check markdown special characters not double-escaped
3. Verify links use `[text](url)` format
4. Test with simple text first

### "Slow alert delivery"

1. Check SOAR playbook performance
2. Monitor API enrichment latency
3. Review network connectivity
4. Check Sentinel query performance

### "Alerts not appearing"

1. Verify Sentinel rule enabled
2. Check customDetails populated
3. Confirm Logic App playbook active
4. Validate Telegram bot token
5. Check Key Vault permissions

---

## 📞 Support Contacts

- **Sentinel Rule Issues**: Azure Support
- **Logic Apps Issues**: Azure Support
- **Telegram Bot Issues**: Telegram Bot Support (@BotFather)
- **Schema/Validation Issues**: Development team
- **SOAR Integration**: Internal SOAR team

---

## 📚 Additional Resources

- [JSON Schema Specification](https://json-schema.org/)
- [OpenAPI 3.0 Documentation](https://spec.openapis.org/oas/v3.0.3)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Microsoft Sentinel KQL](https://docs.microsoft.com/en-us/azure/sentinel/kusto-overview)
- [Azure Logic Apps Documentation](https://docs.microsoft.com/en-us/azure/logic-apps/)

---

**Version:** 1.0.0  
**Last Updated:** 2026-04-25  
**Status:** Production Ready
