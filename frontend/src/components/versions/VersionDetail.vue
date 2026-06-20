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
          <h4>[+] Details</h4>
          <div class="detail-row">
            <span class="detail-key">Created:</span>
            <span class="detail-val">{{ new Date(version.created_at).toLocaleString() }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-key">Assets:</span>
            <span class="detail-val">{{ version.asset_count }}</span>
          </div>
          <div class="detail-row" v-if="version.description">
            <span class="detail-key">Note:</span>
            <span class="detail-val">{{ version.description }}</span>
          </div>
        </div>

        <div class="section" v-if="version.split">
          <h4>[+] Split Ratios</h4>
          <SplitBar :train="version.split.train" :valid="version.split.valid" :test="version.split.test" />
          <div class="split-stats">
            <span>Train: {{ version.split.train }}%</span>
            <span>Valid: {{ version.split.valid }}%</span>
            <span>Test: {{ version.split.test }}%</span>
          </div>
        </div>

        <div class="section" v-if="version.preprocessing?.length">
          <h4>[+] Preprocessing</h4>
          <ul class="steps-list">
            <li v-for="step in version.preprocessing" :key="step">
              [-] {{ step }}
            </li>
          </ul>
        </div>

        <div class="section" v-if="version.augmentations?.length">
          <h4>[+] Augmentations</h4>
          <div class="detail-row" v-if="version.multiplier">
            <span class="detail-key">Multiplier:</span>
            <span class="detail-val">{{ version.multiplier }}x</span>
          </div>
          <ul class="steps-list">
            <li v-for="aug in version.augmentations" :key="aug">
              [-] {{ aug }}
            </li>
          </ul>
        </div>
      </div>

      <div class="panel-footer">
        <div class="export-group">
          <select v-model="exportFormat" class="text-input">
            <option value="yolo">YOLO</option>
            <option value="coco">COCO</option>
          </select>
          <button class="btn-primary" @click="emit('export', { version, format: exportFormat })">Export</button>
        </div>
        <button class="btn-secondary danger-btn" @click="emit('delete', version)">Delete</button>
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
  background: rgba(0, 0, 0, 0.4);
  z-index: var(--z-modal);
  display: flex;
  justify-content: flex-end;
}

.detail-panel {
  width: 400px;
  max-width: 100%;
  height: 100%;
  background: var(--bg-color);
  border-left: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  animation: slideIn 0.2s ease-out;
}

@keyframes slideIn {
  from { transform: translateX(100%); }
  to { transform: translateX(0); }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid var(--hairline);
}

.panel-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--mute);
  font-family: inherit;
  font-size: 1rem;
  cursor: pointer;
  padding: 0;
}

.close-btn:hover {
  color: var(--text-color);
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.section h4 {
  margin: 0 0 16px 0;
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-color);
}

.detail-row {
  display: grid;
  grid-template-columns: 100px 1fr;
  margin-bottom: 8px;
  font-size: 0.9rem;
}

.detail-key {
  color: var(--mute);
}

.detail-val {
  color: var(--body);
}

.split-stats {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: var(--mute);
  margin-top: 12px;
}

.steps-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 0.9rem;
  color: var(--body);
}

.panel-footer {
  padding: 24px;
  border-top: 1px solid var(--hairline);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.export-group {
  display: flex;
  gap: 12px;
}

.text-input {
  background: var(--surface-soft);
  color: var(--text-color);
  border: 1px solid var(--hairline);
  border-radius: 4px;
  padding: 8px 12px;
  font-family: inherit;
  font-size: 0.9rem;
}

.text-input:focus {
  background: var(--bg-color);
  border-color: var(--text-color);
  outline: none;
}

.btn-primary {
  background: var(--text-color);
  color: var(--bg-color);
  border: none;
  border-radius: 4px;
  padding: 8px 20px;
  font-family: inherit;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-secondary {
  background: transparent;
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 8px 20px;
  font-family: inherit;
  font-weight: 500;
  cursor: pointer;
}

.btn-secondary:hover {
  background: var(--hover-bg);
}

.danger-btn {
  color: var(--danger);
  border-color: var(--danger);
}

.danger-btn:hover {
  background: rgba(255, 59, 48, 0.1);
}
</style>
