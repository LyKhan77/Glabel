<!-- frontend/src/components/layout/Sidebar.vue -->
<template>
  <aside :class="['sidebar', { collapsed: isCollapsed }]">
    <div class="logo">
      <button class="menu-btn" @click="toggleSidebar">
        <svg viewBox="0 0 24 24" width="24" height="24" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
      </button>
      <div class="logo-brand" v-show="!isCollapsed">
        <img src="/platypus-glabel.png" alt="Glabel" class="logo-img" />
        <span class="logo-text">Glabel</span>
      </div>
    </div>
    <nav class="nav-links">
      <router-link to="/" class="nav-item" title="Open Vision">
        <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"></path><circle cx="12" cy="12" r="3"></circle></svg>
        <span class="nav-text" v-show="!isCollapsed">Open Vision</span>
      </router-link>
      <router-link to="/playgrounds" class="nav-item" title="Playgrounds">
        <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
        <span class="nav-text" v-show="!isCollapsed">Playgrounds</span>
      </router-link>
      <router-link to="/models" class="nav-item" title="Models">
        <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
        <span class="nav-text" v-show="!isCollapsed">Models</span>
      </router-link>
      <router-link to="/settings" class="nav-item" title="Settings">
        <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
        <span class="nav-text" v-show="!isCollapsed">Settings</span>
      </router-link>
      <button @click="toggleTheme" class="nav-item theme-btn" :title="isDark ? 'Light Mode' : 'Dark Mode'">
        <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" v-if="!isDark"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
        <svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none" v-else><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
        <span class="nav-text" v-show="!isCollapsed">{{ isDark ? 'Light Mode' : 'Dark Mode' }}</span>
      </button>
    </nav>
  </aside>
</template>
<script setup>
import { ref } from 'vue'

const isCollapsed = ref(false)
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const isDark = ref(false)
const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
}
</script>
<style scoped>
.sidebar { width: 250px; border-right: 1px solid var(--border-color); display: flex; flex-direction: column; background: var(--bg-color); font-family: 'Berkeley Mono', monospace; height: 100vh; transition: width 0.3s ease; }
.sidebar.collapsed { width: 72px; }
.logo { padding: 1rem 1.5rem; font-weight: bold; border-bottom: 1px solid var(--border-color); display: flex; align-items: center; gap: 1rem; overflow: hidden; white-space: nowrap; height: 73px; box-sizing: border-box; }
.menu-btn { background: transparent; border: none; cursor: pointer; color: var(--text-color); padding: 0; display: flex; align-items: center; justify-content: center; }
.logo-brand { display: flex; align-items: center; gap: 0.75rem; }
.logo-img { height: 32px; filter: grayscale(100%) invert(var(--img-invert, 0)); }
.logo-text { font-size: 1.25rem; letter-spacing: 0.05em; }
.nav-links { display: flex; flex-direction: column; padding: 1rem 0; flex: 1; overflow-x: hidden; }
.nav-item { padding: 0.75rem 1.5rem; color: var(--text-color); text-decoration: none; display: flex; align-items: center; gap: 1rem; border-left: 3px solid transparent; white-space: nowrap; }
.nav-item:hover { background: var(--hover-bg, rgba(15,0,0,0.05)); }
.router-link-active { background: var(--hover-bg, rgba(15,0,0,0.05)); border-left: 3px solid var(--text-color); font-weight: bold; }
.theme-btn { background: transparent; border: none; cursor: pointer; text-align: left; font-family: inherit; font-size: inherit; margin-top: auto; border-left: none; width: 100%; display: flex; align-items: center; gap: 1rem; }
</style>
