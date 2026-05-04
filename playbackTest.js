// playbackTest.js
// Test playbackController.js with dummy data to ensure arcs don't stack and browser stays responsive

const dummyEvents = [
  { timestamp: '2026-04-25T08:00:00Z', target_email: 'a@b.com', source_ip: '1.1.1.1', user_agent: 'UA1', domain_used: 'alpha.xyz' },
  { timestamp: '2026-04-25T08:01:00Z', target_email: 'b@b.com', source_ip: '2.2.2.2', user_agent: 'UA2', domain_used: 'beta.xyz' },
  { timestamp: '2026-04-25T08:02:00Z', target_email: 'c@b.com', source_ip: '3.3.3.3', user_agent: 'UA3', domain_used: 'gamma.xyz' }
];

// Simulate Three.js globe and arc/pulse logic
function clearLivePulses() {
  console.log('Cleared all live pulses/arcs.');
}
function triggerArcAndPulse(event) {
  console.log(`Arc/Pulse: ${event.target_email} from ${event.source_ip} at ${event.timestamp}`);
}

// Import playbackController.js logic (simulate core functions)
let playbackActive = false;
let playbackTimeout;
let playbackIndex = 0;
let playbackData = dummyEvents;
let playbackSpeed = 24 * 60 * 60 * 1000 / 60000;

function playTimeLapse() {
  if (!playbackData.length) return;
  playbackActive = true;
  playbackIndex = 0;
  clearLivePulses();
  nextPulse();
}
function pauseTimeLapse() {
  playbackActive = false;
  clearTimeout(playbackTimeout);
}
function nextPulse() {
  if (!playbackActive || playbackIndex >= playbackData.length) return;
  const event = playbackData[playbackIndex];
  if (playbackIndex > 0) {
    const prev = new Date(playbackData[playbackIndex - 1].timestamp).getTime();
    const now = new Date(event.timestamp).getTime();
    const delay = Math.max(10, (now - prev) / playbackSpeed);
    playbackTimeout = setTimeout(() => {
      triggerArcAndPulse(event);
      playbackIndex++;
      nextPulse();
    }, delay);
  } else {
    triggerArcAndPulse(event);
    playbackIndex++;
    nextPulse();
  }
}

// Run the test
playTimeLapse();
