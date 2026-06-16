<template>
  <div class="custom-node">
    <Handle type="target" position="left" />
    <div class="node-header">[Output] {{ data.label }}</div>
    <div class="node-body">
      <div class="preview-box">NO SIGNAL</div>
    </div>
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
.preview-box {
  background: rgba(100, 98, 98, 0.1);
  border: 1px solid #646262;
  text-align: center;
  padding: 1rem 0;
  font-size: 0.8em;
  color: #646262;
}
</style>
