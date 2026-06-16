<template>
  <div class="custom-node">
    <Handle type="target" position="left" />
    <div class="node-header">[Inference] {{ data.label }}</div>
    <div class="node-body">
      <div>Model: YOLOv8n</div>
      <div>Conf: 0.5</div>
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
.node-body {
  font-size: 0.9em;
}
</style>
