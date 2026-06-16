<template>
  <div class="workspace-layout">
    <header class="toolbar">
      <button class="btn" @click="goHome">
        <span class="icon">[<]</span> Back to Home
      </button>
      <div class="toolbar-title">[Glabel] Workspace</div>
      <div class="toolbar-actions">
        <button class="btn"><span class="icon">[Save]</span></button>
        <button class="btn"><span class="icon">[Deploy]</span></button>
      </div>
    </header>
    
    <div class="main-area">
      <aside class="node-palette">
        <div class="panel-header">Node Palette</div>
        <div class="palette-items">
          <div class="palette-item">[+] Input</div>
          <div class="palette-item">[+] Inference</div>
          <div class="palette-item">[+] Output</div>
        </div>
      </aside>
      
      <main class="canvas-area">
        <VueFlow :nodes="nodes" :edges="edges" fit-view-on-init />
      </main>
      
      <aside class="properties-panel">
        <div class="panel-header">Properties</div>
        <div class="properties-content">
          <p>Select a node to view properties.</p>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { VueFlow } from '@vue-flow/core'

import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'

const router = useRouter()

const goHome = () => {
  router.push('/')
}

const nodes = ref([
  { id: '1', type: 'input', label: 'Input Image', position: { x: 50, y: 150 } },
  { id: '2', type: 'default', label: 'Inference', position: { x: 250, y: 150 } },
  { id: '3', type: 'output', label: 'Output Result', position: { x: 450, y: 150 } }
])

const edges = ref([
  { id: 'e1-2', source: '1', target: '2' },
  { id: 'e2-3', source: '2', target: '3' }
])
</script>

<style scoped>
.workspace-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #fdfcfc;
  color: #201d1d;
  font-family: 'Berkeley Mono', monospace;
  overflow: hidden;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid #646262;
  background-color: #fdfcfc;
  height: 50px;
  box-sizing: border-box;
}

.toolbar-title {
  font-weight: bold;
}

.toolbar-actions {
  display: flex;
  gap: 0.5rem;
}

.btn {
  background: transparent;
  color: #201d1d;
  border: 1px solid #646262;
  border-radius: 4px;
  padding: 0.25rem 0.75rem;
  font-family: 'Berkeley Mono', monospace;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.btn:hover {
  background: #201d1d;
  color: #fdfcfc;
}

.main-area {
  display: flex;
  flex: 1;
  height: calc(100vh - 50px);
}

.node-palette {
  width: 250px;
  border-right: 1px solid #646262;
  background-color: #fdfcfc;
  display: flex;
  flex-direction: column;
}

.canvas-area {
  flex: 1;
  background-color: #fdfcfc;
  position: relative;
}

.properties-panel {
  width: 300px;
  border-left: 1px solid #646262;
  background-color: #fdfcfc;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 0.5rem 1rem;
  border-bottom: 1px solid #646262;
  font-weight: bold;
  background-color: rgba(15,0,0,0.02);
}

.palette-items {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.palette-item {
  border: 1px solid #646262;
  padding: 0.5rem;
  cursor: grab;
  background-color: #fdfcfc;
}

.palette-item:hover {
  background-color: rgba(15,0,0,0.05);
}

.properties-content {
  padding: 1rem;
}
</style>
