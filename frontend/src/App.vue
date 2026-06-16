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
body { margin: 0; background: #fdfcfc; color: #201d1d; font-family: 'Berkeley Mono', monospace; }
.app-layout { display: flex; height: 100vh; overflow: hidden; }
.main-content { flex: 1; overflow-y: auto; position: relative; }
</style>
