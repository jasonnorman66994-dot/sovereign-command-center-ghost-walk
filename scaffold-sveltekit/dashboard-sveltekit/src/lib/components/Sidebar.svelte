<script lang="ts">
let { active = 'dashboard' } = $props();
</script>

<style>
.sidebar {
  background: #162032;
  color: #fff;
  width: 220px;
  min-height: 100vh;
  padding: 2rem 1rem;
  border-radius: 1rem 0 0 1rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
.nav-link {
  color: #7ecfff;
  text-decoration: none;
  font-weight: 600;
  margin-bottom: 1rem;
  transition: color 0.2s;
}
.nav-link.active {
  color: #fff;
  background: #1a2636;
  border-radius: 0.5rem;
  padding: 0.5rem 1rem;
}
</style>

<nav class="sidebar">
  <a class="nav-link {active === 'dashboard' ? 'active' : ''}" href="/">Dashboard</a>
  <a class="nav-link {active === 'alerts' ? 'active' : ''}" href="/alerts">Alerts</a>
  <a class="nav-link {active === 'settings' ? 'active' : ''}" href="/settings">Settings</a>
</nav>
