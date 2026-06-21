<script setup>
import { ref, onMounted, computed } from 'vue'
import { listModels, downloadModel, detectHardware } from '../api/client.js'

const sysInfo = ref(null)
const recommendedModels = ref([])
const models = ref([])
const error = ref(null)
const downloadingModels = ref(new Set())

const detectSystem = async () => {
  try {
    sysInfo.value = { loading: true }
    const hw = await detectHardware()
    sysInfo.value = hw
    recommendedModels.value = hw.recommended_models || []
  } catch (err) {
    alert("Hardware detection failed: " + err.message)
    sysInfo.value = null
  }
}

const loadModels = async () => {
  try {
    const data = await listModels()
    models.value = data
  } catch (err) {
    error.value = "Failed to load models: " + err.message
  }
}

const handleDownload = async (modelId) => {
  try {
    downloadingModels.value.add(modelId)
    await downloadModel(modelId)
    // Reload to refresh status
    await loadModels()
  } catch (err) {
    alert("Download failed: " + err.message)
  } finally {
    downloadingModels.value.delete(modelId)
  }
}

const groupedModels = computed(() => {
  const groups = {}
  models.value.forEach(m => {
    if (!groups[m.architecture]) groups[m.architecture] = []
    groups[m.architecture].push(m)
  })
  return groups
})

onMounted(() => {
  loadModels()
})
</script>

<template>
  <div class="settings-container">
    <header class="header">
      <h1>Settings</h1>
      <p>Local Configuration</p>
    </header>

    <main class="main-content">
      <div class="settings-section">
        <h3>Hardware Target</h3>
        <div style="display: flex; gap: 1rem; align-items: center; margin-bottom: 0.5rem;">
          <select class="austere-input" style="flex: 1; margin-bottom: 0;">
            <option>Auto (Detect)</option>
            <option>CPU</option>
            <option>GPU (CUDA)</option>
            <option>MPS (Apple Silicon)</option>
          </select>
          <button class="btn" @click="detectSystem">[Detect System]</button>
        </div>
        <div v-if="sysInfo && !sysInfo.loading" class="sys-info-box">
          <p class="desc sys-detail"><strong>OS:</strong> {{ sysInfo.os }}</p>
          <p class="desc sys-detail"><strong>CPU:</strong> {{ sysInfo.cpu }}</p>
          <p class="desc sys-detail"><strong>RAM:</strong> {{ sysInfo.ram_gb }} GB</p>
          <p v-if="sysInfo.gpu" class="desc sys-detail" style="color: #4caf50;">
            <strong>GPU:</strong> {{ sysInfo.gpu }} 
            <span v-if="sysInfo.vram_gb">({{ sysInfo.vram_gb }} GB VRAM)</span>
          </p>
          <div v-if="recommendedModels.length" class="recommendation-box">
            <strong>★ Recommended Models:</strong> {{ recommendedModels.join(', ') }}
          </div>
        </div>
        <p v-else-if="sysInfo?.loading" class="desc sys-info">Detecting hardware...</p>
      </div>

      <div class="settings-section">
        <h3>Data Directory</h3>
        <p class="desc">Location where local datasets and models are saved.</p>
        <input type="text" value="./glabel_data" class="austere-input" />
      </div>

      <div class="settings-section">
        <h3>Model Repository</h3>
        <p class="desc">Download Ultralytics-compatible models for Auto-Annotation and Training.</p>
        
        <p v-if="error" style="color: var(--danger, #ff3b30);">[!] {{ error }}</p>

        <div v-for="(group, arch) in groupedModels" :key="arch" class="model-group">
          <h4 class="group-title">{{ arch }}</h4>
          <div class="list-row" v-for="m in group" :key="m.id">
            <div class="model-info">
              <span class="model-name">[-] {{ m.name }}</span>
              <span class="model-meta">Task: {{ m.task_type }}</span>
            </div>
            <div class="model-action">
              <span v-if="m.is_downloaded" class="status-available">[Available]</span>
              
              <template v-else-if="m.architecture.includes('SAM 3')">
                <a href="https://huggingface.co/facebook/sam3" target="_blank" class="btn-small" style="text-decoration: none; display: inline-block;" title="Requires manual download from Hugging Face">
                  [Manual DL]
                </a>
              </template>

              <button 
                v-else-if="!downloadingModels.has(m.id)"
                class="btn-small" 
                @click="handleDownload(m.id)"
              >
                [Download]
              </button>
              <button 
                v-else
                class="btn-small disabled" 
                disabled
              >
                [Downloading...]
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="settings-section">
        <button class="btn">[Save Configuration]</button>
      </div>
    </main>
  </div>
</template>

<style scoped>
.settings-container {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.header {
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--border-color, #646262);
  padding-bottom: 1rem;
}

.header h1 {
  font-size: 1.5rem;
  margin: 0;
}

.header p {
  margin: 0.5rem 0 0 0;
  color: var(--border-color, #646262);
}

.settings-section {
  margin-bottom: 2rem;
}

.settings-section h3 {
  margin-bottom: 0.5rem;
}

.desc {
  color: var(--border-color, #646262);
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.austere-input {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid var(--border-color, #646262);
  background: transparent;
  color: var(--text-color, #201d1d);
  padding: 0.5rem;
  font-family: inherit;
}
.austere-input:focus {
  outline: 1px solid var(--text-color, #201d1d);
}

select.austere-input option {
  background-color: var(--bg-color, #fdfcfc);
  color: var(--text-color, #201d1d);
}

.sys-info {
  margin-top: 0.5rem;
  color: #4caf50;
}

.sys-info-box {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px dashed var(--border-color, #646262);
  background: rgba(100, 98, 98, 0.05);
}

.sys-detail {
  margin: 0.2rem 0;
  font-family: monospace;
}

.recommendation-box {
  margin-top: 1rem;
  padding: 0.5rem;
  background: var(--text-color, #201d1d);
  color: var(--bg-color, #fdfcfc);
  font-size: 0.9rem;
  border-radius: 4px;
}

.btn {
  background: transparent;
  color: var(--text-color, #201d1d);
  border: 1px solid var(--border-color, #646262);
  border-radius: 4px;
  padding: 0.5rem 1rem;
  font-family: inherit;
  font-size: inherit;
  cursor: pointer;
}

.btn:hover {
  background: var(--text-color, #201d1d);
  color: var(--bg-color, #fdfcfc);
}

.model-group {
  margin-bottom: 1.5rem;
  border-top: 1px solid var(--border-color, #646262);
  padding-top: 1rem;
}

.group-title {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  font-weight: bold;
}

.list-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid rgba(100, 98, 98, 0.2);
}

.model-info {
  display: flex;
  flex-direction: column;
}

.model-name {
  font-weight: bold;
}

.model-meta {
  font-size: 0.85rem;
  color: var(--border-color, #646262);
  margin-left: 1.8rem;
}

.btn-small {
  background: transparent;
  color: var(--text-color, #201d1d);
  border: 1px solid var(--border-color, #646262);
  border-radius: 4px;
  padding: 4px 12px;
  font-family: inherit;
  font-size: 0.85rem;
  cursor: pointer;
}

.btn-small:hover:not(.disabled) {
  background: var(--text-color, #201d1d);
  color: var(--bg-color, #fdfcfc);
}

.btn-small.disabled {
  color: var(--border-color, #646262);
  cursor: not-allowed;
  border-color: rgba(100, 98, 98, 0.3);
}

.status-available {
  color: #30d158; /* Apple Success */
  font-size: 0.85rem;
}
</style>
