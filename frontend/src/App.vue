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
  --text-color: #201d1d;
  --border-color: #646262;
}
[data-theme='dark'] {
  --bg-color: #1a1a1a;
  --text-color: #e0e0e0;
  --border-color: #4a4a4a;
  --img-invert: 1;
}
body { margin: 0; background-color: var(--bg-color); color: var(--text-color); font-family: 'Berkeley Mono', monospace; transition: background-color 0.3s ease, color 0.3s ease; }
.app-layout { display: flex; height: 100vh; overflow: hidden; }
.main-content { flex: 1; overflow-y: auto; position: relative; }
</style>
