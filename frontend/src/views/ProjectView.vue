<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
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
  uploadDatasetFiles,
  deleteDatasetVersion,
  exportDatasetVersion
} from '../api/client'
import AnnotationWorkspace from '../components/AnnotationWorkspace.vue'
import VersionWizard from '../components/versions/VersionWizard.vue'
import VersionCard from '../components/versions/VersionCard.vue'
import VersionDetail from '../components/versions/VersionDetail.vue'
import SplitBar from '../components/versions/SplitBar.vue'
import { paginateItems } from '../utils/pagination.js'

const DATASET_PAGE_SIZE = 50

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
const unassignedPage = ref(1)
const annotatingPage = ref(1)

const onDragOver = (e) => { e.preventDefault(); isDragging.value = true }
const onDragLeave = (e) => { e.preventDefault(); isDragging.value = false }
const onDrop = (e) => {
  e.preventDefault(); 
  isDragging.value = false;
  uploadFiles(Array.from(e.dataTransfer.files))
}

const unassignedImages = computed(() => assets.value.filter(asset => asset.status === 'unassigned' && asset.kind !== 'video'))
const annotatingImages = computed(() => assets.value.filter(asset => (asset.status === 'unannotated' || asset.status === 'annotated') && asset.kind !== 'video'))
const unassignedPagination = computed(() => paginateItems(unassignedImages.value, unassignedPage.value, DATASET_PAGE_SIZE))
const annotatingPagination = computed(() => paginateItems(annotatingImages.value, annotatingPage.value, DATASET_PAGE_SIZE))
const paginatedUnassignedImages = computed(() => unassignedPagination.value.items)
const paginatedAnnotatingImages = computed(() => annotatingPagination.value.items)
const unassignedPageIds = computed(() => paginatedUnassignedImages.value.map(asset => asset.id))
const allUnassignedSelected = computed(() => unassignedPageIds.value.length > 0 && unassignedPageIds.value.every(id => selectedUnassigned.value.includes(id)))

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
    unassignedPage.value = 1
    annotatingPage.value = 1
  } catch (error) {
    errorMessage.value = 'Failed to assign selected assets.'
  }
}

const toggleSelectAllUnassigned = () => {
  if (allUnassignedSelected.value) {
    selectedUnassigned.value = selectedUnassigned.value.filter(id => !unassignedPageIds.value.includes(id))
  } else {
    selectedUnassigned.value = Array.from(new Set([...selectedUnassigned.value, ...unassignedPageIds.value]))
  }
}

const deleteSelectedUnassigned = async () => {
  if (!selectedUnassigned.value.length) return
  if (!window.confirm(`Delete ${selectedUnassigned.value.length} unassigned asset(s)?`)) return
  errorMessage.value = ''
  try {
    await deleteDatasetAssets(projectId.value, selectedUnassigned.value)
    assets.value = await listDatasetAssets(projectId.value)
    selectedUnassigned.value = []
    unassignedPage.value = 1
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
    unassignedPage.value = 1
    annotatingPage.value = 1
  } catch (error) {
    errorMessage.value = 'Failed to return selected assets.'
  }
}

const openAnnotationWorkspace = () => {
  isAnnotating.value = true
}

const refreshDatasetAssets = async () => {
  assets.value = await listDatasetAssets(projectId.value)
  unassignedPage.value = 1
  annotatingPage.value = 1
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
    unassignedPage.value = 1
    annotatingPage.value = 1
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
    unassignedPage.value = 1
    annotatingPage.value = 1
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
    unassignedPage.value = 1
    annotatingPage.value = 1
  } catch (error) {
    errorMessage.value = 'Upload failed. Check file type and backend status.'
  }
  showUploadModal.value = false
}

// Versions state
const versions = ref([])
const showWizard = ref(false)
const selectedVersion = ref(null)

const handleGenerateVersion = async (config) => {
  errorMessage.value = ''
  try {
    await createDatasetVersion(projectId.value, config)
    versions.value = await listDatasetVersions(projectId.value)
    showWizard.value = false
  } catch (error) {
    errorMessage.value = 'Could not create dataset version.'
  }
}

const handleDeleteVersion = async (version) => {
  if (!window.confirm(`Delete version "${version.name}"?`)) return
  errorMessage.value = ''
  try {
    await deleteDatasetVersion(projectId.value, version.id)
    versions.value = await listDatasetVersions(projectId.value)
    if (selectedVersion.value?.id === version.id) {
      selectedVersion.value = null
    }
  } catch (error) {
    errorMessage.value = 'Could not delete version.'
  }
}

const handleExportVersion = async ({ version, format }) => {
  const fmt = format || 'yolo'
  errorMessage.value = ''
  try {
    const blob = await exportDatasetVersion(projectId.value, version.id, fmt)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `dataset_${version.name}_${fmt}.zip`
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    errorMessage.value = 'Could not export version.'
  }
}

const handleDuplicateVersion = (version) => {
  showWizard.value = true
}

// Train state
const selectedTrainVersionId = ref(null)
const trainingProgress = ref(0)
const isTraining = ref(false)

const startTraining = () => {
  if (!selectedTrainVersionId.value) return
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

function handleEsc(event) {
  if (event.key === 'Escape' && showUploadModal.value) showUploadModal.value = false
}

onMounted(() => {
  window.addEventListener('keydown', handleEsc)
  loadProject()
})
onBeforeUnmount(() => window.removeEventListener('keydown', handleEsc))
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
                  {{ allUnassignedSelected ? 'Clear page' : 'Select page' }}
                </button>
                <button class="action-btn danger-btn" @click="deleteSelectedUnassigned" :disabled="!selectedUnassigned.length">Delete</button>
                <button class="action-btn" @click="assignSelected" :disabled="!selectedUnassigned.length">Assign -></button>
              </div>
            </div>
            <div class="image-grid">
              <div
                class="image-card"
                v-for="img in paginatedUnassignedImages"
                :key="img.id"
                :class="{ selected: selectedUnassigned.includes(img.id) }"
                role="button"
                tabindex="0"
                :aria-pressed="selectedUnassigned.includes(img.id)"
                @click="toggleSelection(img.id)"
                @keyup.enter="toggleSelection(img.id)"
              >
                <img :src="`${API_BASE_URL}/api/v1/projects/${projectId}/dataset/assets/${img.id}/image`" class="served-image" @error="$event.target.style.display='none'" />
                <div class="image-label" :title="img.filename">{{ img.filename }}</div>
                <div v-if="selectedUnassigned.includes(img.id)" class="select-tick" aria-hidden="true">✓</div>
              </div>
              <div v-if="unassignedImages.length === 0" class="empty-state">
                No unassigned images.
              </div>
            </div>
            <div v-if="unassignedImages.length > DATASET_PAGE_SIZE" class="pagination-bar">
              <span>Showing {{ unassignedPagination.start }}-{{ unassignedPagination.end }} of {{ unassignedPagination.total }}</span>
              <div class="pagination-actions">
                <button class="action-btn" @click="unassignedPage = unassignedPagination.page - 1" :disabled="unassignedPagination.page === 1">Prev</button>
                <span>Page {{ unassignedPagination.page }} / {{ unassignedPagination.pageCount }}</span>
                <button class="action-btn" @click="unassignedPage = unassignedPagination.page + 1" :disabled="unassignedPagination.page === unassignedPagination.pageCount">Next</button>
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
                v-for="img in paginatedAnnotatingImages"
                :key="img.id"
                :class="{ selected: selectedAnnotating.includes(img.id) }"
                role="button"
                tabindex="0"
                :aria-pressed="selectedAnnotating.includes(img.id)"
                @click="toggleAnnotatingSelection(img.id)"
                @keyup.enter="toggleAnnotatingSelection(img.id)"
              >
                <img :src="`${API_BASE_URL}/api/v1/projects/${projectId}/dataset/assets/${img.id}/image`" class="served-image" @error="$event.target.style.display='none'" />
                <div class="image-label" :title="img.filename">{{ img.filename }}</div>
                <div class="status-badge" v-if="img.status === 'annotated'">Annotated</div>
                <div v-if="selectedAnnotating.includes(img.id)" class="select-tick" aria-hidden="true">✓</div>
              </div>
              <div v-if="annotatingImages.length === 0" class="empty-state">
                No images being annotated.
              </div>
            </div>
            <div v-if="annotatingImages.length > DATASET_PAGE_SIZE" class="pagination-bar">
              <span>Showing {{ annotatingPagination.start }}-{{ annotatingPagination.end }} of {{ annotatingPagination.total }}</span>
              <div class="pagination-actions">
                <button class="action-btn" @click="annotatingPage = annotatingPagination.page - 1" :disabled="annotatingPagination.page === 1">Prev</button>
                <span>Page {{ annotatingPagination.page }} / {{ annotatingPagination.pageCount }}</span>
                <button class="action-btn" @click="annotatingPage = annotatingPagination.page + 1" :disabled="annotatingPagination.page === annotatingPagination.pageCount">Next</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="activeTab === 'versions'" class="versions-view">
        <div class="versions-header">
          <h3>Versions</h3>
        </div>
        
        <div v-if="showWizard">
          <VersionWizard 
            @generate="handleGenerateVersion" 
            @cancel="showWizard = false" 
            :projectId="projectId" 
            :annotatedCount="annotatingImages.filter(i => i.status === 'annotated').length"
            :existingVersionCount="versions.length"
          />
        </div>
        <div v-else>
          <div style="margin-bottom: 1.5rem;">
            <button class="action-btn" @click="showWizard = true">[Generate New Version]</button>
          </div>
          <div class="version-cards-grid" v-if="versions.length > 0">
            <VersionCard
              v-for="version in versions"
              :key="version.id"
              :version="version"
              @click="selectedVersion = version"
              @delete="handleDeleteVersion"
              @export="handleExportVersion"
              @duplicate="handleDuplicateVersion"
            />
          </div>
          <div v-else class="empty-state">
            No versions generated yet.
          </div>
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
            <select v-model="selectedTrainVersionId" class="select-input">
              <option v-for="version in versions" :key="version.id" :value="version.id">
                {{ version.name }}
              </option>
            </select>
          </label>
          <button class="action-btn" @click="startTraining" :disabled="!selectedTrainVersionId || isTraining">[Start Training]</button>
        </div>
        
        <div v-if="trainingProgress > 0" class="progress-container">
          <p>Training Progress: {{ trainingProgress }}%</p>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ transform: `scaleX(${trainingProgress / 100})` }"></div>
          </div>
        </div>
        
        <div v-if="trainingProgress === 100 && !isTraining" class="test-container">
          <button class="action-btn" @click="testInPlayground">[Test in Playground]</button>
        </div>
      </div>
    </main>

    <!-- Upload Media Modal -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
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

    <VersionDetail
      :visible="!!selectedVersion"
      :version="selectedVersion"
      :projectId="projectId"
      @close="selectedVersion = null"
      @delete="handleDeleteVersion"
      @export="handleExportVersion"
    />
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

.nav-btn, .tab-btn, .subtab-btn, .action-btn {
  min-height: 34px;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
}

.nav-btn:hover, .tab-btn:hover, .action-btn:hover {
  background: var(--hover-bg);
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
  border-color: var(--text-color);
  background: var(--hover-bg);
  box-shadow: inset 0 0 0 2px var(--text-color);
}

.select-tick {
  position: absolute;
  top: 0.3rem;
  left: 0.3rem;
  width: 1.15rem;
  height: 1.15rem;
  display: grid;
  place-items: center;
  background: var(--text-color);
  color: var(--bg-color);
  font-size: 0.75rem;
  border-radius: 4px;
}

.image-card:focus-visible {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
}

.served-image {
  max-width: 100%;
  max-height: 80%;
  object-fit: contain;
  margin-bottom: 0.5rem;
}

.image-label {
  font-size: 0.8rem;
  display: -webkit-box;
  max-width: 100%;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  color: #646262;
}

.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px dashed var(--border-color, #646262);
  color: #646262;
  font-size: 0.82rem;
}

.pagination-actions {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
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

.wizard-step label {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.split-inputs {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.split-inputs label {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.split-inputs .number-input {
  width: 4rem;
}

.split-total {
  color: var(--mute);
  font-weight: 700;
}

.split-total.invalid {
  color: var(--danger);
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
  width: 100%;
  height: 100%;
  background: var(--text-color, #201d1d);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s;
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
  z-index: var(--z-modal);
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

  .split-view,
  .pagination-bar {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
