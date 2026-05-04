// stress_test_injector.js
// Usage: node stress_test_injector.js

const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:8000/ws/telemetry');

ws.on('open', function open() {
  const mockIncident = {
    id: 'test-incident-001',
    coords: [37.7749, -122.4194], // Example: San Francisco
    severity: 'critical',
    timestamp: new Date().toISOString(),
    metadata: {
      source: 'RedTeamSim',
      description: 'Unauthorized Egress Detected'
    }
  };
  ws.send(JSON.stringify(mockIncident));
  ws.close();
});

ws.on('error', function error(err) {
  console.error('WebSocket error:', err);
});
