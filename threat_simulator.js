// threat_simulator.js
// Modular threat simulation framework for pipeline testing and boardroom demos
// Usage: node threat_simulator.js <scenario>

const fs = require('fs');
const axios = require('axios');

const scenarios = {
  'geo-anomaly': () => ({
    user: 'testuser',
    ip: '203.0.113.99',
    location: 'Moscow, RU',
    event: 'login',
    risk: 'high',
    details: 'Login from unusual location'
  }),
  'credential-stuffing': () => ({
    user: 'targetuser',
    ip: '198.51.100.42',
    location: 'Unknown',
    event: 'multiple_failed_logins',
    risk: 'medium',
    details: 'Multiple failed login attempts detected'
  }),
  'session-hijack': () => ({
    user: 'vipuser',
    ip: '192.0.2.123',
    location: 'Berlin, DE',
    event: 'session_hijack',
    risk: 'critical',
    details: 'Session token used from new device'
  }),
  'insider-threat': () => ({
    user: 'employee42',
    ip: '10.0.0.55',
    location: 'HQ',
    event: 'privileged_access',
    risk: 'high',
    details: 'Unusual access to sensitive data'
  }),
  'privilege-escalation': () => ({
    user: 'serviceacct',
    ip: '172.16.0.10',
    location: 'Cloud',
    event: 'role_change',
    risk: 'critical',
    details: 'Service account granted admin privileges'
  }),
  'phishing-click': () => ({
    user: 'userphish',
    ip: '203.0.113.77',
    location: 'Remote',
    event: 'link_clicked',
    risk: 'medium',
    details: 'User clicked on suspicious link'
  }),
  'malware-beacon': () => ({
    user: 'infectedhost',
    ip: '198.51.100.99',
    location: 'Branch',
    event: 'beacon',
    risk: 'critical',
    details: 'Outbound connection to known C2 server'
  })
};

async function simulate(scenario, logFile = 'simulation_results.csv') {
  if (!scenarios[scenario]) {
    console.error('Unknown scenario. Available:', Object.keys(scenarios).join(', '));
    process.exit(1);
  }
  const payload = scenarios[scenario]();
  let result = { ...payload, status: 'pending', timestamp: new Date().toISOString() };
  try {
    const res = await axios.post('http://localhost:3000/telemetry', payload);
    result.status = 'sent';
    result.response = JSON.stringify(res.data);
    console.log('Simulation sent:', payload, '\nResponse:', res.data);
  } catch (err) {
    result.status = 'failed';
    result.response = err.message;
    console.error('Simulation failed:', err.message);
  }
  // Append result to CSV
  const header = 'timestamp,user,ip,location,event,risk,details,status,response\n';
  const line = `${result.timestamp},${result.user},${result.ip},${result.location},${result.event},${result.risk},"${result.details}",${result.status},"${result.response || ''}"\n`;
  if (!fs.existsSync(logFile)) {
    fs.writeFileSync(logFile, header);
  }
  fs.appendFileSync(logFile, line);
}

// Support batch mode: node threat_simulator.js batch scenario1 scenario2 ...
const args = process.argv.slice(2);
if (args[0] === 'batch') {
  (async () => {
    for (let i = 1; i < args.length; i++) {
      await simulate(args[i]);
      await new Promise(r => setTimeout(r, 1000)); // 1s delay between
    }
    console.log('Batch simulation complete. Results in simulation_results.csv');
  })();
} else if (args[0] === 'visualize') {
  // Simple visualization: print summary counts by scenario
  const logFile = 'simulation_results.csv';
  if (!fs.existsSync(logFile)) {
    console.log('No simulation results found.');
    process.exit(0);
  }
  const data = fs.readFileSync(logFile, 'utf8').split('\n').slice(1).filter(Boolean);
  const counts = {};
  for (const line of data) {
    const cols = line.split(',');
    const event = cols[4];
    counts[event] = (counts[event] || 0) + 1;
  }
  console.log('Simulation Results Summary:');
  for (const [event, count] of Object.entries(counts)) {
    console.log(`  ${event}: ${count}`);
  }
} else {
  simulate(args[0]);
}
