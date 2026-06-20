<template>
  <div v-if="visible" class="modal-backdrop" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3 class="modal-title">Preview: {{ augmentationKey }}</h3>
        <button @click="$emit('close')" class="close-btn">[x]</button>
      </div>
      
      <div class="modal-body">
        <div class="preview-grid">
          <!-- Original -->
          <div class="preview-col">
            <span class="preview-label">Original</span>
            <div class="image-container">
              <img v-if="originalUrl" :src="originalUrl" class="preview-img" />
              <div v-else class="loading-state">Loading...</div>
            </div>
          </div>
          <!-- Preview -->
          <div class="preview-col">
            <span class="preview-label">Preview</span>
            <div class="image-container">
              <img v-if="previewUrl" :src="previewUrl" class="preview-img" />
              <div v-if="loadingPreview" class="loading-overlay">
                <span class="loading-badge">Loading...</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Controls -->
        <div class="controls-section">
          <div class="controls-header">
            <h4>Parameters</h4>
            <button @click="fetchPreview" class="btn-secondary small">
              [ Regenerate ]
            </button>
          </div>
          
          <div class="params-grid">
            <div v-for="(val, key) in localParams" :key="key" class="param-row">
              <div class="param-labels">
                <label>{{ key.replace('_', ' ') }}</label>
                <span class="param-val">{{ localParams[key] }}</span>
              </div>
              <input 
                type="range" 
                v-model.number="localParams[key]" 
                :min="getMin(key)" 
                :max="getMax(key)" 
                :step="getStep(key)"
                @input="onParamChange"
                class="range-slider"
              />
            </div>
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button @click="$emit('close')" class="btn-secondary">Cancel</button>
        <button @click="apply" class="btn-primary">Apply</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'
import { previewAugmentation, listDatasetAssets, API_BASE_URL } from '../../api/client.js'

const props = defineProps({
  projectId: String,
  augmentationKey: String,
  params: Object,
  visible: Boolean
})

const emit = defineEmits(['close', 'update:params'])

const originalUrl = ref(null)
const previewUrl = ref(null)
const loadingPreview = ref(false)
const localParams = ref({})
let debounceTimeout = null
let currentAssetId = null

const paramRanges = {
  degrees: { min: -180, max: 180, step: 1 },
  factor: { min: 0, max: 2, step: 0.1 },
  kernel_size: { min: 1, max: 31, step: 2 },
  amount: { min: 0, max: 0.5, step: 0.01 },
  holes: { min: 1, max: 20, step: 1 },
  length: { min: 5, max: 200, step: 1 },
  h: { min: 0, max: 1, step: 0.01 },
  s: { min: 0, max: 1, step: 0.01 },
  v: { min: 0, max: 1, step: 0.01 },
  probability: { min: 0, max: 1, step: 0.05 }
}

function getMin(key) { return paramRanges[key]?.min ?? 0 }
function getMax(key) { return paramRanges[key]?.max ?? 100 }
function getStep(key) { return paramRanges[key]?.step ?? 1 }

watch(() => props.visible, async (newVal) => {
  if (newVal) {
    localParams.value = JSON.parse(JSON.stringify(props.params || {}))
    await fetchOriginal()
    fetchPreview()
  } else {
    if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = null
  }
}, { immediate: true })

async function fetchOriginal() {
  try {
    const assets = await listDatasetAssets(props.projectId)
    if (assets && assets.length > 0) {
      const randIdx = Math.floor(Math.random() * assets.length)
      const asset = assets[randIdx]
      currentAssetId = asset.id
      originalUrl.value = `${API_BASE_URL}/api/v1/projects/${props.projectId}/dataset/assets/${asset.id}/image`
    }
  } catch (err) {
    console.error("Failed to fetch original image", err)
  }
}

async function fetchPreview() {
  if (!currentAssetId) return
  loadingPreview.value = true
  try {
    const blob = await previewAugmentation(props.projectId, props.augmentationKey, localParams.value, currentAssetId)
    if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = URL.createObjectURL(blob)
  } catch (err) {
    console.error("Failed to fetch preview", err)
  } finally {
    loadingPreview.value = false
  }
}

function onParamChange() {
  if (debounceTimeout) clearTimeout(debounceTimeout)
  debounceTimeout = setTimeout(() => {
    fetchPreview()
  }, 500)
}

function apply() {
  emit('update:params', { ...localParams.value })
  emit('close')
}

onUnmounted(() => {
  if (debounceTimeout) clearTimeout(debounceTimeout)
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
})
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal);
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.4);
}

.modal-content {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  width: 900px;
  max-width: 95vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: none; /* explicitly removing shadows */
}

.modal-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--hairline);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--surface-soft);
}

.modal-title {
  margin: 0;
  font-size: 1.1rem;
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

.modal-body {
  padding: 24px;
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.preview-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.preview-col {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-label {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--body);
}

.image-container {
  background: var(--surface-soft);
  border: 1px solid var(--hairline);
  border-radius: 4px;
  aspect-ratio: 16 / 9;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.loading-state {
  color: var(--mute);
  font-size: 0.9rem;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(253, 252, 252, 0.5); /* matches canvas cream mostly */
  display: flex;
  align-items: center;
  justify-content: center;
}

[data-theme='dark'] .loading-overlay {
  background: rgba(26, 26, 26, 0.5);
}

.loading-badge {
  background: var(--bg-color);
  color: var(--text-color);
  padding: 4px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 0.85rem;
}

.controls-section {
  background: var(--surface-soft);
  padding: 16px;
  border-radius: 4px;
  border: 1px solid var(--hairline);
}

.controls-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.controls-header h4 {
  margin: 0;
  font-weight: 500;
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

.btn-secondary.small {
  padding: 4px 12px;
  font-size: 0.85rem;
}

.btn-secondary:hover {
  background: var(--hover-bg);
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

.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.param-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.param-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: var(--body);
  text-transform: capitalize;
}

.param-val {
  font-family: inherit;
}

.range-slider {
  width: 100%;
  cursor: pointer;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--hairline);
  background: var(--surface-soft);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
