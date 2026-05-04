// server.js
const express = require('express');
// const path = require('path'); (removed duplicate)
const path = require('path');
const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http, { cors: { origin: '*' } });
const PORT = 3000;
const fs = require('fs');
const crypto = require('crypto');
const remediation = require('./remediation_handler');

// Root route for status
app.get('/', (req, res) => {
  res.send('Server is running. Use /auth for credential simulation.');
});



// --- High-Volume Campaign State ---
const capturedWsids = new Set();
let totalDispatched = 50; // Set to your campaign size
let sessionHarvestCount = 0;

app.get('/auth', (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  const { tid, wsid, user } = req.query;
  // Simulate a JWT for session token, hash with Argon2-like string for demo
  const jwtPayload = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.' + crypto.randomBytes(12).toString('hex') + '.signature';
  // Fake Argon2 hash (for demo, not real Argon2)
  const sessionToken = jwtPayload + '.argon2$' + crypto.randomBytes(8).toString('hex');
  const ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
  const userAgent = req.headers['user-agent'] || 'unknown';
  const timestamp = new Date().toISOString();
  let isReentry = false;

  // Extract segment from wsid (e.g., QA-WS-554 => QA)
  let segment = 'UNKNOWN';
  if (wsid && wsid.includes('-')) {
    segment = wsid.split('-')[0];
  }

  // Build identity metadata object for logging
  const identityLog = {
    event: capturedWsids.has(wsid) ? 'Re-entry' : 'Credential Exfiltration',
    TargetID: tid || 'unknown',
    WorkstationID: wsid || 'unknown',
    User: user || 'unknown',
    Segment: segment,
    SessionToken: sessionToken,
    SourceIP: ip,
    UserAgent: userAgent,
    Timestamp: timestamp
  };

  if (capturedWsids.has(wsid)) {
    isReentry = true;
  } else {
    capturedWsids.add(wsid);
    sessionHarvestCount++;
  }

  // Append as JSON object to log
  fs.appendFile('send_gmail_test.log', JSON.stringify(identityLog) + '\n', err => {
    if (err) console.error('Log write error:', err);
  });

  // --- Automated Remediation Logic ---
  remediation.revokeSessionToken(sessionToken);
  const wsStatus = remediation.isolateWorkstation(wsid);
  const socMsg = remediation.notifySOC(user, wsid, sessionToken);

  if (!isReentry) {
    // Emit to global namespace (Yellow Arc)
    io.of('/').emit('threat-detected', { tid, wsid, user, time: new Date().toISOString() });
  }
  // Emit workstation isolation event for HUD
  io.of('/').emit('workstation-isolated', wsStatus);
  // Emit SOC notification for dashboard
  io.of('/').emit('soc-alert', { message: socMsg, time: new Date().toISOString() });
  // Emit session harvest counter for HUD (IDENTITY HARVEST)
  io.of('/').emit('threat-update', { sessionHarvestCount, total: totalDispatched });
  // Emit threat-detected for Yellow Arc
  io.of('/').emit('threat-detected', { tid, wsid, user, time: new Date().toISOString() });

  // Campaign Health Status every 10 unique hits
  if (!isReentry && sessionHarvestCount % 10 === 0) {
    const statusMsg = `\n[Red Team] [Campaign Health Status] Credential Exfiltration Attempts: ${sessionHarvestCount} / ${totalDispatched} (${((sessionHarvestCount/totalDispatched)*100).toFixed(1)}%)\n`;
    console.log(statusMsg);
  }

  // Serve landing page using path.join
  res.sendFile(path.join(__dirname, 'success.html'));
});


// Serve the PDF file for download
app.get('/pdf', (req, res) => {
  const filePath = __dirname + '/remediation_roadmap.pdf';
  res.download(filePath, 'remediation_roadmap.pdf');
});

// Simple Security Verification Success page with auto-download
app.get('/success', (req, res) => {
  // If a static HTML file exists, serve it; otherwise, fallback to inline HTML
  const successHtmlPath = path.join(__dirname, 'success.html');
  if (fs.existsSync(successHtmlPath)) {
    res.sendFile(successHtmlPath);
  } else {
    res.send(`
      <html>
        <head>
          <title>Security Verification</title>
          <script>
            setTimeout(function() {
              window.location.href = '/pdf';
            }, 1200);
          </script>
        </head>
        <body>
          <h2 style="color:green;">Security Verification Successful</h2>
          <p>Your credentials have been verified and your workstation is now compliant.</p>
          <p><b>Your download will begin automatically. If not, <a href="/pdf">click here</a>.</b></p>
        </body>
      </html>
    `);
  }
});

// Print the last generated phishing URL for route verification
console.log('DEBUG: Example phishing URL: http://localhost:3000/auth?tid=DEBUG-001&wsid=WS-DEBUG&user=testuser');

// Dead Man's Switch: GLOBAL_PURGE_REQUEST event
io.on('connection', (socket) => {
  socket.on('GLOBAL_PURGE_REQUEST', () => {
    const logPath = path.join(__dirname, 'send_gmail_test.log');
    // Read all log entries, update with [STATUS: REVOKED] for each JSON object
    let logData = '';
    try {
      logData = fs.readFileSync(logPath, 'utf-8');
    } catch (e) { logData = ''; }
    const updated = logData.split('\n').map(line => {
      if (!line.trim()) return '';
      try {
        const obj = JSON.parse(line);
        obj.STATUS = 'REVOKED';
        return JSON.stringify(obj);
      } catch {
        return line;
      }
    }).join('\n');
    fs.writeFileSync(logPath, updated + '\n');
    const criticalMsg = '[!] SOVEREIGN PURGE ACTIVATED - ALL SESSIONS TERMINATED.';
    fs.appendFileSync(logPath, criticalMsg + '\n');
    console.log(criticalMsg);
    // Broadcast SYSTEM_LOCKDOWN to all clients with overlay
    io.of('/').emit('SYSTEM_LOCKDOWN', { overlay: 'SYSTEM ISOLATED', color: 'crimson' });
    // Broadcast session harvest counter as NEUTRALIZED
    io.of('/').emit('threat-update', { sessionHarvestCount, total: totalDispatched, neutralized: true });
  });
});

// Start HTTP and WebSocket server
http.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});
