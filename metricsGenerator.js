// metricsGenerator.js (Node.js)
const Database = require('better-sqlite3');
const db = new Database('harvest_events.db');

// Conversion Rate: (Yellow Hits / Cyan Hits) * 100
const cyanHits = db.prepare("SELECT COUNT(*) AS n FROM credential_harvest WHERE stage = 'page_load'").get().n;
const yellowHits = db.prepare("SELECT COUNT(*) AS n FROM credential_harvest WHERE stage = 'interaction'").get().n;
const conversionRate = cyanHits ? ((yellowHits / cyanHits) * 100).toFixed(2) : '0.00';

// Infrastructure Agility: Average Switchover Gap (assume switchover_gap column in seconds)
const gapRows = db.prepare("SELECT switchover_gap FROM credential_harvest WHERE switchover_gap IS NOT NULL").all();
const avgGap = gapRows.length ? (gapRows.reduce((a, b) => a + b.switchover_gap, 0) / gapRows.length).toFixed(2) : 'N/A';

// Success Rate: Total harvested tokens vs. emails sent (assume 'harvested' stage and emails_sent table)
const harvested = db.prepare("SELECT COUNT(*) AS n FROM credential_harvest WHERE stage = 'harvested'").get().n;
const emailsSent = db.prepare("SELECT COUNT(*) AS n FROM emails_sent").get().n;
const successRate = emailsSent ? ((harvested / emailsSent) * 100).toFixed(2) : '0.00';

console.log(`Conversion Rate: ${conversionRate}%`);
console.log(`Infrastructure Agility (Avg Switchover Gap): ${avgGap} seconds`);
console.log(`Success Rate: ${successRate}%`);
