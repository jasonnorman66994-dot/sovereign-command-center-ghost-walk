# Security Automation Platform Architecture

```mermaid
flowchart TD
    A[User Login / Activity] -->|Log| B(MySQL: auth_logs)
    B -->|Evaluated by| C[alert_rule_evaluator.py]
    C -->|Triggers| D[Alert Payload]
    D -->|Validated by| E[Schema: JSON/OpenAPI/TS]
    D -->|Webhook| F(alert_webhook.py)
    D -->|Lambda| G(alert_lambda.py)
    F -->|Format & Send| H[Telegram Bot]
    G -->|Format & Send| H
    D -->|SIEM/SOAR| I[Automation/Playbooks]
    B -->|Dashboard| J[PHP Dashboard]
    B -->|Reporting| K[generate_security_report.py]
    K -->|Boardroom| L[PDF/CSV/MD]
    subgraph CI/CD & Deployment
      M[GitHub Actions / Azure DevOps] --> N[Docker Image]
      N --> O[Kubernetes (AKS/EKS/GKE)]
      O --> F
      O --> G
    end
```

---

This diagram shows the end-to-end flow of your security automation platform, from user activity logging to alerting, validation, delivery, reporting, and CI/CD deployment.
