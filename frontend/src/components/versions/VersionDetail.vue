<script setup>
import { ref } from 'vue'
import SplitBar from './SplitBar.vue'

const props = defineProps({
  version: {
    type: Object,
    default: null
  },
  visible: {
    type: Boolean,
    default: false
  },
  projectId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close', 'delete', 'export'])

const exportFormat = ref('yolo')
</script>

<template>
  <div v-if="visible && version" class="detail-backdrop" @click="emit('close')">
    <div class="detail-panel" @click.stop>
      <div class="panel-header">
        <h3>{{ version.name }}</h3>
        <button class="close-btn" @click="emit('close')">[x]</button>
      </div>
      
      <div class="panel-content">
        <div class="section">
          <h4>Details</h4>
          <p><strong>Created:</strong> {{ new Date(version.created_at).toLocaleString() }}</p>
          <p><strong>Assets:</strong> {{ version.asset_count }}</p>
        </div>

        <div class="section" v-if="version.split">
          <h4>Split Ratios</h4>
          <SplitBar :train="version.split.train" :valid="version.split.valid" :test="version.split.test" />
          <div class="split-stats">
            <span>Train: {{ version.split.train }}%</span>
            <span>Valid: {{ version.split.valid }}%</span>
            <span>Test: {{ version.split.test }}%</span>
          </div>
        </div>

        <div class="section" v-if="version.preprocessing?.length">
          <h4>Preprocessing</h4>
          <ul class="steps-list">
            <li v-for="step in version.preprocessing" :key="step">
              {{ step }}
            </li>
          </ul>
        </div>

        <div class="section" v-if="version.augmentations?.length">
          <h4>Augmentations</h4>
          <p v-if="version.multiplier"><strong>Multiplier:</strong> {{ version.multiplier }}x</p>
          <ul class="steps-list">
            <li v-for="aug in version.augmentations" :key="aug">
              {{ aug }}
            </li>
          </ul>
        </div>
      </div>

      <div class="panel-footer">
        <div class="export-group">
          <select v-model="exportFormat" class="format-select">
            <option value="yolo">YOLO</option>
            <option value="coco">COCO</option>
          </select>
          <button class="action-btn" @click="emit('export', { version, format: exportFormat })">Export</button>
        </div>
        <button class="action-btn danger-btn" @click="emit('delete', version)">Delete</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.detail-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  justify-content: flex-end;
}

.detail-panel {
  width: 400px;
  max-width: 100%;
  height: 100%;
  background: var(--bg-color, #121212);
  border-left: 1px solid var(--border-color, #646262);
  display: flex;
  flex-direction: column;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #646262;
}

.panel-header h3 {
  margin: 0;
}

.close-btn {
  background: transparent;
  border: none;
  color: inherit;
  font-size: 1.2rem;
  cursor: pointer;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.section h4 {
  margin: 0 0 1rem 0;
  color: var(--text-color, #fdfcfc);
  border-bottom: 1px dashed #333;
  padding-bottom: 0.5rem;
}

.section p {
  margin: 0.5rem 0;
}

.split-stats {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: var(--mute, #888);
  margin-top: 0.5rem;
}

.steps-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.steps-list li {
  background: #201d1d;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: 1px solid #333;
}

.panel-footer {
  padding: 1.5rem;
  border-top: 1px solid #646262;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.export-group {
  display: flex;
  gap: 0.5rem;
}

.format-select {
  background: transparent;
  color: inherit;
  border: 1px solid #646262;
  padding: 0.5rem;
  border-radius: 4px;
}

.action-btn {
  background: transparent;
  border: 1px solid #646262;
  color: inherit;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.action-btn:hover {
  background: #333;
}

.danger-btn {
  color: #e06c75;
  border-color: #e06c75;
}

.danger-btn:hover {
  background: rgba(224, 108, 117, 0.1);
}
</style>
