/**
 * Identity Threat Alert TypeScript Interfaces
 * Production-ready types for SOC automation and SOAR playbooks
 */

/**
 * Severity levels with emoji indicators
 */
export type AlertSeverity = 'low' | 'medium' | 'high' | 'critical';
export type AlertType = 'identity_compromise' | 'identity_endpoint_compromise';
export type SourceSystem = 'Sentinel' | 'Defender' | 'UEBA' | 'Custom';
export type Environment = 'production' | 'staging' | 'dev';
export type RiskLevel = 'low' | 'medium' | 'high';

/**
 * User information object
 */
export interface AlertUser {
  /** User's primary email / UPN */
  email: string;
  /** Azure AD / Entra ID user object ID */
  user_id: string;
  /** User's display name */
  display_name: string;
  /** Department from user profile */
  department: string;
  /** Job title or role */
  role: string;
  /** Whether user has privileged access (admin, executive, etc.) */
  privileged_access: boolean;
}

/**
 * Event details object
 */
export interface AlertEvent {
  /** Type of event: mfa_fatigue_attack, oauth_abuse, aitm, legacy_protocol, impossible_travel, token_replay, etc. */
  event_type: string;
  /** Human-readable summary of the event */
  description: string;
  /** Source IP address (IPv4 or IPv6) */
  source_ip: string;
  /** Autonomous System Number (e.g., AS20860) */
  asn: string;
  /** Geographic location string (e.g., Bucharest, Romania) */
  geo_location: string;
  /** Client application: Browser, IMAP, POP3, SMTP, OAuth app, etc. */
  client_app: string;
  /** Authentication method: Password, MFA Push, OTP, Token Replay, etc. */
  auth_method: string;
  /** Risk level assessment for this event */
  risk_level: RiskLevel;
  /** Array of detected risk indicators */
  risk_detections: string[];
  /** Unique correlation ID for tracing across systems (UUID format) */
  correlation_id: string;
  /** Associated session identifier */
  session_id: string;
}

/**
 * Technical indicators from detection engines
 */
export interface TechnicalIndicators {
  /** Number of MFA push prompts in the fatigue window */
  mfa_fatigue_count?: number;
  /** Whether legacy protocol (IMAP/POP3) was used */
  legacy_protocol_used?: boolean;
  /** Whether risky OAuth application consent detected */
  oauth_app_detected?: boolean;
  /** OAuth scopes requested (e.g., Mail.ReadWrite, offline_access) */
  oauth_app_scopes?: string[];
  /** Whether hidden inbox rules were created */
  hidden_inbox_rules_detected?: boolean;
  /** Whether impossible travel pattern detected */
  impossible_travel_detected?: boolean;
  /** Whether token replay or session hijacking pattern detected */
  token_replay_detected?: boolean;
  /** Whether new device was registered */
  new_device_registration?: boolean;
  /** Whether sign-in has unfamiliar properties */
  unfamiliar_signin_properties?: boolean;
  /** Associated device ID from Defender for Endpoint */
  device_id?: string;
  /** Device name / hostname */
  device_name?: string;
  /** Device risk score from Defender */
  device_risk?: RiskLevel;
  /** Associated device alert type if applicable */
  device_alert?: string;
}

/**
 * Investigation links to external systems
 */
export interface InvestigationLinks {
  /** Link to Entra ID Sign-in Logs */
  signin_logs: string;
  /** Link to OAuth Apps listing */
  oauth_apps: string;
  /** Link to Exchange inbox rules */
  inbox_rules: string;
  /** Link to Sentinel KQL query */
  sentinel_query: string;
  /** Link to user profile in Entra ID */
  user_profile: string;
}

/**
 * Assignment and team information
 */
export interface AssignedTo {
  /** On-call analyst or responder (can be @mention handle) */
  analyst: string;
  /** Team responsible for triage */
  team: string;
}

/**
 * Pipeline metadata
 */
export interface Metadata {
  /** Version of the alerting pipeline */
  pipeline_version: string;
  /** Source system that generated the alert */
  source_system: SourceSystem;
  /** Environment classification */
  environment: Environment;
}

/**
 * Main Identity Threat Alert payload
 * Production-ready schema for SOC automation
 */
export interface IdentityThreatAlert {
  /** Classification of the alert type */
  alert_type: AlertType;
  /** Alert severity: low (🟢), medium (🟡), high (🟠), critical (🔴) */
  severity: AlertSeverity;
  /** ISO 8601 UTC timestamp of the alert */
  timestamp_utc: string;
  /** User information object */
  user: AlertUser;
  /** Event details object */
  event: AlertEvent;
  /** Technical indicators from detection engines */
  technical_indicators: TechnicalIndicators;
  /** Prioritized IR response actions */
  recommended_actions: string[];
  /** Investigation links to external systems */
  investigation_links: InvestigationLinks;
  /** Assignment and team information */
  assigned_to: AssignedTo;
  /** Pipeline metadata */
  metadata: Metadata;
}

/**
 * Utility function to validate severity and return emoji
 */
export function getSeverityEmoji(severity: AlertSeverity): string {
  const emojiMap: Record<AlertSeverity, string> = {
    low: '🟢',
    medium: '🟡',
    high: '🟠',
    critical: '🔴'
  };
  return emojiMap[severity];
}

/**
 * Utility function to format timestamp for display
 */
export function formatTimestamp(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    timeZone: 'UTC',
    timeZoneName: 'short'
  });
}

/**
 * Utility function to escape Telegram MarkdownV2 special characters
 */
export function escapeTelegramMarkdown(text: string | null | undefined): string {
  if (!text) return '';
  return String(text)
    .replace(/[_*\[\]()~`>#\-+=|{}.!]/g, '\\$&');
}
