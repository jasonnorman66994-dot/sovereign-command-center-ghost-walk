<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import ActiveContainmentFeed from '$lib/components/ActiveContainmentFeed.svelte';
	import HealthPulse from '$lib/components/HealthPulse.svelte';
	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<HealthPulse />
<div style="display: flex; flex-direction: column; gap: 2rem;">
	{#if children}
		{@render children()}
	{/if}
</div>
