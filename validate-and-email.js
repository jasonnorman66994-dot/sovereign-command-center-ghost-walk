const Ajv = require('ajv');
const fs = require('fs');
const path = require('path');
const nodemailer = require('nodemailer');

const schema = require('./alert-v2-schema.json');
const ajv = new Ajv({ allErrors: true, strict: false });
const validate = ajv.compile(schema);

// List of files to validate (edit as needed)
const files = [
  'alert_aitm_phishing.json','alert_alice_aitm_phishing.json','alert_alice_mfa_fatigue.json','alert_alice_oauth_abuse.json','alert_bob_hidden_inbox_rules.json','alert_bob_infostealer.json','alert_bob_proxy_blocked.json','alert_bob_token_replay.json','alert_ceo_password_spray.json','alert_cfo_mfa_fatigue.json','alert_charlie_legacy_protocol.json','alert_charlie_social_engineering.json','alert_device_risk.json','alert_global_admin_01_password_spray.json','alert_hr_payroll_password_spray.json','alert_it_support_mfa_fatigue.json','alert_legacy_protocol.json','alert_user1_spam_phishing.json','alert_user2_infostealer.json','alert_user3_mfa_fatigue.json','alert_vip_impossible_travel.json','custom1_impossible_travel_token_theft.json','custom2_ransomware_precursor.json','custom3_admin_takeover.json','custom4_insider_threat.json','custom5_unmanaged_device.json','custom_alert.json','device_test.json','example-alert-filled.json','impossible_travel_test.json','impossible_travel_test_fixed.json','legacy_test.json','low_test.json','mfa_test.json','oauth_abuse_test.json','oauth_test.json','token_replay_test.json','token_replay_test_fixed.json'
];

let results = [];

files.forEach(file => {
  try {
    const data = JSON.parse(fs.readFileSync(path.join(__dirname, file), 'utf-8'));
    const valid = validate(data);
    if (valid) {
      results.push(`✅ ${file}: VALID`);
    } else {
      results.push(`❌ ${file}: INVALID\n${JSON.stringify(validate.errors, null, 2)}`);
    }
  } catch (err) {
    results.push(`❌ ${file}: ERROR\n${err.message}`);
  }
});

const summary = results.join('\n\n');

// SMTP config (edit with your Outlook credentials)
const transporter = nodemailer.createTransport({
  host: 'smtp.office365.com',
  port: 587,
  secure: false,
  auth: {
    user: 'jasonnorman66994@outlook.com',
    pass: 'Chidera4321'
  }
});

const mailOptions = {
  from: 'jasonnorman66994@outlook.com',
  to: 'jasonnorman66994@outlook.com', // or another recipient
  subject: 'SOC Alert JSON Validation Results',
  text: summary
};

transporter.sendMail(mailOptions, (error, info) => {
  if (error) {
    return console.error('Error sending email:', error);
  }
  console.log('Validation results sent:', info.response);
});
