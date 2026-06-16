<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const activeTab = ref('dataset') // 'dataset', 'versions', 'train'

// Dataset state
const datasetState = ref('unannotated') // 'unannotated', 'annotated'
const showUploadModal = ref(false)

const images = ref([
  { id: 1, annotated: false },
  { id: 2, annotated: false },
  { id: 3, annotated: false },
  { id: 4, annotated: false }
])

const unannotatedImages = computed(() => images.value.filter(img => !img.annotated))
const annotatedImages = computed(() => images.value.filter(img => img.annotated))

const goBack = () => {
  router.push('/')
}

const autoAnnotateAll = () => {
  images.value.forEach(img => {
    img.annotated = true
  })
}

const mockUpload = () => {
  const newId = images.value.length ? Math.max(...images.value.map(i => i.id)) + 1 : 1
  images.value.push({ id: newId, annotated: false })
  images.value.push({ id: newId + 1, annotated: false })
  showUploadModal.value = false
  alert('Mock: Media uploaded and processed!')
}

// Versions state
const versions = ref([])
const wizardStep = ref(0)

const generateVersion = () => {
  versions.value.push({ id: Date.now(), name: 'Version ' + (versions.value.length + 1) })
  wizardStep.value = 0
}

// Train state
const selectedVersion = ref(null)
const trainingProgress = ref(0)
const isTraining = ref(false)

const startTraining = () => {
  if (!selectedVersion.value) return
  isTraining.value = true
  trainingProgress.value = 0
  const interval = setInterval(() => {
    trainingProgress.value += 10
    if (trainingProgress.value >= 100) {
      clearInterval(interval)
      isTraining.value = false
    }
  }, 500)
}

const testInPlayground = () => {
  router.push('/playgrounds')
}
</script>

<template>
  <div class="project-view">
    <!-- Header / Nav -->
    <header class="header">
      <button class="nav-btn" @click="goBack">[&lt;] Back</button>
      <div class="tabs">
        <button 
          :class="['tab-btn', { active: activeTab === 'dataset' }]"
          @click="activeTab = 'dataset'"
        >[Dataset]</button>
        <button 
          :class="['tab-btn', { active: activeTab === 'versions' }]"
          @click="activeTab = 'versions'"
        >[Versions]</button>
        <button 
          :class="['tab-btn', { active: activeTab === 'train' }]"
          @click="activeTab = 'train'"
        >[Train]</button>
      </div>
      <div class="spacer"></div>
    </header>

    <main class="content">
      <div v-if="activeTab === 'dataset'" class="dataset-view">
        <div class="dataset-subnav">
          <div class="subtabs">
            <button 
              :class="['subtab-btn', { active: datasetState === 'unannotated' }]"
              @click="datasetState = 'unannotated'"
            >[Unannotated]</button>
            <button 
              :class="['subtab-btn', { active: datasetState === 'annotated' }]"
              @click="datasetState = 'annotated'"
            >[Annotated]</button>
          </div>
          <div class="actions">
            <button class="action-btn" v-if="datasetState === 'unannotated'" @click="autoAnnotateAll">
              [Auto-Annotate All (SAM3)]
            </button>
            <button class="action-btn" @click="showUploadModal = true">[Upload Media]</button>
          </div>
        </div>

        <div class="grid-container">
          <div v-if="datasetState === 'unannotated'" class="image-grid">
            <div class="image-card" v-for="img in unannotatedImages" :key="img.id">
              <div class="image-placeholder">Image {{ img.id }}</div>
            </div>
            <div v-if="unannotatedImages.length === 0" class="empty-state">
              No unannotated images.
            </div>
          </div>
          <div v-if="datasetState === 'annotated'" class="image-grid">
            <div class="image-card" v-for="img in annotatedImages" :key="img.id">
              <div class="image-placeholder">Image {{ img.id }}<br>(Annotated)</div>
            </div>
            <div v-if="annotatedImages.length === 0" class="empty-state">
              No annotated images.
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="activeTab === 'versions'" class="versions-view">
        <div class="versions-header">
          <h3>Versions</h3>
          <button class="action-btn" @click="wizardStep = wizardStep ? 0 : 1">[Generate New Version]</button>
        </div>
        
        <div v-if="wizardStep > 0" class="wizard-container">
          <div v-if="wizardStep === 1" class="wizard-step">
            <p>Train/Valid/Test Split (70/20/10)</p>
            <button class="action-btn" @click="wizardStep = 2">[Next]</button>
          </div>
          <div v-if="wizardStep === 2" class="wizard-step">
            <p>Preprocessing</p>
            <label><input type="checkbox" /> Resize</label>
            <label><input type="checkbox" /> Grayscale</label>
            <button class="action-btn" @click="wizardStep = 3">[Next]</button>
          </div>
          <div v-if="wizardStep === 3" class="wizard-step">
            <p>Augmentations</p>
            <label><input type="checkbox" /> Flip</label>
            <label><input type="checkbox" /> Rotate</label>
            <p>Multiplier: <input type="number" value="1" min="1" class="number-input" /></p>
            <button class="action-btn" @click="generateVersion">[Generate]</button>
          </div>
        </div>

        <ul class="version-list" v-if="versions.length > 0">
          <li v-for="version in versions" :key="version.id">
            {{ version.name }}
          </li>
        </ul>
        <div v-else class="empty-state">
          No versions generated yet.
        </div>
      </div>

      <div v-if="activeTab === 'train'" class="train-view">
        <div class="train-header">
          <h3>Train Model</h3>
        </div>
        <div class="train-controls">
          <label>Select Version: 
            <select v-model="selectedVersion" class="select-input">
              <option v-for="version in versions" :key="version.id" :value="version.id">
                {{ version.name }}
              </option>
            </select>
          </label>
          <button class="action-btn" @click="startTraining" :disabled="!selectedVersion || isTraining">[Start Training]</button>
        </div>
        
        <div v-if="trainingProgress > 0" class="progress-container">
          <p>Training Progress: {{ trainingProgress }}%</p>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: trainingProgress + '%' }"></div>
          </div>
        </div>
        
        <div v-if="trainingProgress === 100 && !isTraining" class="test-container">
          <button class="action-btn" @click="testInPlayground">[Test in Playground]</button>
        </div>
      </div>
    </main>

    <!-- Upload Media Modal -->
    <div v-if="showUploadModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Upload Media</h3>
          <button class="nav-btn" @click="showUploadModal = false">[x] Close</button>
        </div>
        <div class="modal-body">
          <div class="upload-options">
            <button class="action-btn" style="width: 100%; margin-bottom: 1rem;">[Choose Image Files]</button>
            <button class="action-btn" style="width: 100%;">[Choose Video File]</button>
          </div>
          <div style="margin-top: 1rem;">
            <label style="display: block; margin-bottom: 0.5rem;">Extract Frames per second (FPS)</label>
            <input type="number" placeholder="e.g. 2" class="number-input" style="width: 100%; display: block; box-sizing: border-box;" />
          </div>
          <div style="margin-top: 2rem; text-align: right;">
            <button class="action-btn" @click="mockUpload">[Upload & Process]</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.project-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #646262;
  gap: 2rem;
}

.tabs {
  display: flex;
  gap: 1rem;
}

.spacer {
  flex-grow: 1;
}

button {
  background: transparent;
  border: none;
  font-family: inherit;
  font-size: inherit;
  color: inherit;
  cursor: pointer;
}

button:hover {
  text-decoration: underline;
}

.nav-btn, .tab-btn, .subtab-btn, .action-btn {
  padding: 0.25rem 0.5rem;
}

.tab-btn.active, .subtab-btn.active {
  background: #201d1d;
  color: #fdfcfc;
}

.content {
  flex-grow: 1;
  padding: 1.5rem;
}

.dataset-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.dataset-subnav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px dashed #646262;
  padding-bottom: 1rem;
}

.subtabs {
  display: flex;
  gap: 1rem;
}

.actions {
  display: flex;
  gap: 1rem;
}

.grid-container {
  flex-grow: 1;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.image-card {
  aspect-ratio: 1;
  border: 1px solid #646262;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  text-align: center;
}

.image-placeholder {
  color: #646262;
}

.empty-state {
  color: #646262;
  font-style: italic;
  padding: 2rem 0;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  text-decoration: none;
}

.versions-view, .train-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.versions-header, .train-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px dashed #646262;
  padding-bottom: 1rem;
}

.versions-header h3, .train-header h3 {
  margin: 0;
  font-weight: normal;
}

.wizard-container {
  border: 1px solid #646262;
  padding: 1rem;
}

.wizard-step {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: flex-start;
}

.number-input, .select-input {
  font-family: inherit;
  font-size: inherit;
  color: inherit;
  background: transparent;
  border: 1px solid #646262;
  padding: 0.25rem;
}

.version-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.version-list li {
  border: 1px solid #646262;
  padding: 0.5rem;
}

.train-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.progress-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.progress-bar {
  height: 1rem;
  border: 1px solid #646262;
  width: 100%;
}

.progress-fill {
  height: 100%;
  background: var(--text-color, #201d1d);
  transition: width 0.3s;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(32, 29, 29, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-color, #fdfcfc);
  border: 1px solid var(--border-color, #646262);
  width: 500px;
  max-width: 90vw;
  padding: 1.5rem;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color, #646262);
  padding-bottom: 0.5rem;
}

.modal-header h3 {
  margin: 0;
}
</style>
