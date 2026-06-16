<template>
  <div class="workspace-layout">
    <header class="toolbar">
      <button class="btn" @click="goHome">
        <span class="icon">[<]</span> Back to Playgrounds
      </button>
      <div class="toolbar-title">[Glabel] Workspace</div>
      <div class="toolbar-actions">
        <button class="btn" @click="savePipeline"><span class="icon">[Save]</span></button>
        <button class="btn" @click="deployPipeline"><span class="icon">[Deploy]</span></button>
      </div>
    </header>
    
    <div class="main-area">
      <aside class="node-palette">
        <div class="panel-header">Node Palette</div>
        <div class="palette-items">
          <div class="palette-item" draggable="true" @dragstart="onDragStart($event, 'customInput')">[+] Input</div>
          <div class="palette-item" draggable="true" @dragstart="onDragStart($event, 'customInference')">[+] Inference</div>
          <div class="palette-item" draggable="true" @dragstart="onDragStart($event, 'customOutput')">[+] Output</div>
        </div>
      </aside>
      
      <main class="canvas-area" @drop="onDrop" @dragover.prevent>
        <VueFlow :nodes="nodes" :edges="edges" fit-view-on-init>
          <template #node-customInput="props">
            <InputNode :data="props.data" />
          </template>
          <template #node-customInference="props">
            <InferenceNode :data="props.data" />
          </template>
          <template #node-customOutput="props">
            <OutputNode :data="props.data" />
          </template>
        </VueFlow>
        <div class="canvas-tools">
          <button class="btn sm-btn" @click="zoomIn">[+] Zoom In</button>
          <button class="btn sm-btn" @click="zoomOut">[-] Zoom Out</button>
        </div>
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
import { VueFlow, useVueFlow } from '@vue-flow/core'

import InputNode from '../components/nodes/InputNode.vue'
import InferenceNode from '../components/nodes/InferenceNode.vue'
import OutputNode from '../components/nodes/OutputNode.vue'

import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'

const router = useRouter()

const goHome = () => {
  router.push('/playgrounds')
}

const nodes = ref([
  { id: '1', type: 'customInput', data: { label: 'Input Image' }, position: { x: 50, y: 150 } },
  { id: '2', type: 'customInference', data: { label: 'Inference' }, position: { x: 250, y: 150 } },
  { id: '3', type: 'customOutput', data: { label: 'Output Result' }, position: { x: 450, y: 150 } }
])

const edges = ref([
  { id: 'e1-2', source: '1', target: '2' },
  { id: 'e2-3', source: '2', target: '3' }
])

const { project, zoomIn, zoomOut } = useVueFlow()
let id = 4

const onDragStart = (event, nodeType) => {
  if (event.dataTransfer) {
    event.dataTransfer.setData('application/vueflow', nodeType)
    event.dataTransfer.effectAllowed = 'move'
  }
}

const onDrop = (event) => {
  const nodeType = event.dataTransfer?.getData('application/vueflow')

  if (!nodeType) {
    return
  }

  const position = project({
    x: event.clientX,
    y: event.clientY,
  })

  // Alternatively just use offsetX / offsetY
  const newNode = {
    id: `dndnode_${id++}`,
    type: nodeType,
    position: { x: event.offsetX, y: event.offsetY },
    data: { label: `${nodeType} node` },
  }

  nodes.value.push(newNode)
}

const savePipeline = () => {
  alert('Mock: Saving pipeline...')
}

const deployPipeline = () => {
  alert('Mock: Exporting to Python script...')
}
</script>

<style scoped>
.workspace-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--bg-color, #fdfcfc);
  color: var(--text-color, #201d1d);
  font-family: 'Berkeley Mono', monospace;
  overflow: hidden;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid var(--border-color, #646262);
  background-color: var(--bg-color, #fdfcfc);
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
  color: var(--text-color, #201d1d);
  border: 1px solid var(--border-color, #646262);
  border-radius: 4px;
  padding: 0.25rem 0.75rem;
  font-family: inherit;
  font-size: inherit;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.btn:hover {
  background: var(--text-color, #201d1d);
  color: var(--bg-color, #fdfcfc);
}

.sm-btn {
  padding: 0.2rem 0.5rem;
  font-size: 0.85rem;
}

.main-area {
  display: flex;
  flex: 1;
  height: calc(100vh - 50px);
}

.node-palette {
  width: 250px;
  border-right: 1px solid var(--border-color, #646262);
  background-color: var(--bg-color, #fdfcfc);
  display: flex;
  flex-direction: column;
}

.canvas-area {
  flex: 1;
  background-color: var(--bg-color, #fdfcfc);
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.05'/%3E%3C/svg%3E");
  position: relative;
}

.canvas-tools {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  display: flex;
  gap: 0.5rem;
  z-index: 10;
}

.properties-panel {
  width: 300px;
  border-left: 1px solid var(--border-color, #646262);
  background-color: var(--bg-color, #fdfcfc);
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 0.5rem 1rem;
  border-bottom: 1px solid var(--border-color, #646262);
  font-weight: bold;
  background-color: var(--hover-bg, rgba(15,0,0,0.02));
}

.palette-items {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.palette-item {
  border: 1px solid var(--border-color, #646262);
  padding: 0.5rem;
  cursor: grab;
  background-color: var(--bg-color, #fdfcfc);
}

.palette-item:hover {
  background-color: var(--hover-bg, rgba(15,0,0,0.05));
}

.properties-content {
  padding: 1rem;
}
</style>
