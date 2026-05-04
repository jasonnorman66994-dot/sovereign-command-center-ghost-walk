
# Identity Threat Detection Alert Schema (v2)

## Overview

This schema defines the structure for enriched identity threat alerts processed by the pipeline and delivered to Telegram and dashboards. It supports custom alert types and deep forensic context.

---

## Top-Level Fields

| Field        | Type   | Required | Description                                                    |
|--------------|--------|----------|----------------------------------------------------------------|
| timestamp    | string | Yes      | ISO 8601 UTC timestamp of the event                            |
| alertType    | string | Yes      | Canonical alert type (e.g., MFABypassAttempt, HiddenInboxRule) |
| severity     | string | Yes      | One of: Critical, High, Medium, Low                            |
| user         | string | Yes      | User principal (email or UPN)                                  |
| details      | string | Yes      | Human-readable summary of the alert                            |
| customType   | string | No       | Custom alert subtype for enrichment (e.g., ImpossibleTravel)   |
| extraContext | object | No       | Arbitrary key-value pairs for forensic enrichment              |

---

## Example

```json
{
  "timestamp": "2026-04-26T13:00:00Z",
  "alertType": "SuspiciousOAuthConsent",
  "severity": "Critical",
  "user": "bob@example.com",
  "customType": "OAuthAppConsent",
  "extraContext": {
    "appName": "EvilApp",
    "permissions": ["Mail.ReadWrite", "Files.ReadWrite.All"],
    "ip": "198.51.100.23",
    "country": "Russia"
  },
  "details": "User consented to a suspicious OAuth app with high privileges."
}
```

---

## Notes

- All fields not listed above are ignored by the pipeline.
- extraContext can include any forensic or contextual data (IPs, User-Agents, device IDs, etc.).
- customType is used for fine-grained alert classification and dashboard filtering.
- The schema is backward compatible: legacy alerts without customType/extraContext are still processed.

---

## Version

- v2 (April 2026): Initial release with enrichment support.
