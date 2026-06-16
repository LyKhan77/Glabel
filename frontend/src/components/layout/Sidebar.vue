<!-- frontend/src/components/layout/Sidebar.vue -->
<template>
  <aside class="sidebar">
    <div class="logo">
      <img src="/platypus-glabel.png" alt="Glabel" style="height: 40px; filter: grayscale(100%) invert(var(--img-invert, 0));" />
    </div>
    <nav class="nav-links">
      <router-link to="/" class="nav-item">Open Vision</router-link>
      <router-link to="/playgrounds" class="nav-item">Playgrounds</router-link>
      <router-link to="/models" class="nav-item">Models</router-link>
      <router-link to="/settings" class="nav-item">Settings</router-link>
      <button @click="toggleTheme" class="nav-item theme-btn">
        {{ isDark ? '[☼] Light Mode' : '[☾] Dark Mode' }}
      </button>
    </nav>
  </aside>
</template>
<script setup>
import { ref } from 'vue'

const isDark = ref(false)
const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
}
</script>
<style scoped>
.sidebar { width: 250px; border-right: 1px solid var(--border-color); display: flex; flex-direction: column; background: var(--bg-color); font-family: 'Berkeley Mono', monospace; height: 100vh; }
.logo { padding: 1rem; font-weight: bold; border-bottom: 1px solid var(--border-color); }
.nav-links { display: flex; flex-direction: column; padding: 1rem 0; flex: 1; }
.nav-item { padding: 0.5rem 1rem; color: var(--text-color); text-decoration: none; display: block; }
.nav-item:hover, .router-link-active { background: rgba(15,0,0,0.05); }
.theme-btn { background: transparent; border: none; cursor: pointer; text-align: left; font-family: inherit; font-size: inherit; margin-top: auto; }
</style>
