<template>
  <div class="app-layout">
    <Sidebar />
    <main class="main-content">
      <router-view></router-view>
    </main>
  </div>
</template>
<script setup>
import Sidebar from './components/layout/Sidebar.vue'
</script>
<style>
:root {
  --bg-color: #fdfcfc;
  --surface-soft: #f8f7f7;
  --text-color: #201d1d;
  --body: #424245;
  --mute: #6e6e73;
  --border-color: #646262;
  --hairline: rgba(15, 0, 0, 0.12);
  --hover-bg: rgba(15, 0, 0, 0.05);
  --accent: #007aff;
  --danger: #ff3b30;
  --success: #30d158;
  --warning: #ff9f0a;
  --focus-ring: #007aff;
  --z-dropdown: 100;
  --z-sticky: 200;
  --z-backdrop: 900;
  --z-modal: 1000;
  --z-toast: 1100;
}
[data-theme='dark'] {
  --bg-color: #1a1a1a;
  --surface-soft: #232323;
  --text-color: #e0e0e0;
  --body: #c9c9c9;
  --mute: #9a9a9a;
  --border-color: #4a4a4a;
  --hairline: rgba(255, 255, 255, 0.12);
  --hover-bg: rgba(255, 255, 255, 0.06);
  --img-invert: 1;
}
body { margin: 0; background-color: var(--bg-color); color: var(--text-color); font-family: 'Berkeley Mono', 'JetBrains Mono', 'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, monospace; transition: background-color 0.3s ease, color 0.3s ease; }
:focus-visible { outline: 2px solid var(--focus-ring); outline-offset: 2px; }
.app-layout { display: flex; height: 100vh; overflow: hidden; }
.main-content { flex: 1; overflow-y: auto; position: relative; }
</style>
