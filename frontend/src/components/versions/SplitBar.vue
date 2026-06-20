<template>
  <div class="split-bar-container">
    <div class="split-bar">
      <div class="split-segment train" :style="{ width: train + '%' }" :title="'Train: ' + train + '%'"></div>
      <div class="split-segment valid" :style="{ width: valid + '%' }" :title="'Valid: ' + valid + '%'"></div>
      <div class="split-segment test" :style="{ width: test + '%' }" :title="'Test: ' + test + '%'"></div>
    </div>
    <div v-if="showLegend" class="split-legend">
      <span class="legend-item"><span class="dot train"></span> Train ({{ train }}%)</span>
      <span class="legend-item"><span class="dot valid"></span> Valid ({{ valid }}%)</span>
      <span class="legend-item"><span class="dot test"></span> Test ({{ test }}%)</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  train: { type: Number, required: true },
  valid: { type: Number, required: true },
  test: { type: Number, required: true },
  showLegend: { type: Boolean, default: true }
});
</script>

<style scoped>
.split-bar-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.split-bar {
  display: flex;
  height: 8px;
  border-radius: 4px;
  overflow: hidden;
  background: var(--bg-surface, #1e1e1e);
}

.split-segment {
  height: 100%;
  transition: width 0.3s ease;
}

.train { background-color: var(--success, #10b981); }
.valid { background-color: var(--primary, #3b82f6); }
.test { background-color: var(--warning, #f59e0b); }

.split-legend {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: var(--text-secondary, #a0a0a0);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}
</style>
