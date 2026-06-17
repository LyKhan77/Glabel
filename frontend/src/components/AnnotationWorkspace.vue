<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  project: {
    type: Object,
    required: true
  },
  assets: {
    type: Array,
    required: true
  },
  apiBaseUrl: {
    type: String,
    required: false,
    default: ''
  }
})

const emit = defineEmits(['close'])

const activeTab = ref('unannotated')

const unannotatedAssets = computed(() => props.assets.filter(a => a.status === 'unannotated'))
const annotatedAssets = computed(() => props.assets.filter(a => a.status === 'annotated'))

const currentList = computed(() => activeTab.value === 'unannotated' ? unannotatedAssets.value : annotatedAssets.value)

const selectedImage = ref(null)

const getImageUrl = (img) => `${props.apiBaseUrl}/api/v1/projects/${props.project.id}/dataset/assets/${img.id}/image`

const selectImage = (img) => {
  selectedImage.value = img
}

const mockClassify = (className) => {
  if (selectedImage.value) {
    selectedImage.value.annotations = { class: className }
  }
}

const mockDrawBoundingBox = () => {
  if (selectedImage.value) {
    selectedImage.value.annotations = { bboxes: [[10, 10, 100, 100]] }
  }
}

const mockDrawPolygon = () => {
  if (selectedImage.value) {
    selectedImage.value.annotations = { polygon: true }
  }
}

const mockDrawSkeleton = () => {
  if (selectedImage.value) {
    selectedImage.value.annotations = { skeleton: true }
  }
}

const saveAnnotation = () => {
  if (selectedImage.value) {
    selectedImage.value.status = 'annotated'
    console.log('Saved annotations:', selectedImage.value.annotations)
    activeTab.value = 'annotated'
  }
}
</script>

<template>
  <div class="workspace-layout">
    <div class="sidebar">
      <div class="sidebar-header">
        <button class="nav-btn" @click="$emit('close')">[&lt;] Back</button>
        <h3>Workspace</h3>
      </div>
      <div class="tabs">
        <button 
          :class="['tab-btn', { active: activeTab === 'unannotated' }]"
          @click="activeTab = 'unannotated'"
        >Unannotated</button>
        <button 
          :class="['tab-btn', { active: activeTab === 'annotated' }]"
          @click="activeTab = 'annotated'"
        >Annotated</button>
      </div>
      <div class="image-list">
        <div v-for="img in currentList" :key="img.id" 
             :class="['image-item', { 'selected': selectedImage?.id === img.id }]"
             @click="selectImage(img)">
          {{ img.filename }}
        </div>
        <div v-if="currentList.length === 0" class="empty-state">
          No images here.
        </div>
      </div>
    </div>
    <div class="canvas-area">
      <div v-if="selectedImage" class="editor-container">
        <div class="toolbar">
          <span class="task-badge">{{ project.task_type }}</span>
          
          <template v-if="project.task_type === 'classification'">
            <button class="tool-btn" @click="mockClassify('Cat')">Cat</button>
            <button class="tool-btn" @click="mockClassify('Dog')">Dog</button>
          </template>
          
          <template v-else-if="project.task_type === 'object_detection'">
            <button class="tool-btn" @click="mockDrawBoundingBox()">Mock Draw BBox</button>
          </template>
          
          <template v-else-if="project.task_type === 'segmentation'">
            <button class="tool-btn" @click="mockDrawPolygon()">Mock Draw Polygon</button>
          </template>
          
          <template v-else-if="project.task_type === 'pose_estimation'">
            <button class="tool-btn" @click="mockDrawSkeleton()">Mock Draw Skeleton</button>
          </template>
          
          <div class="spacer"></div>
          <button class="primary-btn" @click="saveAnnotation">Save Annotation</button>
        </div>
        
        <div class="image-container">
          <img :src="getImageUrl(selectedImage)" alt="Asset" class="canvas-image" />
          
          <!-- Mock Overlays -->
          <div v-if="selectedImage.annotations?.bboxes" class="mock-bbox" style="position: absolute; border: 2px solid #00ff00; left: 10px; top: 10px; width: 100px; height: 100px; box-shadow: 0 0 0 1px rgba(0,0,0,0.5);"></div>
          <div v-if="selectedImage.annotations?.polygon" class="mock-overlay" style="position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); color: #00ff00; font-weight: bold; font-size: 24px; text-shadow: 1px 1px 2px black;">[Mock Polygon]</div>
          <div v-if="selectedImage.annotations?.skeleton" class="mock-overlay" style="position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); color: #00ff00; font-weight: bold; font-size: 24px; text-shadow: 1px 1px 2px black;">[Mock Skeleton]</div>
          <div v-if="selectedImage.annotations?.class" class="mock-class" style="position: absolute; left: 10px; top: 10px; background: rgba(0,0,0,0.7); color: white; padding: 4px 8px;">Class: {{ selectedImage.annotations.class }}</div>
        </div>
        
        <div class="debug-panel">
          <pre>Annotations: {{ selectedImage.annotations || '{}' }}</pre>
        </div>
      </div>
      <p v-else class="empty-canvas-message">Select an image from the sidebar to start annotating.</p>
    </div>
  </div>
</template>

<style scoped>
.workspace-layout { 
  display: flex; 
  flex-grow: 1;
  min-height: 500px;
  border: 1px solid var(--border-color, #646262);
}

.sidebar {
  width: 250px;
  border-right: 1px solid var(--border-color, #646262);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 1rem;
  border-bottom: 1px dashed var(--border-color, #646262);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.sidebar-header h3 {
  margin: 0;
  font-weight: normal;
}

.tabs {
  display: flex;
  border-bottom: 1px dashed var(--border-color, #646262);
}

.tab-btn {
  flex: 1;
  padding: 0.5rem;
  background: transparent;
  border: none;
  border-right: 1px dashed var(--border-color, #646262);
  cursor: pointer;
  font-family: inherit;
  font-size: inherit;
  color: inherit;
}

.tab-btn:last-child {
  border-right: none;
}

.tab-btn.active {
  background: var(--text-color, #201d1d);
  color: var(--bg-color, #fdfcfc);
}

.tab-btn:not(.active):hover {
  text-decoration: underline;
}

.image-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.image-item {
  padding: 0.5rem;
  border: 1px solid var(--border-color, #646262);
  cursor: pointer;
  font-size: 0.8rem;
  word-break: break-all;
}

.image-item:hover {
  background: rgba(0,0,0,0.05);
}

.image-item.selected {
  background: var(--text-color, #201d1d);
  color: var(--bg-color, #fdfcfc);
}

.canvas-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--border-color, #646262);
}

.empty-canvas-message {
  font-style: italic;
}

.nav-btn {
  background: transparent;
  border: none;
  font-family: inherit;
  font-size: inherit;
  color: inherit;
  cursor: pointer;
  padding: 0;
}

.nav-btn:hover {
  text-decoration: underline;
}

.empty-state {
  color: #646262;
  font-style: italic;
  padding: 1rem;
  text-align: center;
}

.editor-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  color: var(--text-color, #201d1d);
}

.toolbar {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-bottom: 1px solid var(--border-color, #646262);
  align-items: center;
  background: var(--bg-color, #fdfcfc);
}

.task-badge {
  background: #eee;
  color: #333;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  margin-right: 1rem;
  font-style: normal;
}

.tool-btn {
  padding: 0.3rem 0.6rem;
  cursor: pointer;
  border: 1px solid var(--border-color, #646262);
  background: transparent;
  color: inherit;
  font-family: inherit;
}

.tool-btn:hover {
  background: rgba(0,0,0,0.05);
}

.primary-btn {
  padding: 0.3rem 0.6rem;
  cursor: pointer;
  background: var(--text-color, #201d1d);
  color: var(--bg-color, #fdfcfc);
  border: 1px solid var(--text-color, #201d1d);
  font-family: inherit;
}

.spacer {
  flex-grow: 1;
}

.image-container {
  flex-grow: 1;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #111;
}

.canvas-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.debug-panel {
  padding: 0.5rem;
  border-top: 1px solid var(--border-color, #646262);
  background: #f5f5f5;
  font-family: monospace;
  font-size: 0.8rem;
  color: #333;
  max-height: 100px;
  overflow-y: auto;
  font-style: normal;
  margin: 0;
}
</style>
