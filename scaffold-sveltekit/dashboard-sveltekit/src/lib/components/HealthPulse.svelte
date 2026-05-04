<script lang="ts">
import { onMount } from 'svelte';
import { writable } from 'svelte/store';

export const k8sStatus = writable<'healthy' | 'unhealthy' | 'unknown'>('unknown');
export const mysqlStatus = writable<'healthy' | 'unhealthy' | 'unknown'>('unknown');
export const k8sError = writable<string | null>(null);
export const mysqlError = writable<string | null>(null);

function manualReconnect(service: 'k8s' | 'mysql') {
	if (service === 'k8s') {
		k8sError.set(null);
		fetchK8sStatus();
	}
	if (service === 'mysql') {
		mysqlError.set(null);
		fetchMySQLStatus();
	}
}

async function fetchK8sStatus() {
	try {
		const res = await fetch('/api/health/k8s');
		const data = await res.json();
		if (data.status === 'healthy') {
			k8sStatus.set('healthy');
			k8sError.set(null);
		} else {
			k8sStatus.set('unhealthy');
			k8sError.set(data.error || 'K8s offline');
		}
	} catch {
		k8sStatus.set('unhealthy');
		k8sError.set('K8s unreachable');
	}
}

async function fetchMySQLStatus() {
	try {
		const res = await fetch('/api/health/mysql');
		const data = await res.json();
		if (data.status === 'healthy') {
			mysqlStatus.set('healthy');
			mysqlError.set(null);
		} else {
			mysqlStatus.set('unhealthy');
			mysqlError.set(data.error || 'MySQL disconnected');
		}
	} catch {
		mysqlStatus.set('unhealthy');
		mysqlError.set('MySQL unreachable');
	}
}

onMount(() => {
	fetchK8sStatus();
	fetchMySQLStatus();
	const interval = setInterval(() => {
		fetchK8sStatus();
		fetchMySQLStatus();
	}, 5000);
	return () => clearInterval(interval);
});
</script>

<div class="health-pulse">
	<div class="pulse-group">
		<div class="pulse-label">Kubernetes</div>
		{#if $k8sStatus === 'healthy'}
			<div class="pulse k8s healthy"></div>
		{:else if $k8sStatus === 'unhealthy'}
			<div class="pulse k8s unhealthy"></div>
		{:else}
			<div class="pulse k8s unknown"></div>
		{/if}
		<div class="status-label">Status: {$k8sStatus}</div>
		{#if $k8sError}
			<div class="error">{$k8sError} <button onclick={() => manualReconnect('k8s')}>Reconnect</button></div>
		{/if}
	</div>
	<div class="pulse-group">
		<div class="pulse-label">MySQL</div>
		{#if $mysqlStatus === 'healthy'}
			<div class="pulse mysql healthy"></div>
		{:else if $mysqlStatus === 'unhealthy'}
			<div class="pulse mysql unhealthy"></div>
		{:else}
			<div class="pulse mysql unknown"></div>
		{/if}
		<div class="status-label">Status: {$mysqlStatus}</div>
		{#if $mysqlError}
			<div class="error">{$mysqlError} <button onclick={() => manualReconnect('mysql')}>Reconnect</button></div>
		{/if}
	</div>
</div>

<style>
.health-pulse {
	display: flex;
	gap: 2rem;
	justify-content: center;
	align-items: center;
	margin: 2rem 0;
}
.pulse-group {
	display: flex;
	flex-direction: column;
	align-items: center;
	min-width: 120px;
}
.pulse-label {
	font-size: 1.1rem;
	margin-bottom: 0.5rem;
	font-weight: 600;
}
.status-label {
	font-size: 0.95rem;
	margin-bottom: 0.25rem;
	color: #666;
}
.pulse {
	width: 32px;
	height: 32px;
	border-radius: 50%;
	margin-bottom: 0.5rem;
	box-shadow: 0 0 0 0 rgba(0,0,0,0.2);
	animation: pulse 2s infinite;
}
.pulse.k8s.healthy {
	background: #4caf50;
	box-shadow: 0 0 8px 2px #4caf50;
}
.pulse.k8s.unhealthy {
	background: #f44336;
	box-shadow: 0 0 8px 2px #f44336;
}
.pulse.k8s.unknown {
	background: #bdbdbd;
	box-shadow: 0 0 8px 2px #bdbdbd;
}
.pulse.mysql.healthy {
	background: #2196f3;
	box-shadow: 0 0 8px 2px #2196f3;
}
.pulse.mysql.unhealthy {
	background: #ff9800;
	box-shadow: 0 0 8px 2px #ff9800;
}
.pulse.mysql.unknown {
	background: #bdbdbd;
	box-shadow: 0 0 8px 2px #bdbdbd;
}
@keyframes pulse {
	0% {
		transform: scale(1);
		box-shadow: 0 0 0 0 rgba(0,0,0,0.2);
	}
	70% {
		transform: scale(1.15);
		box-shadow: 0 0 16px 8px rgba(0,0,0,0.08);
	}
	100% {
		transform: scale(1);
		box-shadow: 0 0 0 0 rgba(0,0,0,0.2);
	}
}
.error {
	color: #f44336;
	font-size: 0.95rem;
	margin-top: 0.25rem;
	text-align: center;
}
button {
	margin-left: 0.5rem;
	padding: 0.2rem 0.7rem;
	font-size: 0.95rem;
	border: none;
	border-radius: 4px;
	background: #eee;
	cursor: pointer;
	transition: background 0.2s;
}
button:hover {
	background: #e0e0e0;
}
</style>

