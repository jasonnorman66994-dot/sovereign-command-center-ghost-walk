/**
 * Calculates a dynamic mid-point height for the Bezier curve.
 * Ensures long-range hits have higher arcs.
 */
const calculateArcHeight = (startVec, endVec, minHeight = 1.5, maxHeight = 4.5) => {
  // Calculate the straight-line distance between the two 3D vectors
  const distance = startVec.distanceTo(endVec);
  // Scale height based on distance (assuming globe radius of 5)
  // Long-distance hits (e.g., London to LA) get the maxHeight.
  // Local hits (e.g., SF to LA) get the minHeight.
  const scaledHeight = minHeight + (distance / 10) * (maxHeight - minHeight);
  return scaledHeight;
};
import * as THREE from 'three';

// 1. Define the Refined Target Constant
const LA_COORDS = { lat: 34.0522, lon: -118.2437 };
const GLOBE_RADIUS = 5; // Ensure this matches your globe's radius

// 2. Optimized Vector Conversion
const getLAVector = (radius) => {
  const phi = (90 - LA_COORDS.lat) * (Math.PI / 180);
  const theta = (LA_COORDS.lon + 180) * (Math.PI / 180);
  return new THREE.Vector3(
    -(radius * Math.sin(phi) * Math.cos(theta)),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta)
  );
};
const laTarget = getLAVector(GLOBE_RADIUS);

/**
 * PATCH: handleIncomingTelemetry
 * Intercepts events to override destination for harvests
 */
export const patchTelemetryHandler = (event) => {
  // Check if event is a successful harvest
  if (event.type === 'Credential_Harvest' || event.pulseColor === 'red' || event.event_type === 'Credential_Harvest') {
    console.log(`[HUD] Precision Snap: Routing hit from ${event.geo} to LA.`);
    /**
     * REFINEMENT PATCH v2: Precision LA Targeting + Dynamic Arc Height
     * Applied to playbackController.js
     */

    import * as THREE from 'three';

    // --- CONFIGURATION ---
    const LA_COORDS = { lat: 34.0522, lon: -118.2437 };
    const GLOBE_RADIUS = 5; 

    // --- DYNAMIC HEIGHT LOGIC ---
    const getLAVector = (radius) => {
        const phi = (90 - LA_COORDS.lat) * (Math.PI / 180);
        const theta = (LA_COORDS.lon + 180) * (Math.PI / 180);
        return new THREE.Vector3(
            -(radius * Math.sin(phi) * Math.cos(theta)),
            radius * Math.cos(phi),
            radius * Math.sin(phi) * Math.sin(theta)
        );
    };

    const laTarget = getLAVector(GLOBE_RADIUS);

    /**
     * Calculates mid-point with altitude compensation
     */
    const getDynamicMidPoint = (startVec, endVec) => {
        const distance = startVec.distanceTo(endVec);
    
        // Scale height: Min 1.5 (local) to Max 5.0 (global)
        const altitude = 1.5 + (distance / 10) * 3.5;
    
        const midPoint = new THREE.Vector3()
            .addVectors(startVec, endVec)
            .multiplyScalar(0.5);
    
        // Push the midpoint away from the center of the globe
        return midPoint.normalize().multiplyScalar(GLOBE_RADIUS + altitude);
    };

    // --- PATCHED TELEMETRY HANDLER ---
    export const patchTelemetryHandler = (event) => {
        if (event.type === 'Credential_Harvest' || event.pulseColor === 'red') {
            const startVector = event.sourceVector; // Existing source logic
        
            return {
                ...event,
                destinationVector: laTarget,
                midPoint: getDynamicMidPoint(startVector, laTarget),
                forceSnap: true,
                bezierCurve: true
            };
        }
        return event;
    };
    return {
      ...event,
      destinationVector: laTarget,
      forceSnap: true
    };
  }
  return event;
};
// --- PRECISE LOS ANGELES COORDINATES ---
const LA_LAT = 34.0522;
const LA_LON = -118.2437;

/**
 * Converts Latitude and Longitude to a 3D Vector3 point.
 * @param {number} lat - Latitude in degrees
 * @param {number} lon - Longitude in degrees
 * @param {number} radius - Radius of your globe (defaulting to 5)
 */
const getVector3FromLatLon = (lat, lon, radius = 5) => {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);

  const x = -(radius * Math.sin(phi) * Math.cos(theta));
  const z = radius * Math.sin(phi) * Math.sin(theta);
  const y = radius * Math.cos(phi);

  return new THREE.Vector3(x, y, z);
};

// This is your fixed destination for all harvest arcs
const laTargetVector = getVector3FromLatLon(LA_LAT, LA_LON);
// playbackController.js (Three.js HUD logic)
// Assumes you have a Three.js globe, arc/pulse functions, and a HUD with a Play/Pause button

let playbackActive = false;
let playbackTimeout;
let playbackIndex = 0;
let playbackData = [];
let playbackStartTime = null;
let playbackSpeed = 24 * 60 * 60 * 1000 / 60000; // 24h in 60s (ms per real ms)

async function fetchHistory() {
  const res = await fetch('/api/v1/history');
  const data = await res.json();
  return data.events;
}

function playTimeLapse() {
  if (!playbackData.length) return;
  playbackActive = true;
  playbackIndex = 0;
  clearLivePulses();
  playbackStartTime = new Date(playbackData[0].timestamp).getTime();
  nextPulse();
}

function pauseTimeLapse() {
  playbackActive = false;
  clearTimeout(playbackTimeout);
}

function nextPulse() {
  if (!playbackActive || playbackIndex >= playbackData.length) return;
  let event = playbackData[playbackIndex];
  // PATCH: Wrap event with precision LA targeting
  event = patchTelemetryHandler(event);
  const now = new Date(event.timestamp).getTime();
  // --- Arc Snap for Credential Harvests ---
  if (event.event_type === 'Credential_Harvest') {
    const startVec = getVector3FromLatLon(event.targetLat, event.targetLon);
    const endVec = laTargetVector;
    // Calculate dynamic arc height
    const arcHeight = calculateArcHeight(startVec, endVec);
    // Compute the Bezier control point (midpoint, raised by arcHeight)
    const midPoint = new THREE.Vector3().addVectors(startVec, endVec).multiplyScalar(0.5);
    midPoint.normalize().multiplyScalar(GLOBE_RADIUS + arcHeight);
    event.arc = {
      start: startVec,
      end: endVec,
      control: midPoint,
      color: '#ff0000', // Red for harvests
      duration: 2000
    };
  }
  if (playbackIndex > 0) {
    const prev = new Date(playbackData[playbackIndex - 1].timestamp).getTime();
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

// HUD Play/Pause toggle
function togglePlayback() {
  if (playbackActive) {
    pauseTimeLapse();
  } else {
    playTimeLapse();
  }
}

// Usage: (async () => { playbackData = await fetchHistory(); playTimeLapse(); })();
// Attach togglePlayback to your HUD button.
