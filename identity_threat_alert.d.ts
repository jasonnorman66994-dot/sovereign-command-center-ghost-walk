export interface IdentityThreatAlert {
  alert_type: 'identity_compromise' | 'identity_endpoint_compromise';
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp_utc: string;
  user: {
    email: string;
    user_id: string;
    display_name?: string;
    department?: string;
    role?: string;
    privileged_access?: string | boolean;
  };
  event: {
    event_type: string;
    description: string;
    source_ip: string;
    asn?: string;
    geo_location?: string;
    client_app?: string;
    auth_method?: string;
    risk_level?: string;
    risk_detections?: string[];
    correlation_id?: string;
    session_id?: string;
  };
  technical_indicators?: {
    mfa_fatigue_count?: number | string;
    legacy_protocol_used?: boolean | string;
    oauth_app_detected?: boolean | string;
    oauth_app_scopes?: string[];
    hidden_inbox_rules_detected?: boolean | string;
    impossible_travel_detected?: boolean | string;
    token_replay_detected?: boolean | string;
    new_device_registration?: boolean | string;
    unfamiliar_signin_properties?: boolean | string;
  };
  recommended_actions: string[];
  investigation_links?: {
    signin_logs?: string;
    oauth_apps?: string;
    inbox_rules?: string;
    sentinel_query?: string;
    user_profile?: string;
  };
  assigned_to: {
    analyst: string;
    team?: string;
  };
  metadata?: {
    pipeline_version?: string;
    source_system?: string;
    environment?: string;
  };
}
