// geo_lookup.js
// Minimal mock for testing anomaly detection
module.exports = async function(ip) {
  // Always return a non-LA location for geo-anomaly simulation
  return {
    city: 'Moscow',
    region: 'RU',
    country: 'Russia',
    ip: ip
  };
};
