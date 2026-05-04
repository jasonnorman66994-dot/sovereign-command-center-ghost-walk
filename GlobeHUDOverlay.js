// GlobeHUDOverlay.js
import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';

const socket = io('http://localhost:3000');

export default function GlobeHUDOverlay({ setGlobeColor }) {
  const [lockdown, setLockdown] = useState(false);
  const [counter, setCounter] = useState({ captured: 0, total: 50 });
  const [flash, setFlash] = useState(false);

  useEffect(() => {
    socket.on('SYSTEM_LOCKDOWN', () => {
      setLockdown(true);
      setFlash(true);
      if (setGlobeColor) setGlobeColor('#b71c1c');
    });
    socket.on('harvest-counter', ({ captured, total }) => {
      setCounter({ captured, total });
    });
    return () => {
      socket.off('SYSTEM_LOCKDOWN');
      socket.off('harvest-counter');
    };
  }, [setGlobeColor]);

  // Counter style
  const counterStyle = {
    position: 'fixed',
    top: 24,
    left: '50%',
    transform: 'translateX(-50%)',
    zIndex: 10001,
    background: lockdown ? '#b71c1c' : 'rgba(0,0,0,0.85)',
    color: lockdown ? '#fff' : '#ffeb3b',
    border: lockdown ? '4px solid #fff' : '2px solid #ffeb3b',
    borderRadius: 12,
    padding: '12px 32px',
    fontSize: 32,
    fontWeight: 'bold',
    letterSpacing: 2,
    boxShadow: '0 0 24px #b71c1c',
    textAlign: 'center',
    transition: 'all 0.4s',
    animation: flash ? 'flashRed 1s steps(2, start) infinite' : 'none',
  };

  // Keyframes for flashing effect
  const styleSheet = document.styleSheets[0];
  if (styleSheet && !styleSheet.rules.namedItem('flashRed')) {
    try {
      styleSheet.insertRule(`@keyframes flashRed { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }`, styleSheet.cssRules.length);
    } catch {}
  }

  return (
    <>
      <div style={counterStyle}>
        {lockdown ? (
          <span style={{ color: '#fff', fontWeight: 'bold', letterSpacing: 2 }}>NEUTRALIZED</span>
        ) : (
          <span>LIVE IDENTITY HARVEST: {counter.captured} / {counter.total}</span>
        )}
      </div>
      {lockdown && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100vw',
          height: '100vh',
          background: 'rgba(60,0,0,0.92)',
          color: '#fff',
          zIndex: 10000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 36,
          fontWeight: 'bold',
          letterSpacing: 2,
          textShadow: '0 0 24px #b71c1c',
          transition: 'background 0.5s'
        }}>
          INFRASTRUCTURE ISOLATED - ZERO TRUST PURGE COMPLETE.
        </div>
      )}
    </>
  );
}
