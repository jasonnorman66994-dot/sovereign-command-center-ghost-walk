// DetectionLineageLegend.js
import React from 'react';

const lineageData = [
  { event: 'Red Arc (Phish)', rule: 'NY-T1566-FakeUpdate-01', attack: 'T1566.002 (Phishing)', source: 'Gmail/SMTP', owner: 'SOC Analyst' },
  { event: 'Pulsing Node (Stealer)', rule: 'NY-T1114-Browser-06', attack: 'T1114 (Collection)', source: 'Sysmon (Windows)', owner: 'Detection Engineer' },
  { event: 'Yellow Arc (Anomaly)', rule: 'NY-T1550-TokenReuse-08', attack: 'T1550.004 (Identity)', source: 'Auth Logs / Node.js', owner: 'SOC Lead' },
  { event: 'Outbound Pulse (C2)', rule: 'NY-T1071-Telegram-11', attack: 'T1071.001 (Telegram)', source: 'Firewall / Proxy', owner: 'Threat Intel Lead' },
  { event: 'Red Pulse (Impact)', rule: 'NY-T1486-Ransom-12', attack: 'T1486 (Ransomware)', source: 'Endpoint FS Events', owner: 'Incident Response' },
];

export default function DetectionLineageLegend() {
  return (
    <div style={{
      position: 'absolute',
      top: 20,
      right: 20,
      background: 'rgba(30,30,30,0.95)',
      color: '#fff',
      padding: '16px',
      borderRadius: '8px',
      fontSize: '12px',
      zIndex: 1000,
      minWidth: 340,
      boxShadow: '0 2px 12px #0008'
    }}>
      <b>Detection Lineage Map</b>
      <table style={{ width: '100%', marginTop: 8, borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid #555' }}>
            <th align="left">Visual</th>
            <th align="left">Rule ID</th>
            <th align="left">ATT&CK</th>
            <th align="left">Source</th>
            <th align="left">Owner</th>
          </tr>
        </thead>
        <tbody>
          {lineageData.map((row, i) => (
            <tr key={i} style={{ borderBottom: '1px solid #333' }}>
              <td>{row.event}</td>
              <td>{row.rule}</td>
              <td>{row.attack}</td>
              <td>{row.source}</td>
              <td>{row.owner}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
