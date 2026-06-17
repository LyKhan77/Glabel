<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { updateProject } from '../api/client.js'
import { saveAssetAnnotations } from '../api/client.js'

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

const activeTool = ref('select')
const isDrawing = ref(false)
const draftBBox = ref(null)
const zoomContainerRef = ref(null)

const zoomScale = ref(1)
const pan = ref({ x: 0, y: 0 })
const MIN_ZOOM = 0.1
const MAX_ZOOM = 10

const isPanning = ref(false)
const isSpaceDown = ref(false)
const lastMousePos = ref({ x: 0, y: 0 })

const draftPolygon = ref(null)
const cursorPos = ref({ x: 0, y: 0 })

const draggedNode = ref(null)

const COCO_KEYPOINTS = [
  'nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear',
  'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow',
  'left_wrist', 'right_wrist', 'left_hip', 'right_hip',
  'left_knee', 'right_knee', 'left_ankle', 'right_ankle'
]

const COCO_EDGES = [
  [15, 13], [13, 11], [16, 14], [14, 12], [11, 12], [5, 11], [6, 12], [5, 6],
  [5, 7], [6, 8], [7, 9], [8, 10], [1, 2], [0, 1], [0, 2], [1, 3], [2, 4],
  [3, 5], [4, 6]
]

const handleKeydown = (e) => {
  if (e.code === 'Space') {
    isSpaceDown.value = true
    if (e.target === document.body) {
      e.preventDefault()
    }
  }
}

const handleKeyup = (e) => {
  if (e.code === 'Space') {
    isSpaceDown.value = false
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  window.addEventListener('keyup', handleKeyup)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('keyup', handleKeyup)
})

const handleWheel = (e) => {
  e.preventDefault()
  const zoomSensitivity = 0.001
  const delta = e.deltaY * -zoomSensitivity
  const newScale = Math.min(Math.max(zoomScale.value * (1 + delta), MIN_ZOOM), MAX_ZOOM)
  
  const scaleRatio = newScale / zoomScale.value
  
  const containerRect = e.currentTarget.getBoundingClientRect()
  const mouseX = e.clientX - containerRect.left
  const mouseY = e.clientY - containerRect.top
  
  pan.value.x = mouseX - (mouseX - pan.value.x) * scaleRatio
  pan.value.y = mouseY - (mouseY - pan.value.y) * scaleRatio
  
  zoomScale.value = newScale
}

const handleMouseDown = (e) => {
  if (e.button === 1 || (e.button === 0 && isSpaceDown.value) || (e.button === 0 && activeTool.value === 'select')) {
    e.preventDefault()
    isPanning.value = true
    lastMousePos.value = { x: e.clientX, y: e.clientY }
  } else if (e.button === 0 && activeTool.value === 'draw_bbox' && zoomContainerRef.value) {
    if (!activeClass.value) {
      alert("Please select a class first.")
      return
    }
    const rect = zoomContainerRef.value.getBoundingClientRect()
    const svgX = (e.clientX - rect.left) / zoomScale.value
    const svgY = (e.clientY - rect.top) / zoomScale.value
    
    isDrawing.value = true
    draftBBox.value = {
      startX: svgX,
      startY: svgY,
      x: svgX,
      y: svgY,
      width: 0,
      height: 0,
      classId: activeClass.value.id,
      color: activeClass.value.color || '#00ff00'
    }
  } else if (e.button === 0 && activeTool.value === 'draw_polygon' && zoomContainerRef.value) {
    if (!activeClass.value) {
      alert("Please select a class first.")
      return
    }
    const rect = zoomContainerRef.value.getBoundingClientRect()
    const svgX = (e.clientX - rect.left) / zoomScale.value
    const svgY = (e.clientY - rect.top) / zoomScale.value

    if (!draftPolygon.value) {
      draftPolygon.value = {
        classId: activeClass.value.id,
        color: activeClass.value.color || '#00ff00',
        points: []
      }
    }
    draftPolygon.value.points.push({ x: svgX, y: svgY })
    cursorPos.value = { x: svgX, y: svgY }
  }
}

const startDragNode = (e, skelIdx, nodeIdx) => {
  if (e.button !== 0 || activeTool.value !== 'select') return
  draggedNode.value = { skelIdx, nodeIdx }
  e.preventDefault()
}

const handleMouseMove = (e) => {
  if (isPanning.value) {
    const dx = e.clientX - lastMousePos.value.x
    const dy = e.clientY - lastMousePos.value.y
    pan.value.x += dx
    pan.value.y += dy
    lastMousePos.value = { x: e.clientX, y: e.clientY }
  } else if (draggedNode.value && zoomContainerRef.value && selectedImage.value?.annotations?.skeletons) {
    const rect = zoomContainerRef.value.getBoundingClientRect()
    const currentX = (e.clientX - rect.left) / zoomScale.value
    const currentY = (e.clientY - rect.top) / zoomScale.value
    
    const { skelIdx, nodeIdx } = draggedNode.value
    const skeleton = selectedImage.value.annotations.skeletons[skelIdx]
    skeleton.keypoints[nodeIdx].x = currentX
    skeleton.keypoints[nodeIdx].y = currentY
  } else if (isDrawing.value && zoomContainerRef.value && activeTool.value === 'draw_bbox') {
    const rect = zoomContainerRef.value.getBoundingClientRect()
    const currentX = (e.clientX - rect.left) / zoomScale.value
    const currentY = (e.clientY - rect.top) / zoomScale.value
    
    draftBBox.value.x = Math.min(draftBBox.value.startX, currentX)
    draftBBox.value.y = Math.min(draftBBox.value.startY, currentY)
    draftBBox.value.width = Math.abs(currentX - draftBBox.value.startX)
    draftBBox.value.height = Math.abs(currentY - draftBBox.value.startY)
  } else if (draftPolygon.value && activeTool.value === 'draw_polygon' && zoomContainerRef.value) {
    const rect = zoomContainerRef.value.getBoundingClientRect()
    cursorPos.value.x = (e.clientX - rect.left) / zoomScale.value
    cursorPos.value.y = (e.clientY - rect.top) / zoomScale.value
  }
}

const handleMouseUp = () => {
  isPanning.value = false
  if (draggedNode.value) {
    draggedNode.value = null
  }
  if (isDrawing.value && activeTool.value === 'draw_bbox') {
    if (draftBBox.value && draftBBox.value.width > 5 && draftBBox.value.height > 5) {
      if (!selectedImage.value.annotations) {
        selectedImage.value.annotations = {}
      }
      if (!selectedImage.value.annotations.bboxes) {
        selectedImage.value.annotations.bboxes = []
      }
      
      const { startX, startY, ...finalBBox } = draftBBox.value
      selectedImage.value.annotations.bboxes.push(finalBBox)
    }
    isDrawing.value = false
    draftBBox.value = null
  }
}

const handleDblClick = (e) => {
  if (activeTool.value === 'draw_polygon' && draftPolygon.value) {
    if (draftPolygon.value.points.length >= 3) {
      if (!selectedImage.value.annotations) {
        selectedImage.value.annotations = {}
      }
      if (!selectedImage.value.annotations.polygons) {
        selectedImage.value.annotations.polygons = []
      }
      selectedImage.value.annotations.polygons.push(draftPolygon.value)
    }
    draftPolygon.value = null
  }
}

const resetView = () => {
  zoomScale.value = 1
  pan.value = { x: 0, y: 0 }
}

const newClassName = ref('')
const projectClasses = ref([...(props.project.classes || [])])
const activeClass = ref(null)

const generateRandomColor = () => {
  return '#' + Math.floor(Math.random()*16777215).toString(16).padStart(6, '0')
}

const addClass = async () => {
  const name = newClassName.value.trim()
  if (!name) return
  
  if (projectClasses.value.some(c => c.name.toLowerCase() === name.toLowerCase())) {
    return
  }

  const newClass = {
    id: crypto.randomUUID(),
    name: name,
    color: generateRandomColor()
  }
  
  const backup = [...projectClasses.value]
  projectClasses.value.push(newClass)
  newClassName.value = ''
  
  try {
    await updateProject(props.project.id, { classes: projectClasses.value })
  } catch (error) {
    console.error("Failed to update project classes:", error)
    projectClasses.value = backup
  }
}

const removeClass = async (classId) => {
  const backup = [...projectClasses.value]
  projectClasses.value = projectClasses.value.filter(c => c.id !== classId)
  if (activeClass.value?.id === classId) {
    activeClass.value = null
  }
  try {
    await updateProject(props.project.id, { classes: projectClasses.value })
  } catch (error) {
    console.error("Failed to update project classes:", error)
    projectClasses.value = backup
  }
}

const getImageUrl = (img) => `${props.apiBaseUrl}/api/v1/projects/${props.project.id}/dataset/assets/${img.id}/image`

const selectImage = (img) => {
  selectedImage.value = img
}

const mockClassify = (className) => {
  if (selectedImage.value) {
    selectedImage.value.annotations = { class: className }
  }
}

const spawnSkeleton = () => {
  if (!activeClass.value) {
    alert("Please select a class first.")
    return
  }
  if (!selectedImage.value) return
  
  if (!selectedImage.value.annotations) selectedImage.value.annotations = {}
  if (!selectedImage.value.annotations.skeletons) selectedImage.value.annotations.skeletons = []

  let centerX = 100
  let centerY = 100
  
  if (zoomContainerRef.value) {
    const parentRect = zoomContainerRef.value.parentElement.getBoundingClientRect()
    const viewCenterX = parentRect.width / 2
    const viewCenterY = parentRect.height / 2
    centerX = (viewCenterX - pan.value.x) / zoomScale.value
    centerY = (viewCenterY - pan.value.y) / zoomScale.value
  }

  const spread = 50 / zoomScale.value
  
  const keypoints = COCO_KEYPOINTS.map((name) => {
    let offsetX = (Math.random() - 0.5) * spread
    let offsetY = (Math.random() - 0.5) * spread
    
    if (name.includes('left')) offsetX -= spread
    if (name.includes('right')) offsetX += spread
    if (name.includes('knee') || name.includes('ankle')) offsetY += spread * 2
    if (name.includes('eye') || name.includes('ear') || name.includes('nose')) offsetY -= spread * 2
    
    return {
      x: centerX + offsetX,
      y: centerY + offsetY,
      name,
      visible: true
    }
  })

  selectedImage.value.annotations.skeletons.push({
    classId: activeClass.value.id,
    color: activeClass.value.color || '#00ff00',
    keypoints
  })
}

const saveAnnotation = async () => {
  if (selectedImage.value) {
    try {
      const updatedAsset = await saveAssetAnnotations(
        props.project.id, 
        selectedImage.value.id, 
        selectedImage.value.annotations || {}, 
        'annotated'
      )
      selectedImage.value.status = 'annotated'
      console.log('Saved annotations:', updatedAsset.annotations)
      activeTab.value = 'annotated'
    } catch (e) {
      console.error('Failed to save annotations:', e)
      alert('Failed to save annotations')
    }
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
          <button class="tool-btn" @click="resetView">Reset View</button>
          <span class="task-badge">{{ project.task_type }}</span>
          
          <template v-if="project.task_type === 'classification'">
            <button class="tool-btn" @click="mockClassify('Cat')">Cat</button>
            <button class="tool-btn" @click="mockClassify('Dog')">Dog</button>
          </template>
          
          <template v-else-if="project.task_type === 'object_detection'">
            <button class="tool-btn" :class="{ active: activeTool === 'select' }" @click="activeTool = 'select'">Select</button>
            <button class="tool-btn" :class="{ active: activeTool === 'draw_bbox' }" @click="activeTool = 'draw_bbox'">Draw BBox</button>
          </template>
          
          <template v-else-if="project.task_type === 'segmentation'">
            <button class="tool-btn" :class="{ active: activeTool === 'select' }" @click="activeTool = 'select'">Select</button>
            <button class="tool-btn" :class="{ active: activeTool === 'draw_polygon' }" @click="activeTool = 'draw_polygon'">Draw Polygon</button>
          </template>
          
          <template v-else-if="project.task_type === 'pose_estimation'">
            <button class="tool-btn" :class="{ active: activeTool === 'select' }" @click="activeTool = 'select'">Select</button>
            <button class="tool-btn" @click="spawnSkeleton">Spawn Skeleton</button>
          </template>
          
          <div class="spacer"></div>
          <button class="primary-btn" @click="saveAnnotation">Save Annotation</button>
        </div>
        
        <div 
          class="image-container"
          @wheel="handleWheel"
          @mousedown="handleMouseDown"
          @mousemove="handleMouseMove"
          @mouseup="handleMouseUp"
          @mouseleave="handleMouseUp"
          @dblclick="handleDblClick"
          @contextmenu.prevent
        >
          <div 
            class="zoom-container"
            ref="zoomContainerRef"
            :style="{
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoomScale})`,
              transformOrigin: '0 0'
            }"
          >
            <img :src="getImageUrl(selectedImage)" alt="Asset" class="canvas-image" draggable="false" />
            <svg class="annotation-svg" xmlns="http://www.w3.org/2000/svg">
              <template v-if="selectedImage.annotations?.bboxes">
                <g v-for="(bbox, idx) in selectedImage.annotations.bboxes" :key="idx">
                  <rect 
                    :x="bbox.x" :y="bbox.y" :width="bbox.width" :height="bbox.height" 
                    fill="transparent" :stroke="bbox.color" stroke-width="2" 
                  />
                  <text 
                    :x="bbox.x" :y="bbox.y - 4" :fill="bbox.color" font-size="12" font-family="sans-serif">
                    {{ projectClasses.find(c => c.id === bbox.classId)?.name || 'Unknown' }}
                  </text>
                </g>
              </template>
              <template v-if="draftBBox">
                <rect 
                  :x="draftBBox.x" :y="draftBBox.y" :width="draftBBox.width" :height="draftBBox.height" 
                  fill="rgba(255, 255, 255, 0.2)" :stroke="draftBBox.color" stroke-width="2" stroke-dasharray="4"
                />
              </template>
              <template v-if="selectedImage.annotations?.polygons">
                <g v-for="(poly, idx) in selectedImage.annotations.polygons" :key="'poly-'+idx">
                  <polygon 
                    :points="poly.points.map(p => `${p.x},${p.y}`).join(' ')"
                    fill="rgba(255, 255, 255, 0.2)" :stroke="poly.color" stroke-width="2"
                  />
                  <text 
                    v-if="poly.points.length > 0"
                    :x="poly.points[0].x" :y="poly.points[0].y - 4" :fill="poly.color" font-size="12" font-family="sans-serif">
                    {{ projectClasses.find(c => c.id === poly.classId)?.name || 'Unknown' }}
                  </text>
                </g>
              </template>
              <template v-if="draftPolygon">
                <polyline 
                  :points="draftPolygon.points.map(p => `${p.x},${p.y}`).join(' ')"
                  fill="none" :stroke="draftPolygon.color" stroke-width="2" stroke-dasharray="4"
                />
                <line 
                  v-if="draftPolygon.points.length > 0"
                  :x1="draftPolygon.points[draftPolygon.points.length - 1].x" 
                  :y1="draftPolygon.points[draftPolygon.points.length - 1].y"
                  :x2="cursorPos.x" 
                  :y2="cursorPos.y"
                  :stroke="draftPolygon.color" stroke-width="2" stroke-dasharray="4"
                />
                <circle 
                  v-for="(p, i) in draftPolygon.points" :key="'dp-'+i"
                  :cx="p.x" :cy="p.y" r="3" :fill="draftPolygon.color"
                />
              </template>
              <template v-if="selectedImage.annotations?.skeletons">
                <g v-for="(skel, sIdx) in selectedImage.annotations.skeletons" :key="'skel-'+sIdx">
                  <line
                    v-for="(edge, eIdx) in COCO_EDGES" :key="'edge-'+eIdx"
                    :x1="skel.keypoints[edge[0]].x" :y1="skel.keypoints[edge[0]].y"
                    :x2="skel.keypoints[edge[1]].x" :y2="skel.keypoints[edge[1]].y"
                    :stroke="skel.color" stroke-width="2"
                  />
                  <circle
                    v-for="(kp, nIdx) in skel.keypoints" :key="'kp-'+nIdx"
                    :cx="kp.x" :cy="kp.y" r="4" :fill="skel.color"
                    class="skeleton-node"
                    @mousedown.stop="startDragNode($event, sIdx, nIdx)"
                  />
                  <text 
                    v-if="skel.keypoints.length > 0"
                    :x="skel.keypoints[0].x" :y="skel.keypoints[0].y - 10" :fill="skel.color" font-size="12" font-family="sans-serif">
                    {{ projectClasses.find(c => c.id === skel.classId)?.name || 'Unknown' }}
                  </text>
                </g>
              </template>
            </svg>
            
            <!-- Mock Overlays -->
            <div v-if="selectedImage.annotations?.class" class="mock-class" style="position: absolute; left: 10px; top: 10px; background: rgba(0,0,0,0.7); color: white; padding: 4px 8px;">Class: {{ selectedImage.annotations.class }}</div>
          </div>
        </div>
        
        <div class="debug-panel">
          <pre>Annotations: {{ selectedImage.annotations || '{}' }}</pre>
        </div>
      </div>
      <p v-else class="empty-canvas-message">Select an image from the sidebar to start annotating.</p>
    </div>
    <div class="right-sidebar">
      <div class="sidebar-header">
        <h3>Classes</h3>
      </div>
      <div class="classes-panel">
        <div class="add-class-form">
          <input v-model="newClassName" type="text" placeholder="New class name..." @keyup.enter="addClass" />
          <button class="primary-btn" @click="addClass">Add</button>
        </div>
        <div class="class-list">
          <div v-for="c in projectClasses" :key="c.id"
               :class="['class-item', { active: activeClass?.id === c.id }]"
               @click="activeClass = c">
            <span class="color-dot" :style="{ backgroundColor: c.color }"></span>
            <span class="class-name">{{ c.name }}</span>
            <button class="del-btn" @click.stop="removeClass(c.id)">Del</button>
          </div>
          <div v-if="projectClasses.length === 0" class="empty-state">
            No classes defined.
          </div>
        </div>
      </div>
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

.right-sidebar {
  width: 250px;
  border-left: 1px solid var(--border-color, #646262);
  display: flex;
  flex-direction: column;
  background: var(--bg-color, #fdfcfc);
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

.tool-btn.active {
  background: var(--text-color, #201d1d);
  color: var(--bg-color, #fdfcfc);
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
  overflow: hidden;
  background: #111;
  cursor: grab;
}

.image-container:active {
  cursor: grabbing;
}

.zoom-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

.canvas-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  pointer-events: none;
  display: block;
}

.annotation-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.skeleton-node {
  pointer-events: auto;
  cursor: pointer;
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

.classes-panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 0.5rem;
  gap: 1rem;
}

.add-class-form {
  display: flex;
  gap: 0.5rem;
}

.add-class-form input {
  flex: 1;
  padding: 0.3rem;
  border: 1px solid var(--border-color, #646262);
  font-family: inherit;
  font-size: 0.9rem;
}

.class-list {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.class-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem;
  border: 1px solid var(--border-color, #646262);
  cursor: pointer;
}

.class-item:hover {
  background: rgba(0,0,0,0.05);
}

.class-item.active {
  background: var(--text-color, #201d1d);
  color: var(--bg-color, #fdfcfc);
}

.color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid #fff;
  box-shadow: 0 0 0 1px #000;
}

.class-name {
  flex: 1;
  font-size: 0.9rem;
}

.del-btn {
  background: #ff4444;
  color: white;
  border: none;
  border-radius: 3px;
  padding: 2px 6px;
  font-size: 0.7rem;
  cursor: pointer;
}

.del-btn:hover {
  background: #cc0000;
}
</style>
