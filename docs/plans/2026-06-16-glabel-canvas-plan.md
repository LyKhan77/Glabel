# Glabel Canvas Workspace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the infinite canvas workspace with VueFlow, including custom nodes, left palette, and right properties panel using mock data.

**Architecture:** Murni frontend Vue 3. Komponen utama adalah `Workspace.vue` yang membungkus komponen `<VueFlow>`. Terdapat integrasi *layouting* statis untuk mensimulasikan *Node Palette* dan *Properties Panel*.

**Tech Stack:** Vue 3, Vue Router, `@vue-flow/core`.

---

### Task 1: Setup Workspace Layout & Routing

**Files:**
- Create: `frontend/src/views/Workspace.vue`
- Modify: `frontend/src/main.js`
- Modify: `frontend/src/views/Dashboard.vue`

- [ ] **Step 1: Add Route in main.js**

```javascript
// Add to frontend/src/main.js routes array:
import Workspace from './views/Workspace.vue'
// ...
{ path: '/workspace', component: Workspace }
```

- [ ] **Step 2: Update Dashboard Navigation**

```javascript
// In frontend/src/views/Dashboard.vue
// Change the newPlayground function:
const newPlayground = () => {
  router.push('/workspace')
}
```

- [ ] **Step 3: Create Workspace Layout Shell**

```vue
<!-- frontend/src/views/Workspace.vue -->
<template>
  <div class="workspace-layout">
    <header class="toolbar">
      <button @click="$router.push('/')" class="nav-btn">[&lt;] Back to Home</button>
      <div class="workspace-title">Untitled Workspace.glabel</div>
      <div class="toolbar-actions">
        <span class="hw-target">[GPU: cuda:0]</span>
        <button class="export-btn">[x] Export</button>
      </div>
    </header>
    
    <div class="workspace-body">
      <aside class="node-palette">
        <h3>Node Palette</h3>
        <div class="node-item">[+] Camera Input</div>
        <div class="node-item">[+] YOLOv8 Inference</div>
        <div class="node-item">[+] Output Preview</div>
      </aside>
      
      <main class="canvas-area">
        <!-- VueFlow will go here -->
        <div style="padding: 1rem; color: #646262;">Loading Canvas...</div>
      </main>
      
      <aside class="properties-panel">
        <h3>Properties</h3>
        <p class="empty-state">Select a node to edit properties.</p>
      </aside>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.workspace-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #fdfcfc;
  color: #201d1d;
  font-family: 'Berkeley Mono', monospace;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.5rem;
  border-bottom: 1px solid #646262;
}

button {
  background: transparent;
  border: 1px solid #646262;
  color: #201d1d;
  padding: 0.25rem 0.75rem;
  font-family: inherit;
  cursor: pointer;
  border-radius: 4px;
}

button:hover {
  background: #201d1d;
  color: #fdfcfc;
}

.workspace-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.node-palette, .properties-panel {
  width: 250px;
  border-right: 1px solid #646262;
  padding: 1rem;
  background: #fdfcfc;
}

.properties-panel {
  border-right: none;
  border-left: 1px solid #646262;
}

h3 {
  font-size: 1rem;
  margin-top: 0;
  border-bottom: 1px dashed #646262;
  padding-bottom: 0.5rem;
}

.node-item {
  border: 1px solid #646262;
  padding: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  cursor: grab;
}

.canvas-area {
  flex: 1;
  position: relative;
  background: #f1eeee; /* slightly darker cream to distinguish canvas */
}

.empty-state {
  color: #646262;
  font-size: 0.9rem;
  font-style: italic;
}
</style>
```

- [ ] **Step 4: Commit**
```bash
git add frontend/src/
git commit -m "feat: add workspace layout and routing"
```

### Task 2: Implement VueFlow Canvas & Mock DAG

**Files:**
- Modify: `frontend/src/views/Workspace.vue`

- [ ] **Step 1: Import VueFlow and Add Mock Nodes**

Update `Workspace.vue` script setup:
```vue
<script setup>
import { ref } from 'vue'
import { VueFlow } from '@vue-flow/core'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'

const nodes = ref([
  { id: '1', type: 'input', label: 'Camera Stream', position: { x: 50, y: 150 } },
  { id: '2', type: 'default', label: 'YOLOv8 Inference', position: { x: 300, y: 150 } },
  { id: '3', type: 'output', label: 'Output Preview', position: { x: 550, y: 150 } }
])

const edges = ref([
  { id: 'e1-2', source: '1', target: '2', animated: true },
  { id: 'e2-3', source: '2', target: '3', animated: true }
])
</script>
```

- [ ] **Step 2: Render VueFlow in Canvas Area**

Update the template in `Workspace.vue` replacing the "Loading Canvas..." text:
```vue
      <main class="canvas-area">
        <VueFlow :nodes="nodes" :edges="edges" fit-view-on-init />
      </main>
```

Ensure `.canvas-area` has `height: 100%` in styles.

- [ ] **Step 3: Commit**
```bash
git add frontend/src/views/Workspace.vue
git commit -m "feat: integrate vue-flow with mock pipeline"
```
