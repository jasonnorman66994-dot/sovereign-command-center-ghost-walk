// batch_click_simulator.js
// Usage: node batch_click_simulator.js
// This script reads a CSV of targets and opens each phishing link in the default browser (with a delay)

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const csvPath = path.join(__dirname, 'Wave_3_Targets.csv');
const baseUrl = 'http://localhost:3000/auth';
const delayMs = 500; // 0.5s between opens

function parseCsv(csv) {
  // Assumes CSV has headers: ID,Email,TargetID
    const lines = csv.trim().split('\n');
    const headers = lines[0].split(',');
    return lines.slice(1).map(line => {
      const values = line.split(',');
      if (values.length !== headers.length) return null;
      const obj = {};
      headers.forEach((h, i) => obj[h.trim()] = (values[i] || '').trim());
      return obj;
    }).filter(Boolean);
}

function openLink(url) {
  // Windows: start, Mac: open, Linux: xdg-open
  const opener = process.platform === 'win32' ? 'start' : (process.platform === 'darwin' ? 'open' : 'xdg-open');
  exec(`${opener} "${url}"`);
}

function main() {
  if (!fs.existsSync(csvPath)) {
    console.error('Target CSV not found:', csvPath);
    process.exit(1);
  }
  const csv = fs.readFileSync(csvPath, 'utf-8');
  const targets = parseCsv(csv);
  let i = 0;
  function next() {
    if (i >= targets.length) return;
    const t = targets[i++];
    // Map CSV columns to expected query params
    const url = `${baseUrl}?tid=${encodeURIComponent(t.TargetID)}&wsid=${encodeURIComponent(t.ID)}&user=${encodeURIComponent(t.Email)}`;
    console.log('Opening:', url);
    openLink(url);
    setTimeout(next, delayMs);
  }
  next();
}

main();
