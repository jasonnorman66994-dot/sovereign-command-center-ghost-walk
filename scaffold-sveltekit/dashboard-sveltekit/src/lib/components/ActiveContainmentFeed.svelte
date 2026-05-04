
<script lang="ts">
import { onMount } from 'svelte';

interface ContainmentLog {
  id: number;
  pod_name: string;
  action_taken: string;
  timestamp_utc: string;
}

let showModal = $state(false);
let modalLog = $state(null);
let logs = $state([
  {
    id: 1,
    pod_name: 'Identity-Layer-01',
    action_taken: 'Unauthorized Token Rotation',
    timestamp_utc: new Date().toISOString(),
    status: 'QUARANTINED'
  }
]); // Injected mock event for Project Ghost-Walk simulation
let notification = $state('');
let processingId = $state(null);
let interval: NodeJS.Timeout;
let notificationTimeout: NodeJS.Timeout | null = null;

function openDefenseSummary(log: ContainmentLog) {
  modalLog = log;
  showModal = true;
}
function closeModal() {
  showModal = false;
  modalLog = null;
}

function downloadIncidentReport() {
  if (!modalLog) return;
  const lines = [
    `Defense Summary for Pod: ${modalLog.pod_name}`,
    '',
    `1. Detection: ${modalLog.timestamp_utc}`,
    `2. Anomaly Score: 4.5`,
    `3. Containment Action: K8s Label applied (status=quarantine)`,
    `4. Final Status: Success`
  ];
  const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `incident_report_${modalLog.pod_name}_${modalLog.id}.txt`;
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, 100);
}


// fetchLogs is disabled for UI stability. All API calls are bypassed.


// retryContainment is disabled for UI stability. All API calls are bypassed.
async function retryContainment(log: ContainmentLog) {
  notification = 'Containment retry is disabled in static mode.';
  if (notificationTimeout) clearTimeout(notificationTimeout);
  notificationTimeout = setTimeout(() => { notification = ''; }, 3000);
}


// onMount polling is disabled for UI stability. No API calls are made.
</script>

<div class="feed-container">
  <div class="feed-header">Active Containment Feed</div>
  {#if notification}
    <div class="notification">{notification}</div>
  {/if}
  <ul class="feed-list">
    {#each logs ?? [] as log (log.id)}
      <li class="feed-item {processingId === log.id ? 'blink' : ''}">
        <span class="pod">{log.pod_name}</span>
        <span class="action">{log.action_taken}</span>
        <span class="time">{log.timestamp_utc}</span>
        {#if log.action_taken === 'Queued'}
          <button class="retry-btn" onclick={() => retryContainment(log)} disabled={processingId === log.id}>
            {processingId === log.id ? 'Processing...' : 'Retry'}
          </button>
        {/if}
        <button class="summary-btn" onclick={() => openDefenseSummary(log)}>
          Defense Summary
        </button>
      </li>
    {/each}
    {#if logs.length === 0}
      <li class="feed-item">No active quarantines.</li>
    {/if}
  </ul>

  {#if showModal && modalLog}
    <div class="modal-overlay">
      <div class="modal-content">
        <button class="close-btn" onclick={closeModal} title="Close">×</button>
        <h2>Defense Summary</h2>
        <ol>
          <li><b>Detection:</b> {modalLog.timestamp_utc}</li>
          <li><b>Anomaly Score:</b> 4.5</li>
          <li><b>Containment Action:</b> K8s Label applied (status=quarantine)</li>
          <li><b>Final Status:</b> Success</li>
        </ol>
        <button class="download-btn" onclick={downloadIncidentReport}>
          Download Incident Report
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
.feed-container {
  padding: 0;
  box-shadow: 0 4px 16px rgba(255,0,0,0.25);
  color: #fff;
  min-width: 350px;
  border: 2px solid #ff1744;
}
.feed-header {
  background: #ff1744;
  color: #fff;
  font-size: 1.3rem;
  font-weight: bold;
  padding: 1rem 1.5rem;
  border-radius: 10px 10px 0 0;
  letter-spacing: 1px;
  box-shadow: 0 2px 8px rgba(255,23,68,0.15);
  margin-bottom: 0;
}
.feed-list {
  list-style: none;
  padding: 1rem 1.5rem 1.5rem 1.5rem;
  margin: 0;
}
.feed-item {
  padding: 1rem 0.5rem;
  border-bottom: 1px solid #ff5252;
  background: rgba(255,23,68,0.08);
  margin-bottom: 0.5rem;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  transition: background 0.2s;
}
.feed-item:last-child {
  border-bottom: none;
}
.blink {
  animation: blink 1s linear 3;
}
.action {
  color: #ffd54f;
  font-weight: 500;
  margin-top: 0.3em;
}
.time {
  font-size: 0.9em;
  color: #b0bec5;
  margin-top: 0.2em;
}
.notification {
  background: #ffd54f;
  color: #222;
  padding: 0.5em 1em;
  margin: 0.5em 1.5em 0.5em 1.5em;
  border-radius: 5px;
  font-weight: bold;
}
.retry-btn {
  margin-top: 0.5em;
  background: #ff1744;
  color: #fff;
  border: none;
  padding: 0.4em 1em;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}
.retry-btn[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
}
.summary-btn {
  margin-top: 0.5em;
  background: #ffd54f;
  color: #222;
  border: none;
  padding: 0.4em 1em;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.45);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-content {
  background: #181c24;
  padding: 2.5rem 2rem 2rem 2rem;
  border-radius: 12px;
  min-width: 340px;
  max-width: 95vw;
  box-shadow: 0 8px 32px #000b;
  position: relative;
  color: #fff;
}
.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  color: #fff;
  font-size: 1.5em;
  cursor: pointer;
}
.download-btn {
  margin-top: 1.5em;
  background: #ffd54f;
  color: #222;
  border: none;
  padding: 0.7em 1.5em;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
}
h2 {
  color: #ff1744;
  margin-bottom: 1.5rem;
}
ol {
  color: #fff;
  font-size: 1.1em;
  line-height: 1.7;
}
</style>
