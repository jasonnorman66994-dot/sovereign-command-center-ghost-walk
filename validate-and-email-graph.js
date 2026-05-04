
require('dotenv').config();
const { ClientSecretCredential } = require("@azure/identity");
const { Client } = require("@microsoft/microsoft-graph-client");
require("isomorphic-fetch");
const Ajv = require("ajv");
const fs = require("fs");
const path = require("path");

// Microsoft Graph API credentials from environment variables
const tenantId = process.env.TENANT_ID;
const clientId = process.env.CLIENT_ID;
const clientSecret = process.env.CLIENT_SECRET;
const userEmail = process.env.USER_EMAIL;

if (!tenantId || !clientId || !clientSecret || !userEmail) {
  throw new Error("Missing required environment variables. Please check your .env file.");
}

const credential = new ClientSecretCredential(tenantId, clientId, clientSecret);

// Validation setup
const schema = require("./alert-v2-schema.json");
const ajv = new Ajv({ allErrors: true, strict: false });
const validate = ajv.compile(schema);

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

async function sendMail(subject, body) {
  const graphClient = Client.initWithMiddleware({
    authProvider: {
      getAccessToken: async () => {
        const token = await credential.getToken("https://graph.microsoft.com/.default");
        return token.token;
      }
    }
  });

  await graphClient.api('/users/' + userEmail + '/sendMail').post({
    message: {
      subject,
      body: { contentType: "Text", content: body },
      toRecipients: [{ emailAddress: { address: userEmail } }]
    }
  });

  console.log("Validation results sent via Microsoft Graph email!");
}

// Run validation and send email
sendMail("SOC Alert JSON Validation Results", summary);
