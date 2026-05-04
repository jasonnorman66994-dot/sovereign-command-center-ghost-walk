<script lang="ts">
let { threatData = [] } = $props();
</script>

<style>
.panel {
  background: #1a2636;
  color: #fff;
  border-radius: 1rem;
  padding: 1rem;
  margin-bottom: 1rem;
  min-height: 200px;
}
.table {
  width: 100%;
  border-collapse: collapse;
}
.table th, .table td {
  padding: 0.5rem;
  border-bottom: 1px solid #2a3a4d;
}
.table th {
  text-align: left;
  color: #7ecfff;
}
</style>

<div class="panel">
  <h2>Critical Identity Threats</h2>
  {#if threatData.length === 0}
    <p>No critical alerts found.</p>
  {:else}
    <table class="table">
      <thead>
        <tr>
          <th>Time (UTC)</th>
          <th>User</th>
          <th>Type</th>
          <th>Location</th>
        </tr>
      </thead>
      <tbody>
        {#each threatData as alert}
          <tr>
            <td>{alert.timestamp_utc}</td>
            <td>{alert.user_email}</td>
            <td>{alert.alert_type}</td>
            <td>{alert.geo_location ? `${alert.geo_location.lat}, ${alert.geo_location.lon}` : 'N/A'}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>
