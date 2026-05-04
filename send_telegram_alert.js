// send_telegram_alert.js
// Sends a formatted alert to your Telegram bot using your token and chat ID

const fs = require('fs');
const https = require('https');
const { formatTelegramAlert } = require('./telegram-formatter');

// === CONFIGURATION ===
require('dotenv').config();
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;
if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) {
  console.error('❌ TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set as environment variables or in a .env file.');
  process.exit(1);
}
const PAYLOAD_FILE = process.argv[2] || 'example-alert-filled.json';

// === MAIN ===
function sendTelegramMessage(message) {
  const data = JSON.stringify({
    chat_id: TELEGRAM_CHAT_ID,
    text: message,
    parse_mode: 'MarkdownV2',
    disable_web_page_preview: true
  });

  const options = {
    hostname: 'api.telegram.org',
    path: `/bot${TELEGRAM_BOT_TOKEN}/sendMessage`,
    method: 'POST',
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Content-Length': Buffer.byteLength(data, 'utf8')
    }
  };

  const req = https.request(options, res => {
    let body = '';
    res.setEncoding('utf8');
    res.on('data', chunk => body += chunk);
    res.on('end', () => {
      if (res.statusCode === 200) {
        console.log('✅ Alert sent to Telegram!');
      } else {
        try {
          console.error('❌ Telegram API error:', res.statusCode, body);
        } catch (unicodeErr) {
          console.error('[Unicode Error] Telegram API error (see log for details)');
        }
      }
    });
  });

  req.on('error', error => {
    try {
      console.error('❌ Request error:', error);
    } catch (unicodeErr) {
      console.error('[Unicode Error] Request error (see log for details)');
    }
  });

  req.write(data, 'utf8');
  req.end();
}

try {
  const payload = JSON.parse(fs.readFileSync(PAYLOAD_FILE, 'utf8'));
  const message = formatTelegramAlert(payload);
  sendTelegramMessage(message);
} catch (err) {
  console.error('❌ Error:', err.message);
  process.exit(1);
}
