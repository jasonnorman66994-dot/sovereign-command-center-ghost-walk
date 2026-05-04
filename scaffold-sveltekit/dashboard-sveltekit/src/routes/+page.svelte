
<script lang="ts">
import ActiveContainmentFeed from '$lib/components/ActiveContainmentFeed.svelte';
</script>

<style>
.dashboard-layout {
	display: flex;
	min-height: 100vh;
	background: #0d1524;
}
.sidebar-area {
	flex: 0 0 220px;
}
.main-area {
	flex: 1;
	padding: 2rem;
	display: flex;
	flex-direction: column;
	gap: 2rem;
}
</style>


<main style="padding: 2rem; background: #0d1524; min-height: 100vh;">
	<ActiveContainmentFeed />
</main>
