// Sovereign Dead Man's Switch UI component (React example)
// Place this in your Globe/HUD React component file
import React, { useState } from 'react';
import io from 'socket.io-client';

const socket = io('http://localhost:3000');

export default function DeadMansSwitch() {
  const [armed, setArmed] = useState(true);
  const [activated, setActivated] = useState(false);

  const handleDMS = () => {
    if (armed && !activated) {
      socket.emit('GLOBAL_PURGE');
      setActivated(true);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      bottom: 32,
      right: 32,
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
    }}>
      <button
        onClick={handleDMS}
        style={{
          background: armed ? (activated ? '#b71c1c' : '#ffeb3b') : '#ccc',
          color: '#222',
          border: '2px solid #222',
          borderRadius: '50%',
          width: 72,
          height: 72,
          fontSize: 32,
          boxShadow: '0 0 16px #b71c1c',
          cursor: armed && !activated ? 'pointer' : 'not-allowed',
          transition: 'background 0.2s',
        }}
        title={activated ? 'DMS Activated' : 'Dead Man\'s Switch (Armed)'}
        disabled={!armed || activated}
      >
        <span role="img" aria-label="fingerprint">🔒</span>
      </button>
      <div style={{marginTop: 8, fontWeight: 'bold', color: activated ? '#b71c1c' : '#222'}}>
        {activated ? 'System Isolated' : 'DMS Armed'}
      </div>
    </div>
  );
}
