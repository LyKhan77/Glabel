<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  project: {
    type: Object,
    required: true
  },
  assets: {
    type: Array,
    required: true
  },
  apiBaseUrl: {
    type: String,
    required: false,
    default: ''
  }
})

const emit = defineEmits(['close'])

const activeTab = ref('unannotated')

const unannotatedAssets = computed(() => props.assets.filter(a => a.status === 'unannotated'))
const annotatedAssets = computed(() => props.assets.filter(a => a.status === 'annotated'))

const currentList = computed(() => activeTab.value === 'unannotated' ? unannotatedAssets.value : annotatedAssets.value)
</script>

<template>
  <div class="workspace-layout">
    <div class="sidebar">
      <div class="sidebar-header">
        <button class="nav-btn" @click="$emit('close')">[&lt;] Back</button>
        <h3>Workspace</h3>
      </div>
      <div class="tabs">
        <button 
          :class="['tab-btn', { active: activeTab === 'unannotated' }]"
          @click="activeTab = 'unannotated'"
        >Unannotated</button>
        <button 
          :class="['tab-btn', { active: activeTab === 'annotated' }]"
          @click="activeTab = 'annotated'"
        >Annotated</button>
      </div>
      <div class="image-list">
        <div v-for="img in currentList" :key="img.id" class="image-item">
          {{ img.filename }}
        </div>
        <div v-if="currentList.length === 0" class="empty-state">
          No images here.
        </div>
      </div>
    </div>
    <div class="canvas-area">
      <!-- Placeholder for Image Canvas (to be implemented in Task 6) -->
      <p>Select an image from the sidebar to start annotating.</p>
    </div>
  </div>
</template>

<style scoped>
.workspace-layout { 
  display: flex; 
  flex-grow: 1;
  min-height: 500px;
  border: 1px solid var(--border-color, #646262);
}

.sidebar {
  width: 250px;
  border-right: 1px solid var(--border-color, #646262);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px dashed var(--border-color, #646262);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.sidebar-header h3 {
  margin: 0;
  font-weight: normal;
}

.tabs {
  display: flex;
  border-bottom: 1px dashed var(--border-color, #646262);
}

.tab-btn {
  flex: 1;
  padding: 0.5rem;
  background: transparent;
  border: none;
  border-right: 1px dashed var(--border-color, #646262);
  cursor: pointer;
  font-family: inherit;
  font-size: inherit;
  color: inherit;
}

.tab-btn:last-child {
  border-right: none;
}

.tab-btn.active {
  background: var(--text-color, #201d1d);
  color: var(--bg-color, #fdfcfc);
}

.tab-btn:not(.active):hover {
  text-decoration: underline;
}

.image-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.image-item {
  padding: 0.5rem;
  border: 1px solid var(--border-color, #646262);
  cursor: pointer;
  font-size: 0.8rem;
  word-break: break-all;
}

.image-item:hover {
  background: rgba(0,0,0,0.05);
}

.canvas-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--border-color, #646262);
  font-style: italic;
}

.nav-btn {
  background: transparent;
  border: none;
  font-family: inherit;
  font-size: inherit;
  color: inherit;
  cursor: pointer;
  padding: 0;
}

.nav-btn:hover {
  text-decoration: underline;
}

.empty-state {
  color: #646262;
  font-style: italic;
  padding: 1rem;
  text-align: center;
}
</style>
