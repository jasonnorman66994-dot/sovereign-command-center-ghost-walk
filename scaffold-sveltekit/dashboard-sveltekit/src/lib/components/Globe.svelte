
<script lang="ts">


import { mysqlStatus } from './HealthPulse.svelte';
import { onMount } from 'svelte';
import * as THREE from 'three';
import { get } from 'svelte/store';
let { threatData = [], highlightAlert = null } = $props();
let container: HTMLDivElement;
let renderer: THREE.WebGLRenderer;
let scene: THREE.Scene;
let camera: THREE.PerspectiveCamera;
let globe: THREE.Mesh;

// Helper: check if any alert is Executed
function hasExecutedAlert() {
    return threatData.some(alert => alert.action_taken === 'Executed');
}

function randomLatLon() {
    // Generate a random lat/lon (not Los Angeles)
    let lat = Math.random() * 180 - 90;
    let lon = Math.random() * 360 - 180;
    // Avoid Los Angeles (lat 34.0522, lon -118.2437)
    if (Math.abs(lat - 34.0522) < 5 && Math.abs(lon + 118.2437) < 5) {
        lat += 10;
        lon += 10;
    }
    return { lat, lon };
}

onMount(() => {
    // Scene setup
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.z = 2.5;

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);

    // Globe
    const geometry = new THREE.SphereGeometry(1, 64, 64);
    let globeMaterial: THREE.Material;
    if (get(mysqlStatus) === 'CONNECTED') {
        globeMaterial = new THREE.MeshStandardMaterial({ color: 0x0077be, wireframe: true, opacity: 0.5, transparent: true });
    } else {
        globeMaterial = new THREE.MeshStandardMaterial({ color: 0x222a3a, wireframe: false });
    }
    globe = new THREE.Mesh(geometry, globeMaterial);
    scene.add(globe);

    // If any Executed alert, pulse red at LA
    if (hasExecutedAlert()) {
        const laLat = 34.0522;
        const laLon = -118.2437;
        const phi = (90 - laLat) * (Math.PI / 180);
        const theta = (laLon + 180) * (Math.PI / 180);
        const r = 1.01;
        const x = r * Math.sin(phi) * Math.cos(theta);
        const y = r * Math.cos(phi);
        const z = r * Math.sin(phi) * Math.sin(theta);
        const pulseGeometry = new THREE.SphereGeometry(0.07, 24, 24);
        const pulseMaterial = new THREE.MeshBasicMaterial({ color: 0xff1744 });
        const pulse = new THREE.Mesh(pulseGeometry, pulseMaterial);
        pulse.position.set(x, y, z);
        scene.add(pulse);
        // Animate pulse (grow/shrink)
        let scale = 1;
        let growing = true;
        function pulseAnim() {
            if (growing) {
                scale += 0.02;
                if (scale > 1.4) growing = false;
            } else {
                scale -= 0.02;
                if (scale < 1) growing = true;
            }
            pulse.scale.set(scale, scale, scale);
            requestAnimationFrame(pulseAnim);
        }
        pulseAnim();
    }

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight.position.set(5, 3, 5);
    scene.add(directionalLight);

    // Plot threatData as dots: pulse yellow if deviation_score > 2.0, else red
    threatData.forEach(alert => {
        if (!alert.geo_location) return;
        const { lat, lon } = alert.geo_location;
        const phi = (90 - lat) * (Math.PI / 180);
        const theta = (lon + 180) * (Math.PI / 180);
        const r = 1.01;
        const x = r * Math.sin(phi) * Math.cos(theta);
        const y = r * Math.cos(phi);
        const z = r * Math.sin(phi) * Math.sin(theta);
        const dotGeometry = new THREE.SphereGeometry(0.025, 16, 16);
        let color = 0xff0000; // default: red for critical
        if (alert.deviation_score && alert.deviation_score > 2.0) {
            color = 0xffff00; // yellow for anomaly
        }
        const dotMaterial = new THREE.MeshStandardMaterial({ color });
        const dot = new THREE.Mesh(dotGeometry, dotMaterial);
        dot.position.set(x, y, z);
        scene.add(dot);

        // Draw red arc for Executed containment
        if (alert.action_taken === 'Executed') {
            // Los Angeles coordinates
            const laLat = 34.0522;
            const laLon = -118.2437;
            const laPhi = (90 - laLat) * (Math.PI / 180);
            const laTheta = (laLon + 180) * (Math.PI / 180);
            const laR = 1.01;
            const laX = laR * Math.sin(laPhi) * Math.cos(laTheta);
            const laY = laR * Math.cos(laPhi);
            const laZ = laR * Math.sin(laPhi) * Math.sin(laTheta);

            // Random exfil endpoint
            let exfil = alert.exfil_location || randomLatLon();
            // Save for future renders
            alert.exfil_location = exfil;
            const exPhi = (90 - exfil.lat) * (Math.PI / 180);
            const exTheta = (exfil.lon + 180) * (Math.PI / 180);
            const exR = 1.01;
            const exX = exR * Math.sin(exPhi) * Math.cos(exTheta);
            const exY = exR * Math.cos(exPhi);
            const exZ = exR * Math.sin(exPhi) * Math.sin(exTheta);

            // Arc points
            const arcCurve = new THREE.QuadraticBezierCurve3(
                new THREE.Vector3(laX, laY, laZ),
                new THREE.Vector3((laX + exX) / 2, (laY + exY) / 2 + 0.5, (laZ + exZ) / 2),
                new THREE.Vector3(exX, exY, exZ)
            );
            const arcPoints = arcCurve.getPoints(50);
            const arcGeometry = new THREE.BufferGeometry().setFromPoints(arcPoints);
            const arcMaterial = new THREE.LineBasicMaterial({ color: 0xff1744, linewidth: 3 });
            const arc = new THREE.Line(arcGeometry, arcMaterial);
            scene.add(arc);
        }
    });

    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        globe.rotation.y += 0.002;
        renderer.render(scene, camera);
    }
    animate();

    return () => {
        renderer.dispose();
    };
});
</script>

<style>
:global(.globe-container) {
  width: 100%;
  height: 100%;
  min-height: 400px;
  background: #101c2c;
  border-radius: 1rem;
  overflow: hidden;
}
</style>

<div bind:this={container} class="globe-container"></div>
<div style="position:absolute;left:1.5rem;bottom:1.5rem;z-index:10;background:#181c24cc;padding:0.7em 1.2em;border-radius:0.7em;font-size:1em;color:#fff;box-shadow:0 2px 8px #0007;min-width:220px;">
    <b>Legend:</b><br>
    <span style="color:#ffd600;">●</span> Yellow = Anomaly Detected<br>
    <span style="color:#ff1744;">━</span> Red Arc = Blocked Exfiltration
</div>
