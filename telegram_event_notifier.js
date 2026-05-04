const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');

const TELEGRAM_BOT_TOKEN = '8333246413:AAHuWsWj3I_Io-JpHZ3Gbwldmb60yiu2_bg';
const TELEGRAM_CHAT_ID = '7406674050';

// Example event object
const event = {
  status: '✅', // or '❌'
  user: 'jdoe',
  method: 'password',
  reason: 'Successful login',
  timestamp: new Date().toISOString()
};

// 1. Format the Telegram message
function formatTelegramMessage(event) {
  return `${event.status} *User:* ${event.user}\n*Method:* ${event.method}\n*Reason:* ${event.reason}\n*Time:* ${event.timestamp}`;
}

// 2. Send the summary message
async function sendTelegramMessage(text) {
  await axios.post(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
    chat_id: TELEGRAM_CHAT_ID,
    text,
    parse_mode: 'Markdown'
  });
}

// 3. Send the raw event log as a .txt file
async function sendTelegramDocument(filePath) {
  const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendDocument`;
  const formData = new FormData();
  formData.append('chat_id', TELEGRAM_CHAT_ID);
  formData.append('document', fs.createReadStream(filePath));
  await axios.post(url, formData, { headers: formData.getHeaders() });
}

// Example usage:
(async () => {
  // Write the raw event to a .txt file
  const logPath = './event_log.txt';
  fs.writeFileSync(logPath, JSON.stringify(event, null, 2));

  // Send the formatted message
  await sendTelegramMessage(formatTelegramMessage(event));

  // Send the raw log file
  await sendTelegramDocument(logPath);
})();
