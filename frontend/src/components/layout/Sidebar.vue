<!-- frontend/src/components/layout/Sidebar.vue -->
<template>
  <aside class="sidebar">
    <div class="logo">[Glabel]</div>
    <nav class="nav-links">
      <router-link to="/" class="nav-item">Open Vision</router-link>
      <router-link to="/playgrounds" class="nav-item">Playgrounds</router-link>
      <router-link to="/models" class="nav-item">Models</router-link>
      <router-link to="/settings" class="nav-item">Settings</router-link>
    </nav>
  </aside>
</template>
<style scoped>
.sidebar { width: 250px; border-right: 1px solid #646262; display: flex; flex-direction: column; background: #fdfcfc; font-family: 'Berkeley Mono', monospace; height: 100vh; }
.logo { padding: 1rem; font-weight: bold; border-bottom: 1px solid #646262; }
.nav-links { display: flex; flex-direction: column; padding: 1rem 0; }
.nav-item { padding: 0.5rem 1rem; color: #201d1d; text-decoration: none; display: block; }
.nav-item:hover, .router-link-active { background: rgba(15,0,0,0.05); }
</style>
