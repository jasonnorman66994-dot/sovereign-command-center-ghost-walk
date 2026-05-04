// Advanced deduplication using Redis set
const Redis = require('ioredis');
const redis = new Redis();
const DEDUP_SET = 'alertDedupSet';

async function isDuplicate(alert) {
    // Use a hash of username+password+campaign for uniqueness
    const key = `${alert.username}|${alert.password}|${alert.campaign || ''}`;
    const exists = await redis.sismember(DEDUP_SET, key);
    if (!exists) await redis.sadd(DEDUP_SET, key);
    return !!exists;
}

// Collapse repeated MFA fatigue attempts into a single incident
async function deduplicateMfaFatigue(alert) {
    if (alert.type !== 'MFA_FATIGUE') return false;
    const incidentKey = `mfaFatigue|${alert.username}|${alert.campaign || ''}`;
    const exists = await redis.sismember(DEDUP_SET, incidentKey);
    if (!exists) {
        await redis.sadd(DEDUP_SET, incidentKey);
        return false; // Not a duplicate, treat as new incident
    }
    return true; // Duplicate, suppress alert
}

// Utility: clear deduplication set for new rollouts
async function clearDedupSet() {
    await redis.del(DEDUP_SET);
}

module.exports = { isDuplicate, deduplicateMfaFatigue, clearDedupSet };
