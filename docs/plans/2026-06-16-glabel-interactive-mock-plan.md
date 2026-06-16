# Glabel Interactive Mock & Custom Nodes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the frontend fully interactive for E2E testing with mock data and implement custom austere VueFlow nodes.

**Architecture:** Vue 3 Composition API. We will use Vue's reactivity to handle mock state in the Dashboard. For the Workspace, we will register custom node types in VueFlow and implement a drag-and-drop mechanism from the Palette to the Canvas.

**Tech Stack:** Vue 3, Vue Router, `@vue-flow/core`.

---

### Task 1: Dashboard Interactivity

**Files:**
- Modify: `frontend/src/views/Dashboard.vue`

- [ ] **Step 1: Make Recent Workspaces Interactive**
Update the `recentWorkspaces` to be reactive.
Implement a `removeWorkspace(id)` function that filters out the workspace from the array.
Bind the `[-] Remove` button to `removeWorkspace(ws.id)`.
Bind clicking on the workspace row (or adding an `[Open]` button) to route to `/workspace?id=...`.

- [ ] **Step 2: Make "Open Vision Solution" Interactive**
Create a `openSolution()` function that triggers a native browser `alert('Mock: Opening File Picker...')` or simulates loading a file and routing to `/workspace`.

- [ ] **Step 3: Commit**
```bash
git add frontend/src/views/Dashboard.vue
git commit -m "feat: add interactivity to dashboard actions"
```

### Task 2: Custom VueFlow Nodes

**Files:**
- Create: `frontend/src/components/nodes/InputNode.vue`
- Create: `frontend/src/components/nodes/InferenceNode.vue`
- Create: `frontend/src/components/nodes/OutputNode.vue`
- Modify: `frontend/src/views/Workspace.vue`

- [ ] **Step 1: Create InputNode.vue**
Austere design. Displays the node label and a mock `<select>` for Camera/Video. Includes a right `<Handle>`.

```vue
<template>
  <div class="custom-node">
    <div class="node-header">[Input] {{ data.label }}</div>
    <div class="node-body">
      <select class="mock-select"><option>Webcam 0</option></select>
    </div>
    <Handle type="source" position="right" />
  </div>
</template>
<script setup>
import { Handle } from '@vue-flow/core'
defineProps(['data'])
</script>
<style scoped>
.custom-node { border: 1px solid #646262; background: #fdfcfc; font-family: 'Berkeley Mono', monospace; min-width: 150px; }
.node-header { background: rgba(15,0,0,0.02); padding: 4px 8px; border-bottom: 1px solid #646262; font-size: 0.85rem; font-weight: bold; }
.node-body { padding: 8px; }
.mock-select { background: transparent; border: 1px solid #646262; font-family: inherit; width: 100%; }
</style>
```

- [ ] **Step 2: Create InferenceNode.vue**
Requires both left and right Handles. Displays mock sliders or text for "Model" and "Confidence".

```vue
<template>
  <div class="custom-node">
    <Handle type="target" position="left" />
    <div class="node-header">[Inference] {{ data.label }}</div>
    <div class="node-body">
      <div class="mock-text">Model: YOLOv8n</div>
      <div class="mock-text">Conf: 0.5</div>
    </div>
    <Handle type="source" position="right" />
  </div>
</template>
<script setup>
import { Handle } from '@vue-flow/core'
defineProps(['data'])
</script>
<style scoped>
.custom-node { border: 1px solid #646262; background: #fdfcfc; font-family: 'Berkeley Mono', monospace; min-width: 150px; }
.node-header { background: rgba(15,0,0,0.02); padding: 4px 8px; border-bottom: 1px solid #646262; font-size: 0.85rem; font-weight: bold; }
.node-body { padding: 8px; }
.mock-text { font-size: 0.8rem; margin-bottom: 4px; }
</style>
```

- [ ] **Step 3: Create OutputNode.vue**
Requires left Handle. Contains a grey box representing a mock image preview.

```vue
<template>
  <div class="custom-node">
    <Handle type="target" position="left" />
    <div class="node-header">[Output] {{ data.label }}</div>
    <div class="node-body">
      <div class="mock-preview">NO SIGNAL</div>
    </div>
  </div>
</template>
<script setup>
import { Handle } from '@vue-flow/core'
defineProps(['data'])
</script>
<style scoped>
.custom-node { border: 1px solid #646262; background: #fdfcfc; font-family: 'Berkeley Mono', monospace; width: 200px; }
.node-header { background: rgba(15,0,0,0.02); padding: 4px 8px; border-bottom: 1px solid #646262; font-size: 0.85rem; font-weight: bold; }
.node-body { padding: 8px; }
.mock-preview { width: 100%; height: 100px; background: rgba(15,0,0,0.05); border: 1px dashed #646262; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; color: #646262; }
</style>
```

- [ ] **Step 4: Register Custom Nodes in Workspace.vue**
Import the 3 node components. Use `<template #node-customInput="props">` mapping in VueFlow or pass them via `nodeTypes` property if applicable. Actually, in VueFlow you use template slots:
```vue
<VueFlow :nodes="nodes" :edges="edges" fit-view-on-init>
  <template #node-customInput="props"><InputNode :data="props.data" /></template>
  <template #node-customInference="props"><InferenceNode :data="props.data" /></template>
  <template #node-customOutput="props"><OutputNode :data="props.data" /></template>
</VueFlow>
```
Update `nodes` ref to use `type: 'customInput'`, `type: 'customInference'`, `type: 'customOutput'`.

- [ ] **Step 5: Commit**
```bash
git add frontend/src/
git commit -m "feat: implement custom austere vueflow nodes"
```

### Task 3: Workspace Drag & Drop and Interactivity

**Files:**
- Modify: `frontend/src/views/Workspace.vue`

- [ ] **Step 1: Implement Drag & Drop**
Make Node Palette items draggable: `draggable="true" @dragstart="onDragStart($event, 'customInput')"`.
Add `@drop="onDrop"` and `@dragover.prevent` to the `canvas-area` div.
In `onDrop`, calculate position and push a new node to the `nodes` array.

- [ ] **Step 2: Connect Toolbar Actions**
Make `[Save]` and `[Deploy]` buttons trigger `alert('Mock: Saving pipeline...')` and `alert('Mock: Exporting to Python script...')`.

- [ ] **Step 3: Commit**
```bash
git add frontend/src/views/Workspace.vue
git commit -m "feat: add drag and drop and toolbar mock actions"
```
