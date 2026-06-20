<template>
  <div class="split-bar-container">
    <div class="split-bar">
      <div class="split-segment train" :style="{ width: train + '%' }" :title="'Train: ' + train + '%'"></div>
      <div class="split-segment valid" :style="{ width: valid + '%' }" :title="'Valid: ' + valid + '%'"></div>
      <div class="split-segment test" :style="{ width: test + '%' }" :title="'Test: ' + test + '%'"></div>
    </div>
    <div v-if="showLegend" class="split-legend">
      <span class="legend-item"><span class="box train"></span> Train ({{ train }}%)</span>
      <span class="legend-item"><span class="box valid"></span> Valid ({{ valid }}%)</span>
      <span class="legend-item"><span class="box test"></span> Test ({{ test }}%)</span>
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
  background: var(--surface-soft);
  border: 1px solid var(--hairline);
}

.split-segment {
  height: 100%;
  transition: width 0.3s ease;
}

.train { background-color: var(--success); }
.valid { background-color: var(--accent); }
.test { background-color: var(--warning); }

.split-legend {
  display: flex;
  gap: 16px;
  font-size: 0.85rem;
  color: var(--mute);
  font-family: inherit;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.box {
  width: 8px;
  height: 8px;
  border-radius: 2px;
}
</style>
