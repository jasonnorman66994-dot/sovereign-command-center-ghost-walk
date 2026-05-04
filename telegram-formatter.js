/**
 * Identity Threat Alert Telegram Bot Formatter (Node.js)
 * Converts JSON payloads to SOC-friendly Telegram MarkdownV2 messages
 *
 * Usage:
 *   const { formatTelegramAlert } = require('./telegram-formatter');
 *   const message = formatTelegramAlert(payload);
 *
 * Or as CLI:
 *   node telegram-formatter.js payload.json
 */

/**
 * Escape Telegram MarkdownV2 special characters
 * @param {string|null} text - Text to escape
 * @returns {string} Escaped text safe for Telegram MarkdownV2
 */
function escapeTelegramMarkdown(text) {
  if (!text) return '';
  const specialChars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!'];
  return String(text).split('').map(char => 
    specialChars.includes(char) ? `\\${char}` : char
  ).join('');
}

/**
 * Get severity emoji indicator
 * @param {string} severity - Severity level (low, medium, high, critical)
 * @returns {string} Emoji indicator
 */
function getSeverityEmoji(severity) {
  const emojiMap = {
    'low': '🟢',
    'medium': '🟡',
    'high': '🟠',
    'critical': '🔴'
  };
  return emojiMap[severity?.toLowerCase()] || '⚪';
}

/**
 * Format risk detections as bulleted list
 * @param {string[]} detections - Array of detection strings
 * @returns {string} Formatted bulleted list
 */
function formatRiskDetections(detections) {
  if (!detections || detections.length === 0) {
    return '• No specific indicators detected';
  }
  
  const formatted = detections.slice(0, 5).map(d => 
    `• ${escapeTelegramMarkdown(d)}`
  );
  
  if (detections.length > 5) {
    formatted.push(`• \\+${detections.length - 5} more indicators`);
  }
  
  return formatted.join('\n');
}

/**
 * Format investigation links as inline markdown
 * @param {object} links - Investigation links object
 * @returns {string} Formatted links
 */
function formatInvestigationLinks(links) {
  const linkLabels = {
    'signin_logs': 'Sign\\-in Logs',
    'oauth_apps': 'OAuth Apps',
    'inbox_rules': 'Inbox Rules',
    'sentinel_query': 'Sentinel Query',
    'user_profile': 'User Profile'
  };
  
  const formatted = [];
  for (const [key, label] of Object.entries(linkLabels)) {
    if (links[key]) {
      formatted.push(`[${label}](${links[key]})`);
    }
  }
  
  // Telegram MarkdownV2 requires '|' to be escaped as '\|'
  return formatted.join(' \\| ');
}

/**
 * Convert Identity Threat Alert JSON payload to Telegram MarkdownV2 message
 * @param {object} payload - Alert payload object
 * @returns {string} Formatted message string
 */
function formatTelegramAlert(payload) {
  const user = payload.user || {};
  const event = payload.event || {};
  const tech = payload.technical_indicators || {};
  const links = payload.investigation_links || {};
  const assigned = payload.assigned_to || {};
  const severity = payload.severity || 'medium';
  
  const severityEmoji = getSeverityEmoji(severity);
  
  // Build message parts
  const messageParts = [
    `${severityEmoji} *IDENTITY SECURITY ALERT*`,
    'Potential account compromise detected\\.',
    '',
    `👤 *User:* ${escapeTelegramMarkdown(user.email)}`,
    `🆔 *User ID:* ${escapeTelegramMarkdown(user.user_id)}`,
    `🏢 *Department:* ${escapeTelegramMarkdown(user.department)}`,
    `🔐 *Role:* ${escapeTelegramMarkdown(user.role)}`,
    '',
    '\\-\\-\\-',
    '',
    `⚠️ *Event Type:* ${escapeTelegramMarkdown(event.event_type)}`,
    escapeTelegramMarkdown(event.description),
    '',
    `🕒 *Timestamp:* ${escapeTelegramMarkdown(payload.timestamp_utc)}`,
    `🌐 *Source IP:* ${escapeTelegramMarkdown(event.source_ip)}`,
    `🏢 *ASN / Location:* ${escapeTelegramMarkdown(event.asn)} / ${escapeTelegramMarkdown(event.geo_location)}`,
    `📱 *Client App:* ${escapeTelegramMarkdown(event.client_app)}`,
    `🔐 *Auth Method:* ${escapeTelegramMarkdown(event.auth_method)}`,
    '',
    '\\-\\-\\-',
    '',
    '*🧩 Risk Indicators:*',
    formatRiskDetections(event.risk_detections),
    '',
    '\\-\\-\\-',
    '',
    '*🛑 Immediate Response Actions:*'
  ];
  
  // Add recommended actions
  const actions = payload.recommended_actions || [];
  for (let i = 0; i < Math.min(actions.length, 6); i++) {
    messageParts.push(`${i + 1}\\. ${escapeTelegramMarkdown(actions[i])}`);
  }
  
  if (actions.length > 6) {
    messageParts.push(`\\+ ${actions.length - 6} additional actions`);
  }
  
  messageParts.push(
    '',
    '\\-\\-\\-',
    '',
    '*🛠️ Investigation Links:*',
    formatInvestigationLinks(links),
    '',
    '\\-\\-\\-',
    '',
    `*📣 Severity:* ${severityEmoji} ${escapeTelegramMarkdown(severity.toUpperCase())}`,
    `*👮 Assigned To:* ${escapeTelegramMarkdown(assigned.analyst)}`
  );
  
  return messageParts.join('\n');
}

/**
 * CLI entry point
 */
if (require.main === module) {
  const fs = require('fs');
  const path = require('path');
  
  if (process.argv.length < 3) {
    console.error('Usage: node telegram-formatter.js <payload.json>');
    process.exit(1);
  }
  
  try {
    const filePath = process.argv[2];
    const payload = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    const message = formatTelegramAlert(payload);
    console.log(message);
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

module.exports = {
  formatTelegramAlert,
  escapeTelegramMarkdown,
  getSeverityEmoji
};
