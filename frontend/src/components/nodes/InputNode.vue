<template>
  <div class="custom-node">
    <div class="node-header">[Input] {{ data.label }}</div>
    <div class="node-body">
      <select>
        <option>Webcam 0</option>
      </select>
    </div>
    <Handle type="source" position="right" />
  </div>
</template>

<script setup>
import { Handle } from '@vue-flow/core'
defineProps(['data'])
</script>

<style scoped>
.custom-node {
  background: #fdfcfc;
  border: 1px solid #646262;
  color: #201d1d;
  font-family: 'Berkeley Mono', monospace;
  padding: 0.5rem;
  min-width: 150px;
}
.node-header {
  font-weight: bold;
  margin-bottom: 0.5rem;
  border-bottom: 1px dashed #646262;
  padding-bottom: 0.25rem;
}
.node-body select {
  width: 100%;
  font-family: 'Berkeley Mono', monospace;
  background: transparent;
  border: 1px solid #646262;
  color: #201d1d;
}
</style>
