// Example: Dashboard integration stub
// This function would POST alert data to your dashboard API for real-time visualization
const fetch = require('node-fetch');
require('dotenv').config();

async function sendToDashboard(alert) {
    if (!process.env.DASHBOARD_API_URL) return;
    await fetch(process.env.DASHBOARD_API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(alert)
    });
}

module.exports = { sendToDashboard };
