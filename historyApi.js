// historyApi.js
const express = require('express');
const Database = require('better-sqlite3');
const router = express.Router();
const db = new Database('harvest_events.db');

// GET /api/v1/history - returns all Credential_Harvest events in chronological order
router.get('/api/v1/history', (req, res) => {
  try {
    const rows = db.prepare(`
      SELECT timestamp, target_email, source_ip, user_agent, domain_used
      FROM credential_harvest
      ORDER BY timestamp ASC
    `).all();
    res.json({ success: true, events: rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

module.exports = router;
