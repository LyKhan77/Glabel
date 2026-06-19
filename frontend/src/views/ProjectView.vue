<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  API_BASE_URL,
  assignDatasetAssets,
  autoAnnotateDataset,
  createDatasetVersion,
  deleteDatasetAssets,
  getProject,
  listDatasetAssets,
  listDatasetVersions,
  unassignDatasetAssets,
  uploadDatasetFiles
} from '../api/client'
import AnnotationWorkspace from '../components/AnnotationWorkspace.vue'

const router = useRouter()
const route = useRoute()
const projectId = computed(() => route.params.id)

const activeTab = ref('dataset') // 'dataset', 'versions', 'train'
const isAnnotating = ref(false)
const project = ref(null)
const assets = ref([])
const errorMessage = ref('')
const isLoading = ref(false)

// Dataset state
const fpsSlider = ref(2)
const isDragging = ref(false)
const showUploadModal = ref(false)
const fileInput = ref(null)

const selectedUnassigned = ref([])
const selectedAnnotating = ref([])

const onDragOver = (e) => { e.preventDefault(); isDragging.value = true }
const onDragLeave = (e) => { e.preventDefault(); isDragging.value = false }
const onDrop = (e) => {
  e.preventDefault(); 
  isDragging.value = false;
  uploadFiles(Array.from(e.dataTransfer.files))
}

const unassignedImages = computed(() => assets.value.filter(asset => asset.status === 'unassigned' && asset.kind !== 'video'))
const annotatingImages = computed(() => assets.value.filter(asset => (asset.status === 'unannotated' || asset.status === 'annotated') && asset.kind !== 'video'))
const allUnassignedSelected = computed(() => unassignedImages.value.length > 0 && selectedUnassigned.value.length === unassignedImages.value.length)

const toggleSelection = (id) => {
  const index = selectedUnassigned.value.indexOf(id)
  if (index === -1) {
    selectedUnassigned.value.push(id)
  } else {
    selectedUnassigned.value.splice(index, 1)
  }
}

const toggleAnnotatingSelection = (id) => {
  const index = selectedAnnotating.value.indexOf(id)
  if (index === -1) {
    selectedAnnotating.value.push(id)
  } else {
    selectedAnnotating.value.splice(index, 1)
  }
}

const assignSelected = async () => {
  if (!selectedUnassigned.value.length) return
  errorMessage.value = ''
  try {
    await assignDatasetAssets(projectId.value, selectedUnassigned.value)
    assets.value = await listDatasetAssets(projectId.value)
    selectedUnassigned.value = []
  } catch (error) {
    errorMessage.value = 'Failed to assign selected assets.'
  }
}

const toggleSelectAllUnassigned = () => {
  selectedUnassigned.value = allUnassignedSelected.value ? [] : unassignedImages.value.map(asset => asset.id)
}

const deleteSelectedUnassigned = async () => {
  if (!selectedUnassigned.value.length) return
  if (!window.confirm(`Delete ${selectedUnassigned.value.length} unassigned asset(s)?`)) return
  errorMessage.value = ''
  try {
    await deleteDatasetAssets(projectId.value, selectedUnassigned.value)
    assets.value = await listDatasetAssets(projectId.value)
    selectedUnassigned.value = []
  } catch (error) {
    errorMessage.value = 'Failed to delete selected assets.'
  }
}

const returnSelectedToUnassigned = async () => {
  if (!selectedAnnotating.value.length) return
  errorMessage.value = ''
  try {
    await unassignDatasetAssets(projectId.value, selectedAnnotating.value)
    assets.value = await listDatasetAssets(projectId.value)
    selectedAnnotating.value = []
  } catch (error) {
    errorMessage.value = 'Failed to return selected assets.'
  }
}

const openAnnotationWorkspace = () => {
  isAnnotating.value = true
}

const refreshDatasetAssets = async () => {
  assets.value = await listDatasetAssets(projectId.value)
}

const goBack = () => {
  router.push('/')
}

const loadProject = async () => {
  if (projectId.value === 'new') {
    errorMessage.value = 'Create a project from the dashboard first.'
    return
  }
  isLoading.value = true
  errorMessage.value = ''
  try {
    const [projectData, assetData, versionData] = await Promise.all([
      getProject(projectId.value),
      listDatasetAssets(projectId.value),
      listDatasetVersions(projectId.value)
    ])
    project.value = projectData
    assets.value = assetData
    versions.value = versionData
  } catch (error) {
    errorMessage.value = 'Could not load project data. Check backend status.'
  } finally {
    isLoading.value = false
  }
}

const autoAnnotateAll = async () => {
  errorMessage.value = ''
  try {
    await autoAnnotateDataset(projectId.value)
    assets.value = await listDatasetAssets(projectId.value)
  } catch (error) {
    errorMessage.value = 'Auto-annotate failed. Check backend status.'
  }
}

const chooseFiles = () => {
  fileInput.value?.click()
}

const onFileSelected = async (event) => {
  await uploadFiles(Array.from(event.target.files || []))
  event.target.value = ''
}

const uploadFiles = async (files) => {
  if (!files.length) return
  errorMessage.value = ''
  try {
    await uploadDatasetFiles(projectId.value, files, fpsSlider.value)
    assets.value = await listDatasetAssets(projectId.value)
  } catch (error) {
    errorMessage.value = 'Upload failed. Check file type and backend status.'
  }
  showUploadModal.value = false
}

// Versions state
const versions = ref([])
const wizardStep = ref(0)

const generateVersion = async () => {
  errorMessage.value = ''
  try {
    await createDatasetVersion(projectId.value, {
      name: 'Version ' + (versions.value.length + 1),
      split: { train: 70, valid: 20, test: 10 },
      preprocessing: ['resize'],
      augmentations: ['flip'],
      multiplier: 1
    })
    versions.value = await listDatasetVersions(projectId.value)
    wizardStep.value = 0
  } catch (error) {
    errorMessage.value = 'Could not create dataset version.'
  }
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

onMounted(loadProject)
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
      <div class="project-title">{{ project?.name || 'Project' }}</div>
    </header>

    <main class="content">
      <div v-if="isLoading" class="empty-state">Loading project...</div>
      <div v-if="errorMessage" class="empty-state error-state">{{ errorMessage }}</div>
      <div v-if="activeTab === 'dataset'" class="dataset-view">
        <div class="dataset-subnav">
          <div class="actions">
            <button class="action-btn" @click="autoAnnotateAll">
              [Auto-Annotate All (SAM3)]
            </button>
            <button class="action-btn" @click="showUploadModal = true">[Upload Media]</button>
          </div>
        </div>

        <AnnotationWorkspace 
          v-if="isAnnotating"
          :project="project"
          :assets="annotatingImages"
          :apiBaseUrl="API_BASE_URL"
          @close="isAnnotating = false"
          @saved="refreshDatasetAssets"
          @deleted="refreshDatasetAssets"
        />
        <div v-else class="split-view">
          <div class="pane left-pane">
            <div class="pane-header">
              <h3>Unassigned ({{ unassignedImages.length }})</h3>
              <div class="pane-actions">
                <button class="action-btn" @click="toggleSelectAllUnassigned" :disabled="!unassignedImages.length">
                  {{ allUnassignedSelected ? 'Clear' : 'Select all' }}
                </button>
                <button class="action-btn danger-btn" @click="deleteSelectedUnassigned" :disabled="!selectedUnassigned.length">Delete</button>
                <button class="action-btn" @click="assignSelected" :disabled="!selectedUnassigned.length">Assign -></button>
              </div>
            </div>
            <div class="image-grid">
              <div 
                class="image-card" 
                v-for="img in unassignedImages" 
                :key="img.id"
                :class="{ selected: selectedUnassigned.includes(img.id) }"
                @click="toggleSelection(img.id)"
              >
                <img :src="`${API_BASE_URL}/api/v1/projects/${projectId}/dataset/assets/${img.id}/image`" class="served-image" @error="$event.target.style.display='none'" />
                <div class="image-label">{{ img.filename }}</div>
              </div>
              <div v-if="unassignedImages.length === 0" class="empty-state">
                No unassigned images.
              </div>
            </div>
          </div>
          <div class="pane right-pane">
            <div class="pane-header">
              <h3>Annotating ({{ annotatingImages.length }})</h3>
              <div class="pane-actions">
                <button class="action-btn" @click="returnSelectedToUnassigned" :disabled="!selectedAnnotating.length">Return to Unassigned</button>
                <button class="action-btn" @click="openAnnotationWorkspace">Start Annotating</button>
              </div>
            </div>
            <div class="image-grid">
              <div
                class="image-card"
                v-for="img in annotatingImages"
                :key="img.id"
                :class="{ selected: selectedAnnotating.includes(img.id) }"
                @click="toggleAnnotatingSelection(img.id)"
              >
                <img :src="`${API_BASE_URL}/api/v1/projects/${projectId}/dataset/assets/${img.id}/image`" class="served-image" @error="$event.target.style.display='none'" />
                <div class="image-label">{{ img.filename }}</div>
                <div class="status-badge" v-if="img.status === 'annotated'">Annotated</div>
              </div>
              <div v-if="annotatingImages.length === 0" class="empty-state">
                No images being annotated.
              </div>
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
            {{ version.name }} - {{ version.asset_count }} annotated assets - {{ version.multiplier }}x
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
        <div class="empty-state">
          Real local training is intentionally disabled in this integration. Dataset selection is real; progress below is a lightweight UI simulation.
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
          <div 
            class="drag-zone" 
            :class="{ 'drag-active': isDragging }"
            @dragover="onDragOver"
            @dragleave="onDragLeave"
            @drop="onDrop"
          >
            <p style="margin: 0;">Drag and drop files/folders here<br>or</p>
            <div class="upload-options" style="margin-top: 1rem; display: flex; gap: 1rem; justify-content: center;">
              <button class="action-btn" @click="chooseFiles">[Choose Image/Video Files]</button>
            </div>
            <input ref="fileInput" type="file" multiple accept="image/*,video/*" class="hidden-input" @change="onFileSelected" />
          </div>
          <div style="margin-top: 1.5rem;">
            <label style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
              <span>Extract Frames per second (FPS)</span>
              <strong>{{ fpsSlider }} FPS</strong>
            </label>
            <input type="range" v-model="fpsSlider" min="1" max="60" class="slider" style="width: 100%; display: block; box-sizing: border-box;" />
          </div>
          <div style="margin-top: 2rem; text-align: right;">
            <button class="action-btn" @click="chooseFiles">[Upload & Process]</button>
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

.project-title {
  color: #646262;
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
  justify-content: flex-end;
  align-items: center;
  border-bottom: 1px dashed #646262;
  padding-bottom: 1rem;
}

.split-view {
  display: flex;
  gap: 2rem;
  height: 100%;
}

.pane {
  flex: 1;
  border: 1px solid var(--border-color, #646262);
  padding: 1rem;
  display: flex;
  flex-direction: column;
}

.pane-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  border-bottom: 1px dashed var(--border-color, #646262);
  padding-bottom: 0.5rem;
}

.pane-header h3 {
  margin: 0;
}

.pane-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: flex-end;
}

.danger-btn {
  color: #8a1f11;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 1rem;
}

.image-card {
  aspect-ratio: 1;
  border: 1px solid #646262;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  text-align: center;
  position: relative;
  cursor: pointer;
}

.image-card.selected {
  border-color: #fdfcfc;
  background: rgba(255, 255, 255, 0.1);
}

.served-image {
  max-width: 100%;
  max-height: 80%;
  object-fit: contain;
  margin-bottom: 0.5rem;
}

.image-label {
  font-size: 0.8rem;
  word-break: break-all;
  color: #646262;
}

.status-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: #201d1d;
  color: #fdfcfc;
  font-size: 0.7rem;
  padding: 0.1rem 0.3rem;
  border-bottom-left-radius: 4px;
}

.empty-state {
  color: #646262;
  font-style: italic;
  padding: 2rem 0;
}

.error-state {
  color: #8a1f11;
}

.hidden-input {
  display: none;
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

.drag-zone {
  border: 2px dashed var(--border-color, #646262);
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
  margin-bottom: 1rem;
}

.drag-zone.drag-active {
  background: var(--hover-bg, rgba(15,0,0,0.05));
  border-color: var(--text-color, #201d1d);
}

.slider {
  -webkit-appearance: none;
  background: transparent;
}
.slider::-webkit-slider-runnable-track {
  width: 100%;
  height: 2px;
  background: var(--border-color, #646262);
}
.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  height: 16px;
  width: 8px;
  background: var(--text-color, #201d1d);
  margin-top: -7px;
  cursor: ew-resize;
}

@media (max-width: 720px) {
  .header {
    align-items: flex-start;
    flex-direction: column;
    gap: 0.75rem;
  }

  .content {
    padding: 0.75rem;
  }

  .dataset-subnav {
    justify-content: flex-start;
  }

  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
}
</style>
