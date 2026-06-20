<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import {
  BoxSelect,
  BrainCircuit,
  Check,
  ChevronLeft,
  ChevronRight,
  CircleDot,
  Crosshair,
  Hand,
  HelpCircle,
  Maximize2,
  MousePointer2,
  Pentagon,
  Redo2,
  RotateCcw,
  Trash2,
  Undo2,
  Waypoints,
  ZoomIn,
  ZoomOut
} from 'lucide-vue-next'
import { deleteDatasetAssets, saveAssetAnnotations, updateProject } from '../api/client.js'
import {
  COCO_EDGES,
  COCO_KEYPOINTS,
  TASK_LABELS,
  clamp,
  clampBox,
  createEmptyAnnotations,
  createPoseSkeleton,
  getContainedImageRect,
  getTaskTools,
  isAnnotationComplete,
  normalizeAnnotations,
  pointerToImagePoint,
  pointOnSegment
} from '../utils/annotationGeometry.js'

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

const emit = defineEmits(['close', 'saved', 'deleted'])

const activeQueue = ref('unannotated')
const selectedImage = ref(null)
const selectedAnnotation = ref(null)
const activeTool = ref('select')
const projectClasses = ref([...(props.project.classes || [])])
const activeClass = ref(projectClasses.value[0] || null)
const newClassName = ref('')
const errorMessage = ref('')
const saveState = ref('')

const viewportRef = ref(null)
const imageMetrics = ref({ naturalWidth: 0, naturalHeight: 0 })
const viewportSize = ref({ width: 0, height: 0 })
const zoom = ref(1)
const pan = ref({ x: 0, y: 0 })
const isSpaceDown = ref(false)
const interaction = ref(null)
const draftBox = ref(null)
const draftPolygon = ref(null)
const cursorPoint = ref(null)
const selectedVertex = ref(null)
const insertHint = ref(null)
const labeledKeypoint = ref(null)
const history = ref([])
const redoStack = ref([])
const showShortcuts = ref(false)
const queueQuery = ref('')
let resizeObserver = null
let autosaveTimer = null

const MIN_ZOOM = 0.25
const MAX_ZOOM = 8
const MIN_POLYGON_POINTS = 3
const CLOSE_TOLERANCE_PX = 8
const INSERT_TOLERANCE_PX = 6

const taskType = computed(() => props.project.task_type || 'object_detection')
const taskLabel = computed(() => TASK_LABELS[taskType.value] || taskType.value)
const taskTools = computed(() => getTaskTools(taskType.value))
const unannotatedAssets = computed(() => props.assets.filter((asset) => asset.status !== 'annotated'))
const annotatedAssets = computed(() => props.assets.filter((asset) => asset.status === 'annotated'))
const currentAssets = computed(() => activeQueue.value === 'annotated' ? annotatedAssets.value : unannotatedAssets.value)
const filteredAssets = computed(() => {
  const query = queueQuery.value.trim().toLowerCase()
  if (!query) return currentAssets.value
  return currentAssets.value.filter((asset) => asset.filename.toLowerCase().includes(query))
})
const selectedIndex = computed(() => currentAssets.value.findIndex((asset) => asset.id === selectedImage.value?.id))
const selectedQueuePosition = computed(() => selectedIndex.value === -1 ? 0 : selectedIndex.value + 1)
const selectedAnnotations = computed(() => normalizeAnnotations(taskType.value, selectedImage.value?.annotations))
const canUndo = computed(() => history.value.length > 0)
const canRedo = computed(() => redoStack.value.length > 0)
const imageRect = computed(() => getContainedImageRect({
  viewportWidth: viewportSize.value.width,
  viewportHeight: viewportSize.value.height,
  naturalWidth: imageMetrics.value.naturalWidth,
  naturalHeight: imageMetrics.value.naturalHeight
}))
const stageStyle = computed(() => ({
  transform: `translate(${pan.value.x}px, ${pan.value.y}px) scale(${zoom.value})`,
  transformOrigin: '0 0'
}))
const imgStyle = computed(() => ({
  left: `${imageRect.value.x}px`,
  top: `${imageRect.value.y}px`,
  width: `${imageRect.value.width}px`,
  height: `${imageRect.value.height}px`
}))
const canvasCursor = computed(() => {
  if (isSpaceDown.value || interaction.value?.type === 'pan') return 'grabbing'
  if (activeTool.value === 'bbox' || activeTool.value === 'polygon') return 'crosshair'
  return 'default'
})
const selectedDetail = computed(() => {
  if (!selectedAnnotation.value) return null
  return findAnnotation(selectedAnnotation.value)
})
const hintText = computed(() => {
  if (activeTool.value === 'bbox') return 'Drag to draw box'
  if (activeTool.value === 'polygon') return 'Click points, then click the first point to close'
  if (activeTool.value === 'select' && taskType.value === 'segmentation' && (selectedAnnotations.value.polygons || []).length) {
    return 'Click an edge to add a point · select a point + Delete to remove'
  }
  if (activeTool.value === 'select' && taskType.value === 'pose_estimation' && (selectedAnnotations.value.skeletons || []).length) {
    return 'Drag joints · drag box/bone moves whole · hover for name · dbl-click toggles visibility'
  }
  return ''
})

watch(() => props.assets, () => {
  if (!selectedImage.value || !props.assets.some((asset) => asset.id === selectedImage.value.id)) {
    selectAsset(currentAssets.value[0] || props.assets[0] || null)
  }
}, { immediate: true })

watch(taskType, () => {
  activeTool.value = 'select'
  activeClass.value = projectClasses.value[0] || null
})

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  window.addEventListener('keyup', handleKeyup)
  resizeObserver = new ResizeObserver(updateViewportSize)
  if (viewportRef.value) resizeObserver.observe(viewportRef.value)
  updateViewportSize()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('keyup', handleKeyup)
  resizeObserver?.disconnect()
  clearTimeout(autosaveTimer)
})

function selectAsset(asset) {
  selectedImage.value = asset
  selectedAnnotation.value = null
  draftBox.value = null
  draftPolygon.value = null
  cursorPoint.value = null
  selectedVertex.value = null
  insertHint.value = null
  labeledKeypoint.value = null
  history.value = []
  redoStack.value = []
  saveState.value = ''
  errorMessage.value = ''
  if (asset) {
    asset.annotations = normalizeAnnotations(taskType.value, asset.annotations)
  }
  nextTick(fitView)
}

function selectRelativeAsset(offset) {
  if (!currentAssets.value.length) return
  const current = selectedIndex.value === -1 ? 0 : selectedIndex.value
  const nextIndex = clamp(current + offset, 0, currentAssets.value.length - 1)
  selectAsset(currentAssets.value[nextIndex])
}

function getImageUrl(asset) {
  return `${props.apiBaseUrl}/api/v1/projects/${props.project.id}/dataset/assets/${asset.id}/image`
}

function updateViewportSize() {
  if (!viewportRef.value) return
  const rect = viewportRef.value.getBoundingClientRect()
  viewportSize.value = { width: rect.width, height: rect.height }
}

function handleImageLoad(event) {
  imageMetrics.value = {
    naturalWidth: event.target.naturalWidth,
    naturalHeight: event.target.naturalHeight
  }
  fitView()
}

function fitView() {
  zoom.value = 1
  pan.value = { x: 0, y: 0 }
}

function resetView() {
  fitView()
}

function zoomAtCenter(multiplier) {
  const center = {
    x: viewportSize.value.width / 2,
    y: viewportSize.value.height / 2
  }
  setZoom(zoom.value * multiplier, center)
}

function setZoom(nextZoom, center) {
  const normalized = clamp(nextZoom, MIN_ZOOM, MAX_ZOOM)
  const ratio = normalized / zoom.value
  pan.value = {
    x: center.x - (center.x - pan.value.x) * ratio,
    y: center.y - (center.y - pan.value.y) * ratio
  }
  zoom.value = normalized
}

function pointFromEvent(event) {
  if (!viewportRef.value || !imageMetrics.value.naturalWidth) return null
  return pointerToImagePoint({
    clientX: event.clientX,
    clientY: event.clientY,
    containerRect: viewportRef.value.getBoundingClientRect(),
    pan: pan.value,
    zoom: zoom.value,
    imageRect: imageRect.value,
    naturalWidth: imageMetrics.value.naturalWidth,
    naturalHeight: imageMetrics.value.naturalHeight
  })
}

function stageX(x) {
  return imageRect.value.x + x * imageRect.value.scale
}

function stageY(y) {
  return imageRect.value.y + y * imageRect.value.scale
}

function stageWidth(width) {
  return width * imageRect.value.scale
}

function displayBox(box) {
  return {
    x: stageX(box.x),
    y: stageY(box.y),
    width: stageWidth(box.width),
    height: stageWidth(box.height)
  }
}

function displayPoints(points = []) {
  return points.map((point) => `${stageX(point.x)},${stageY(point.y)}`).join(' ')
}

function ensureActiveClass() {
  if (activeClass.value) return true
  errorMessage.value = 'Select or create a class before annotating.'
  return false
}

function pushHistory() {
  if (!selectedImage.value) return
  history.value.push(JSON.stringify(selectedImage.value.annotations || createEmptyAnnotations(taskType.value)))
  redoStack.value = []
  saveState.value = ''
}

function replaceAnnotations(nextAnnotations, shouldPushHistory = true) {
  if (!selectedImage.value) return
  if (shouldPushHistory) pushHistory()
  selectedImage.value.annotations = normalizeAnnotations(taskType.value, nextAnnotations)
  scheduleAutosave()
}

function undo() {
  if (!selectedImage.value || !history.value.length) return
  redoStack.value.push(JSON.stringify(selectedImage.value.annotations || createEmptyAnnotations(taskType.value)))
  selectedImage.value.annotations = JSON.parse(history.value.pop())
  selectedAnnotation.value = null
  scheduleAutosave()
}

function redo() {
  if (!selectedImage.value || !redoStack.value.length) return
  history.value.push(JSON.stringify(selectedImage.value.annotations || createEmptyAnnotations(taskType.value)))
  selectedImage.value.annotations = JSON.parse(redoStack.value.pop())
  selectedAnnotation.value = null
  scheduleAutosave()
}

function handleWheel(event) {
  event.preventDefault()
  setZoom(zoom.value * (event.deltaY < 0 ? 1.12 : 0.88), {
    x: event.clientX - event.currentTarget.getBoundingClientRect().left,
    y: event.clientY - event.currentTarget.getBoundingClientRect().top
  })
}

function handleCanvasDown(event) {
  if (!selectedImage.value) return
  errorMessage.value = ''

  if (event.button === 1 || isSpaceDown.value || activeTool.value === 'select') {
    interaction.value = { type: 'pan', start: { x: event.clientX, y: event.clientY }, pan: { ...pan.value } }
    event.preventDefault()
    return
  }

  const point = pointFromEvent(event)
  if (!point) return

  if (activeTool.value === 'bbox') {
    if (!ensureActiveClass()) return
    draftBox.value = {
      startX: point.x,
      startY: point.y,
      x: point.x,
      y: point.y,
      width: 0,
      height: 0,
      classId: activeClass.value.id,
      color: activeClass.value.color
    }
    interaction.value = { type: 'draw-box' }
  }

  if (activeTool.value === 'polygon') {
    if (!ensureActiveClass()) return
    if (!draftPolygon.value) {
      draftPolygon.value = {
        id: createId(),
        classId: activeClass.value.id,
        color: activeClass.value.color,
        points: []
      }
    }
    if (draftPolygon.value.points.length >= MIN_POLYGON_POINTS && nearFirstPoint(point)) {
      closeDraftPolygon()
      return
    }
    draftPolygon.value.points.push(point)
    cursorPoint.value = point
  }
}

function handleCanvasMove(event) {
  const point = pointFromEvent(event)
  cursorPoint.value = point

  if (interaction.value?.type === 'pan') {
    pan.value = {
      x: interaction.value.pan.x + event.clientX - interaction.value.start.x,
      y: interaction.value.pan.y + event.clientY - interaction.value.start.y
    }
    return
  }

  if (!point || !selectedImage.value) return

  if (activeTool.value === 'select' && !interaction.value) {
    let hint = null
    for (const polygon of selectedAnnotations.value.polygons || []) {
      const ins = findEdgeInsertionIn(point, polygon)
      if (ins && (!hint || ins.dist < hint.dist)) hint = { id: polygon.id, point: ins.point, dist: ins.dist }
    }
    insertHint.value = hint
  } else if (insertHint.value) {
    insertHint.value = null
  }

  if (interaction.value?.type === 'draw-box' && draftBox.value) {
    draftBox.value.x = Math.min(draftBox.value.startX, point.x)
    draftBox.value.y = Math.min(draftBox.value.startY, point.y)
    draftBox.value.width = Math.abs(point.x - draftBox.value.startX)
    draftBox.value.height = Math.abs(point.y - draftBox.value.startY)
  }

  if (interaction.value?.type === 'move-box') {
    const annotations = selectedAnnotations.value
    const box = annotations.bboxes.find((item) => item.id === interaction.value.id)
    if (!box) return
    const dx = point.x - interaction.value.startPoint.x
    const dy = point.y - interaction.value.startPoint.y
    box.x = clamp(Math.round(interaction.value.startBox.x + dx), 0, imageMetrics.value.naturalWidth - box.width)
    box.y = clamp(Math.round(interaction.value.startBox.y + dy), 0, imageMetrics.value.naturalHeight - box.height)
    selectedImage.value.annotations = annotations
  }

  if (interaction.value?.type === 'resize-box') {
    resizeBox(point)
  }

  if (interaction.value?.type === 'move-polygon-point') {
    const polygon = selectedAnnotations.value.polygons.find((item) => item.id === interaction.value.id)
    if (polygon?.points[interaction.value.pointIndex]) {
      polygon.points[interaction.value.pointIndex] = point
      selectedImage.value.annotations = selectedAnnotations.value
    }
  }

  if (interaction.value?.type === 'move-keypoint') {
    const skeleton = selectedAnnotations.value.skeletons.find((item) => item.id === interaction.value.id)
    if (skeleton?.keypoints[interaction.value.pointIndex]) {
      skeleton.keypoints[interaction.value.pointIndex].x = point.x
      skeleton.keypoints[interaction.value.pointIndex].y = point.y
      selectedImage.value.annotations = selectedAnnotations.value
    }
  }

  if (interaction.value?.type === 'move-skeleton') {
    const skeleton = selectedAnnotations.value.skeletons.find((item) => item.id === interaction.value.id)
    if (skeleton) {
      const dx = point.x - interaction.value.startPoint.x
      const dy = point.y - interaction.value.startPoint.y
      const w = imageMetrics.value.naturalWidth
      const h = imageMetrics.value.naturalHeight
      skeleton.keypoints.forEach((kp, i) => {
        const start = interaction.value.startPoints[i]
        kp.x = clamp(Math.round(start.x + dx), 0, w)
        kp.y = clamp(Math.round(start.y + dy), 0, h)
      })
      selectedImage.value.annotations = selectedAnnotations.value
    }
  }
}

function handleCanvasUp() {
  const finishingEdit = interaction.value && !['pan', 'draw-box'].includes(interaction.value.type)
  if (interaction.value?.type === 'draw-box' && draftBox.value) {
    const box = clampBox(draftBox.value, imageMetrics.value.naturalWidth, imageMetrics.value.naturalHeight)
    if (box) {
      const annotations = selectedAnnotations.value
      annotations.bboxes.push({
        id: createId(),
        classId: draftBox.value.classId,
        color: draftBox.value.color,
        ...box
      })
      replaceAnnotations(annotations)
    }
    draftBox.value = null
  }
  interaction.value = null
  if (finishingEdit) scheduleAutosave()
}

function handleCanvasLeave() {
  handleCanvasUp()
  cursorPoint.value = null
}

function cursorInsideImage() {
  return cursorPoint.value && imageMetrics.value.naturalWidth && imageMetrics.value.naturalHeight
}

function handleCanvasDblClick() {
  if (activeTool.value === 'polygon') closeDraftPolygon()
}

function closeDraftPolygon() {
  if (!draftPolygon.value) return
  if (draftPolygon.value.points.length >= MIN_POLYGON_POINTS) {
    const annotations = selectedAnnotations.value
    annotations.polygons.push({
      ...draftPolygon.value,
      points: draftPolygon.value.points.map((point) => ({ ...point }))
    })
    replaceAnnotations(annotations)
  }
  draftPolygon.value = null
  cursorPoint.value = null
}

// ponytail: image-space distance, screen tolerance scaled by current zoom+fit
function nearFirstPoint(point) {
  const first = draftPolygon.value.points[0]
  const tolerance = CLOSE_TOLERANCE_PX / (imageRect.value.scale * zoom.value)
  return Math.hypot(point.x - first.x, point.y - first.y) <= tolerance
}

function cancelDraft() {
  draftBox.value = null
  draftPolygon.value = null
  cursorPoint.value = null
  interaction.value = null
}

function selectAnnotation(type, id) {
  selectedAnnotation.value = { type, id }
}

// In a drawing tool, let mousedown bubble to the canvas so a new shape can be
// started on top of an existing annotation. Only capture (stop + act) in select mode.
function guardSelect(event) {
  if (activeTool.value !== 'select') return false
  event.stopPropagation()
  return true
}

function selectOnCanvas(event, type, id) {
  if (!guardSelect(event)) return
  selectAnnotation(type, id)
}

function startBoxMove(event, box) {
  if (!guardSelect(event)) return
  const point = pointFromEvent(event)
  if (!point) return
  selectAnnotation('bbox', box.id)
  pushHistory()
  interaction.value = {
    type: 'move-box',
    id: box.id,
    startPoint: point,
    startBox: { ...box }
  }
}

function startBoxResize(event, box, handle) {
  if (!guardSelect(event)) return
  const point = pointFromEvent(event)
  if (!point) return
  selectAnnotation('bbox', box.id)
  pushHistory()
  interaction.value = {
    type: 'resize-box',
    id: box.id,
    handle,
    startBox: { ...box }
  }
}

function resizeBox(point) {
  const annotations = selectedAnnotations.value
  const box = annotations.bboxes.find((item) => item.id === interaction.value.id)
  if (!box) return
  const start = interaction.value.startBox
  const next = { ...start }
  if (interaction.value.handle.includes('e')) next.width = point.x - start.x
  if (interaction.value.handle.includes('s')) next.height = point.y - start.y
  if (interaction.value.handle.includes('w')) {
    next.x = point.x
    next.width = start.x + start.width - point.x
  }
  if (interaction.value.handle.includes('n')) {
    next.y = point.y
    next.height = start.y + start.height - point.y
  }
  const clamped = clampBox(next, imageMetrics.value.naturalWidth, imageMetrics.value.naturalHeight, 1)
  if (!clamped) return
  Object.assign(box, clamped)
  selectedImage.value.annotations = annotations
}

function findEdgeInsertionIn(point, polygon) {
  const tolerance = INSERT_TOLERANCE_PX / (imageRect.value.scale * zoom.value)
  const pts = polygon.points
  let best = null
  for (let i = 0; i < pts.length; i++) {
    const a = pts[i]
    const b = pts[(i + 1) % pts.length]
    const proj = pointOnSegment(point, a, b)
    if (proj.dist <= tolerance && (!best || proj.dist < best.dist)) {
      best = { index: i + 1, point: { x: Math.round(proj.x), y: Math.round(proj.y) }, dist: proj.dist }
    }
  }
  return best
}

// ponytail: scoped to clicked polygon; the <polygon> element is the hit target,
// so we intercept its mousedown to insert on edge before it becomes a selection.
function onPolygonMouseDown(event, polygon) {
  if (!guardSelect(event)) return
  const point = pointFromEvent(event)
  if (point) {
    const ins = findEdgeInsertionIn(point, polygon)
    if (ins) {
      pushHistory()
      polygon.points.splice(ins.index, 0, ins.point)
      selectedAnnotation.value = { type: 'polygon', id: polygon.id }
      selectedVertex.value = { id: polygon.id, pointIndex: ins.index }
      selectedImage.value.annotations = selectedAnnotations.value
      insertHint.value = null
      scheduleAutosave()
      return
    }
  }
  selectAnnotation('polygon', polygon.id)
}

function deleteSelectedVertex() {
  const sel = selectedVertex.value
  if (!sel) return false
  const polygon = selectedAnnotations.value.polygons.find((item) => item.id === sel.id)
  selectedVertex.value = null
  if (!polygon || polygon.points.length <= MIN_POLYGON_POINTS) return true
  pushHistory()
  polygon.points.splice(sel.pointIndex, 1)
  selectedImage.value.annotations = selectedAnnotations.value
  scheduleAutosave()
  return true
}

function startPolygonPointMove(event, polygon, pointIndex) {
  if (!guardSelect(event)) return
  selectAnnotation('polygon', polygon.id)
  selectedVertex.value = { id: polygon.id, pointIndex }
  pushHistory()
  interaction.value = { type: 'move-polygon-point', id: polygon.id, pointIndex }
}

function startKeypointMove(event, skeleton, pointIndex) {
  if (!guardSelect(event)) return
  selectAnnotation('skeleton', skeleton.id)
  pushHistory()
  interaction.value = { type: 'move-keypoint', id: skeleton.id, pointIndex }
}

function skeletonStageBox(skeleton) {
  const xs = skeleton.keypoints.map((k) => k.x)
  const ys = skeleton.keypoints.map((k) => k.y)
  const pad = 8 / zoom.value
  return {
    x: stageX(Math.min(...xs)) - pad,
    y: stageY(Math.min(...ys)) - pad,
    width: stageWidth(Math.max(...xs) - Math.min(...xs)) + pad * 2,
    height: stageWidth(Math.max(...ys) - Math.min(...ys)) + pad * 2
  }
}

function startSkeletonMove(event, skeleton) {
  if (!guardSelect(event)) return
  selectAnnotation('skeleton', skeleton.id)
  const point = pointFromEvent(event)
  if (!point) return
  pushHistory()
  interaction.value = {
    type: 'move-skeleton',
    id: skeleton.id,
    startPoint: point,
    startPoints: skeleton.keypoints.map((k) => ({ x: k.x, y: k.y }))
  }
}

function toggleKeypoint(skeleton, pointIndex) {
  const annotations = selectedAnnotations.value
  const target = annotations.skeletons.find((item) => item.id === skeleton.id)
  if (!target) return
  pushHistory()
  target.keypoints[pointIndex].visible = !target.keypoints[pointIndex].visible
  selectedImage.value.annotations = annotations
  scheduleAutosave()
}

function deleteSelected() {
  if (!selectedAnnotation.value) return
  deleteAnnotation(selectedAnnotation.value.type, selectedAnnotation.value.id)
}

function deleteAnnotation(type, id) {
  const annotations = selectedAnnotations.value
  pushHistory()
  if (type === 'classification') {
    replaceAnnotations(createEmptyAnnotations('classification'), false)
    return
  }
  if (type === 'bbox') {
    annotations.bboxes = annotations.bboxes.filter((item) => item.id !== id)
  }
  if (type === 'polygon') {
    annotations.polygons = annotations.polygons.filter((item) => item.id !== id)
  }
  if (type === 'skeleton') {
    annotations.skeletons = annotations.skeletons.filter((item) => item.id !== id)
  }
  selectedAnnotation.value = null
  selectedImage.value.annotations = annotations
  scheduleAutosave()
}

function markNull() {
  selectedAnnotation.value = null
  replaceAnnotations({ ...createEmptyAnnotations(taskType.value), null: true })
}

function clearAnnotations() {
  selectedAnnotation.value = null
  replaceAnnotations(createEmptyAnnotations(taskType.value))
}

function setClassification(classId) {
  replaceAnnotations({ ...createEmptyAnnotations('classification'), classId, null: false })
}

function spawnSkeleton() {
  if (!ensureActiveClass() || !selectedImage.value) return
  const annotations = selectedAnnotations.value
  const skeleton = createPoseSkeleton({
    id: createId(),
    classId: activeClass.value.id,
    color: activeClass.value.color,
    center: {
      x: imageMetrics.value.naturalWidth / 2,
      y: imageMetrics.value.naturalHeight / 2
    }
  })
  annotations.skeletons.push(skeleton)
  replaceAnnotations(annotations)
  selectedAnnotation.value = { type: 'skeleton', id: skeleton.id }
}

function runMockAssist() {
  if (!selectedImage.value) return
  errorMessage.value = ''
  if (!projectClasses.value.length) {
    errorMessage.value = 'Create a class before using mock AI assist.'
    return
  }
  activeClass.value = activeClass.value || projectClasses.value[0]
  const classId = activeClass.value.id
  const color = activeClass.value.color
  const w = imageMetrics.value.naturalWidth
  const h = imageMetrics.value.naturalHeight

  if (taskType.value === 'classification') {
    setClassification(classId)
    return
  }
  if (taskType.value === 'object_detection') {
    replaceAnnotations({
      ...selectedAnnotations.value,
      null: false,
      bboxes: [
        ...selectedAnnotations.value.bboxes,
        { id: createId(), classId, color, x: Math.round(w * 0.25), y: Math.round(h * 0.2), width: Math.round(w * 0.5), height: Math.round(h * 0.55) }
      ]
    })
    return
  }
  if (taskType.value === 'segmentation') {
    replaceAnnotations({
      ...selectedAnnotations.value,
      null: false,
      polygons: [
        ...selectedAnnotations.value.polygons,
        {
          id: createId(),
          classId,
          color,
          points: [
            { x: Math.round(w * 0.5), y: Math.round(h * 0.18) },
            { x: Math.round(w * 0.78), y: Math.round(h * 0.48) },
            { x: Math.round(w * 0.5), y: Math.round(h * 0.82) },
            { x: Math.round(w * 0.22), y: Math.round(h * 0.48) }
          ]
        }
      ]
    })
    return
  }
  spawnSkeleton()
}

async function saveAnnotation() {
  if (!selectedImage.value) return
  errorMessage.value = ''
  saveState.value = 'Saving...'
  try {
    const annotations = normalizeAnnotations(taskType.value, selectedImage.value.annotations)
    const status = isAnnotationComplete(taskType.value, annotations) ? 'annotated' : 'unannotated'
    const updatedAsset = await saveAssetAnnotations(props.project.id, selectedImage.value.id, annotations, status)
    selectedImage.value.annotations = updatedAsset.annotations
    selectedImage.value.status = updatedAsset.status
    saveState.value = 'Autosaved'
    emit('saved', updatedAsset)
  } catch (error) {
    errorMessage.value = 'Could not save annotation. Check backend status.'
    saveState.value = ''
  }
}

function scheduleAutosave() {
  if (!selectedImage.value) return
  clearTimeout(autosaveTimer)
  saveState.value = 'Saving...'
  autosaveTimer = setTimeout(saveAnnotation, 500)
}

async function deleteAsset(event, asset) {
  event.stopPropagation()
  if (!window.confirm(`Delete ${asset.filename}?`)) return
  try {
    await deleteDatasetAssets(props.project.id, [asset.id])
    if (selectedImage.value?.id === asset.id) selectAsset(null)
    emit('deleted', asset)
  } catch (error) {
    errorMessage.value = 'Could not delete image.'
  }
}

async function addClass() {
  const name = newClassName.value.trim()
  if (!name || projectClasses.value.some((item) => item.name.toLowerCase() === name.toLowerCase())) return
  const nextClass = { id: createId(), name, color: generateClassColor(projectClasses.value.length) }
  const backup = [...projectClasses.value]
  projectClasses.value.push(nextClass)
  activeClass.value = nextClass
  newClassName.value = ''
  try {
    await updateProject(props.project.id, { classes: projectClasses.value })
  } catch (error) {
    projectClasses.value = backup
    activeClass.value = backup[0] || null
    errorMessage.value = 'Could not save class list.'
  }
}

async function removeClass(classId) {
  const backup = [...projectClasses.value]
  projectClasses.value = projectClasses.value.filter((item) => item.id !== classId)
  if (activeClass.value?.id === classId) activeClass.value = projectClasses.value[0] || null
  try {
    await updateProject(props.project.id, { classes: projectClasses.value })
  } catch (error) {
    projectClasses.value = backup
    errorMessage.value = 'Could not remove class.'
  }
}

function recolorAnnotations(classId, color) {
  if (!selectedImage.value) return
  const annotations = selectedAnnotations.value
  let changed = false
  const apply = (items = []) => {
    for (const item of items) {
      if (item.classId === classId && item.color !== color) {
        item.color = color
        changed = true
      }
    }
  }
  apply(annotations.bboxes)
  apply(annotations.polygons)
  apply(annotations.skeletons)
  if (changed) {
    selectedImage.value.annotations = annotations
    scheduleAutosave()
  }
}

async function updateClassColor(classId, color) {
  const target = projectClasses.value.find((item) => item.id === classId)
  if (!target || target.color === color) return
  const backup = projectClasses.value.map((item) => ({ ...item }))
  target.color = color
  recolorAnnotations(classId, color)
  try {
    await updateProject(props.project.id, { classes: projectClasses.value })
  } catch (error) {
    projectClasses.value = backup
    errorMessage.value = 'Could not save class color.'
  }
}

function findClass(classId) {
  return projectClasses.value.find((item) => item.id === classId)
}

function findAnnotation(selection) {
  if (!selection) return null
  const annotations = selectedAnnotations.value
  if (selection.type === 'bbox') return annotations.bboxes.find((item) => item.id === selection.id)
  if (selection.type === 'polygon') return annotations.polygons.find((item) => item.id === selection.id)
  if (selection.type === 'skeleton') return annotations.skeletons.find((item) => item.id === selection.id)
  return null
}

function annotationItems() {
  const annotations = selectedAnnotations.value
  if (taskType.value === 'classification') {
    return annotations.classId ? [{ type: 'classification', id: annotations.classId, classId: annotations.classId }] : []
  }
  if (taskType.value === 'object_detection') return annotations.bboxes.map((item) => ({ ...item, type: 'bbox' }))
  if (taskType.value === 'segmentation') return annotations.polygons.map((item) => ({ ...item, type: 'polygon' }))
  if (taskType.value === 'pose_estimation') return annotations.skeletons.map((item) => ({ ...item, type: 'skeleton' }))
  return []
}

function handleKeydown(event) {
  if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) return

  if (event.key === '?' || event.key === '/') {
    showShortcuts.value = !showShortcuts.value
    return
  }
  if (event.key === 'Escape') {
    if (showShortcuts.value) { showShortcuts.value = false; return }
    cancelDraft()
    return
  }
  if (event.code === 'Space') {
    isSpaceDown.value = true
    event.preventDefault()
    return
  }
  if (/^[1-9]$/.test(event.key)) {
    const cls = projectClasses.value[Number(event.key) - 1]
    if (!cls) return
    if (taskType.value === 'classification') setClassification(cls.id)
    else activeClass.value = cls
    return
  }
  if (event.key === 'Backspace' && draftPolygon.value?.points.length) {
    draftPolygon.value.points.pop()
    if (!draftPolygon.value.points.length) draftPolygon.value = null
    return
  }

  if (event.key.toLowerCase() === 'v') activeTool.value = 'select'
  if (event.key.toLowerCase() === 'b' && taskType.value === 'object_detection') activeTool.value = 'bbox'
  if (event.key.toLowerCase() === 'p' && taskType.value === 'segmentation') activeTool.value = 'polygon'
  if (event.key.toLowerCase() === 'k' && taskType.value === 'pose_estimation') activeTool.value = 'pose'
  if (event.key === 'Delete' || event.key === 'Backspace') {
    if (deleteSelectedVertex()) return
    deleteSelected()
  }
  if (event.ctrlKey && event.key.toLowerCase() === 'z') undo()
  if ((event.ctrlKey && event.key.toLowerCase() === 'y') || (event.ctrlKey && event.shiftKey && event.key.toLowerCase() === 'z')) redo()
}

function handleKeyup(event) {
  if (event.code === 'Space') isSpaceDown.value = false
}

function createId() {
  return crypto?.randomUUID ? crypto.randomUUID() : `ann-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

function generateClassColor(index) {
  const colors = ['#007aff', '#ff9f0a', '#30d158', '#ff3b30', '#8b5cf6', '#00a7c7', '#d946ef']
  return colors[index % colors.length]
}
</script>

<template>
  <div class="annotation-shell">
    <aside class="queue-panel" aria-label="Dataset queue">
      <div class="panel-header">
        <button class="icon-text-btn" type="button" @click="$emit('close')">
          <ChevronLeft :size="16" />
          Back
        </button>
        <span class="task-pill">{{ selectedQueuePosition }} / {{ currentAssets.length }} · {{ taskLabel }}</span>
      </div>

      <div class="queue-tabs" role="tablist" aria-label="Asset status">
        <button :class="{ active: activeQueue === 'unannotated' }" type="button" @click="activeQueue = 'unannotated'">
          To label {{ unannotatedAssets.length }}
        </button>
        <button :class="{ active: activeQueue === 'annotated' }" type="button" @click="activeQueue = 'annotated'">
          Done {{ annotatedAssets.length }}
        </button>
      </div>

      <div class="queue-search-wrap">
        <input v-model="queueQuery" type="search" class="queue-search" placeholder="Search filename…" />
      </div>

      <div class="asset-list">
        <div
          v-for="asset in filteredAssets"
          :key="asset.id"
          :class="['asset-row', { selected: selectedImage?.id === asset.id }]"
          role="button"
          tabindex="0"
          @click="selectAsset(asset)"
          @keyup.enter="selectAsset(asset)"
        >
          <img :src="getImageUrl(asset)" class="queue-thumb" loading="lazy" draggable="false" alt="" />
          <span class="asset-name" :title="asset.filename">{{ asset.filename }}</span>
          <span class="asset-row-footer">
            <span class="asset-status">{{ asset.status }}</span>
            <button class="row-delete" type="button" title="Delete image" @click="deleteAsset($event, asset)">
              <Trash2 :size="14" />
            </button>
          </span>
        </div>
        <p v-if="currentAssets.length === 0" class="empty-state">No assets in this queue.</p>
        <p v-else-if="filteredAssets.length === 0" class="empty-state">No match for "{{ queueQuery }}".</p>
      </div>
    </aside>

    <main class="studio-panel">
      <div class="toolbar" aria-label="Annotation toolbar">
        <div class="toolbar-group">
          <button
            v-for="tool in taskTools"
            :key="tool.id"
            :class="['tool-btn', { active: activeTool === tool.id }]"
            type="button"
            :title="`${tool.label} (${tool.shortcut})`"
            @click="activeTool = tool.id"
          >
            <MousePointer2 v-if="tool.id === 'select'" :size="17" />
            <BoxSelect v-if="tool.id === 'bbox'" :size="17" />
            <Pentagon v-if="tool.id === 'polygon'" :size="17" />
            <Waypoints v-if="tool.id === 'pose'" :size="17" />
            <span>{{ tool.label }}</span>
          </button>
        </div>

        <div class="toolbar-group">
          <button class="icon-btn" type="button" title="Zoom out" @click="zoomAtCenter(0.85)">
            <ZoomOut :size="17" />
          </button>
          <span class="zoom-readout">{{ Math.round(zoom * 100) }}%</span>
          <button class="icon-btn" type="button" title="Zoom in" @click="zoomAtCenter(1.18)">
            <ZoomIn :size="17" />
          </button>
          <button class="icon-btn" type="button" title="Fit image" @click="fitView">
            <Maximize2 :size="17" />
          </button>
          <button class="icon-btn" type="button" title="Reset view" @click="resetView">
            <RotateCcw :size="17" />
          </button>
        </div>

        <div class="toolbar-group">
          <button class="icon-btn" type="button" title="Undo" :disabled="!canUndo" @click="undo">
            <Undo2 :size="17" />
          </button>
          <button class="icon-btn" type="button" title="Redo" :disabled="!canRedo" @click="redo">
            <Redo2 :size="17" />
          </button>
        </div>

        <div class="toolbar-spacer"></div>

        <div class="toolbar-group">
          <button class="tool-btn" type="button" title="Mock AI assist" @click="runMockAssist">
            <BrainCircuit :size="17" />
            <span>Mock AI</span>
          </button>
          <button class="tool-btn" type="button" title="Mark this image as null/background" @click="markNull">
            <CircleDot :size="17" />
            <span>Null</span>
          </button>
          <button class="icon-btn" type="button" title="Shortcuts (?)" @click="showShortcuts = !showShortcuts">
            <HelpCircle :size="17" />
          </button>
        </div>
      </div>

      <div v-if="selectedImage" class="canvas-wrap">
        <div
          ref="viewportRef"
          class="canvas-viewport"
          :style="{ cursor: canvasCursor }"
          @wheel="handleWheel"
          @mousedown="handleCanvasDown"
          @mousemove="handleCanvasMove"
          @mouseup="handleCanvasUp"
          @mouseleave="handleCanvasLeave"
          @dblclick="handleCanvasDblClick"
          @contextmenu.prevent
        >
          <div class="canvas-stage" :style="stageStyle">
            <img
              :src="getImageUrl(selectedImage)"
              :alt="selectedImage.filename"
              class="canvas-image"
              :style="imgStyle"
              draggable="false"
              @load="handleImageLoad"
            />
            <svg
              class="annotation-layer"
              :viewBox="`0 0 ${viewportSize.width} ${viewportSize.height}`"
              :width="viewportSize.width"
              :height="viewportSize.height"
              aria-hidden="true"
            >
              <g v-if="cursorInsideImage()" class="cursor-guide">
                <line
                  :x1="stageX(cursorPoint.x)"
                  y1="0"
                  :x2="stageX(cursorPoint.x)"
                  :y2="viewportSize.height"
                />
                <line
                  x1="0"
                  :y1="stageY(cursorPoint.y)"
                  :x2="viewportSize.width"
                  :y2="stageY(cursorPoint.y)"
                />
              </g>

              <g v-if="insertHint && activeTool === 'select'" class="insert-hint">
                <circle :cx="stageX(insertHint.point.x)" :cy="stageY(insertHint.point.y)" :r="5 / zoom" />
                <line
                  :x1="stageX(insertHint.point.x) - 3 / zoom"
                  :y1="stageY(insertHint.point.y)"
                  :x2="stageX(insertHint.point.x) + 3 / zoom"
                  :y2="stageY(insertHint.point.y)"
                />
                <line
                  :x1="stageX(insertHint.point.x)"
                  :y1="stageY(insertHint.point.y) - 3 / zoom"
                  :x2="stageX(insertHint.point.x)"
                  :y2="stageY(insertHint.point.y) + 3 / zoom"
                />
              </g>

              <g v-for="box in selectedAnnotations.bboxes || []" :key="box.id">
                <rect
                  v-bind="displayBox(box)"
                  :class="['annotation-box', { selected: selectedAnnotation?.id === box.id }]"
                  :stroke="box.color"
                  @mousedown="startBoxMove($event, box)"
                />
                <text :x="displayBox(box).x" :y="displayBox(box).y - 6" :fill="box.color" class="label-text">
                  {{ findClass(box.classId)?.name || 'Unknown' }}
                </text>
                <g v-if="selectedAnnotation?.id === box.id">
                  <circle
                    v-for="handle in ['nw', 'ne', 'sw', 'se']"
                    :key="handle"
                    class="resize-handle"
                    :cx="handle.includes('w') ? displayBox(box).x : displayBox(box).x + displayBox(box).width"
                    :cy="handle.includes('n') ? displayBox(box).y : displayBox(box).y + displayBox(box).height"
                    :r="4 / zoom"
                    @mousedown="startBoxResize($event, box, handle)"
                  />
                </g>
              </g>

              <rect
                v-if="draftBox"
                v-bind="displayBox(draftBox)"
                class="draft-shape"
                :stroke="draftBox.color"
              />

              <g v-for="polygon in selectedAnnotations.polygons || []" :key="polygon.id">
                <polygon
                  :points="displayPoints(polygon.points)"
                  :class="['annotation-polygon', { selected: selectedAnnotation?.id === polygon.id }]"
                  :stroke="polygon.color"
                  @mousedown="onPolygonMouseDown($event, polygon)"
                />
                <text
                  v-if="polygon.points.length"
                  :x="stageX(polygon.points[0].x)"
                  :y="stageY(polygon.points[0].y) - 6"
                  :fill="polygon.color"
                  class="label-text"
                >
                  {{ findClass(polygon.classId)?.name || 'Unknown' }}
                </text>
                <circle
                  v-for="(point, pointIndex) in polygon.points"
                  :key="`${polygon.id}-${pointIndex}`"
                  :class="['vertex-handle', { 'vertex-selected': selectedVertex?.id === polygon.id && selectedVertex?.pointIndex === pointIndex }]"
                  :cx="stageX(point.x)"
                  :cy="stageY(point.y)"
                  :r="4 / zoom"
                  @mousedown="startPolygonPointMove($event, polygon, pointIndex)"
                />
              </g>

              <g v-if="draftPolygon">
                <polyline :points="displayPoints(draftPolygon.points)" class="draft-line" :stroke="draftPolygon.color" />
                <line
                  v-if="draftPolygon.points.length && cursorPoint"
                  :x1="stageX(draftPolygon.points[draftPolygon.points.length - 1].x)"
                  :y1="stageY(draftPolygon.points[draftPolygon.points.length - 1].y)"
                  :x2="stageX(cursorPoint.x)"
                  :y2="stageY(cursorPoint.y)"
                  class="draft-line"
                  :stroke="draftPolygon.color"
                />
                <circle
                  v-for="(point, pointIndex) in draftPolygon.points"
                  :key="`draft-${pointIndex}`"
                  class="vertex-handle"
                  :cx="stageX(point.x)"
                  :cy="stageY(point.y)"
                  :r="3 / zoom"
                />
                <circle
                  v-if="draftPolygon.points.length >= MIN_POLYGON_POINTS"
                  class="vertex-close"
                  :cx="stageX(draftPolygon.points[0].x)"
                  :cy="stageY(draftPolygon.points[0].y)"
                  :r="5 / zoom"
                />
              </g>

              <g v-for="skeleton in selectedAnnotations.skeletons || []" :key="skeleton.id">
                <rect
                  v-if="selectedAnnotation?.id === skeleton.id"
                  v-bind="skeletonStageBox(skeleton)"
                  class="skeleton-move-box"
                  @mousedown="startSkeletonMove($event, skeleton)"
                />
                <line
                  v-for="(edge, edgeIndex) in COCO_EDGES"
                  :key="`${skeleton.id}-hit-${edgeIndex}`"
                  class="skeleton-edge-hit"
                  :x1="stageX(skeleton.keypoints[edge[0]].x)"
                  :y1="stageY(skeleton.keypoints[edge[0]].y)"
                  :x2="stageX(skeleton.keypoints[edge[1]].x)"
                  :y2="stageY(skeleton.keypoints[edge[1]].y)"
                  @mousedown="startSkeletonMove($event, skeleton)"
                />
                <line
                  v-for="(edge, edgeIndex) in COCO_EDGES"
                  :key="`${skeleton.id}-edge-${edgeIndex}`"
                  class="skeleton-edge"
                  :stroke="skeleton.color"
                  :x1="stageX(skeleton.keypoints[edge[0]].x)"
                  :y1="stageY(skeleton.keypoints[edge[0]].y)"
                  :x2="stageX(skeleton.keypoints[edge[1]].x)"
                  :y2="stageY(skeleton.keypoints[edge[1]].y)"
                />
                <circle
                  v-for="(keypoint, pointIndex) in skeleton.keypoints"
                  :key="`${skeleton.id}-point-${pointIndex}`"
                  :class="['keypoint', { hidden: !keypoint.visible }]"
                  :fill="skeleton.color"
                  :cx="stageX(keypoint.x)"
                  :cy="stageY(keypoint.y)"
                  :r="4 / zoom"
                  @mousedown="startKeypointMove($event, skeleton, pointIndex)"
                  @mouseenter="labeledKeypoint = { id: skeleton.id, index: pointIndex }"
                  @mouseleave="labeledKeypoint = null"
                  @dblclick.stop="toggleKeypoint(skeleton, pointIndex)"
                />
                <text
                  v-if="labeledKeypoint?.id === skeleton.id"
                  :x="stageX(skeleton.keypoints[labeledKeypoint.index].x) + 6"
                  :y="stageY(skeleton.keypoints[labeledKeypoint.index].y) - 6"
                  :fill="skeleton.color"
                  class="label-text"
                  pointer-events="none"
                >
                  {{ COCO_KEYPOINTS[labeledKeypoint.index] }}
                </text>
                <text
                  v-if="skeleton.keypoints.length"
                  :x="stageX(skeleton.keypoints[0].x)"
                  :y="stageY(skeleton.keypoints[0].y) - 10"
                  :fill="skeleton.color"
                  class="label-text"
                  @mousedown="selectOnCanvas($event, 'skeleton', skeleton.id)"
                >
                  {{ findClass(skeleton.classId)?.name || 'Unknown' }}
                </text>
              </g>
            </svg>
          </div>

          <div v-if="selectedAnnotations.null" class="null-banner">
            <Check :size="16" />
            Marked as null/background
          </div>
          <div v-if="hintText" class="crosshair-hint">
            <Crosshair :size="16" />
            {{ hintText }}
          </div>
        </div>

        <div class="canvas-footer" role="status" aria-live="polite">
          <span>{{ selectedImage.filename }}</span>
          <span>{{ imageMetrics.naturalWidth }} x {{ imageMetrics.naturalHeight }}</span>
          <span v-if="saveState">{{ saveState }}</span>
          <span v-if="errorMessage" class="error-text">{{ errorMessage }}</span>
        </div>
      </div>

      <div v-else class="empty-canvas">
        Select an asset to start annotating.
      </div>
    </main>

    <aside class="inspector-panel" aria-label="Annotation inspector">
      <section class="inspector-section">
        <div class="section-title">
          <h3>Classes</h3>
        </div>
        <div class="add-class">
          <input v-model="newClassName" type="text" placeholder="New class" @keyup.enter="addClass" />
          <button class="icon-btn" type="button" title="Add class" @click="addClass">
            <Check :size="16" />
          </button>
        </div>
        <div class="class-list">
          <button
            v-for="(item, classIndex) in projectClasses"
            :key="item.id"
            :class="['class-row', { active: activeClass?.id === item.id || selectedAnnotations.classId === item.id }]"
            type="button"
            @click="taskType === 'classification' ? setClassification(item.id) : activeClass = item"
          >
            <label class="color-dot-wrap" :title="'Change color'">
              <span class="color-dot" :style="{ backgroundColor: item.color }"></span>
              <input
                type="color"
                class="color-input"
                :value="item.color"
                aria-label="Class color"
                @change="updateClassColor(item.id, $event.target.value)"
              />
            </label>
            <span>{{ item.name }}</span>
            <span v-if="classIndex < 9" class="hotkey-badge">{{ classIndex + 1 }}</span>
            <Trash2 :size="14" class="row-action" @click.stop="removeClass(item.id)" />
          </button>
          <p v-if="projectClasses.length === 0" class="empty-state">Create a class before labeling.</p>
        </div>
      </section>

      <section v-if="taskType === 'pose_estimation'" class="inspector-section">
        <div class="section-title">
          <h3>Pose</h3>
        </div>
        <button class="tool-btn full-width" type="button" :class="{ active: activeTool === 'pose' }" @click="spawnSkeleton">
          <Waypoints :size="17" />
          Spawn COCO skeleton
        </button>
        <p class="hint-text">Drag keypoints to place joints. Double-click a keypoint to toggle visibility.</p>
      </section>

      <section class="inspector-section">
        <div class="section-title">
          <h3>Annotations</h3>
          <button class="text-btn" type="button" @click="clearAnnotations">Clear</button>
        </div>
        <div class="annotation-list">
          <div
            v-for="item in annotationItems()"
            :key="`${item.type}-${item.id}`"
            :class="['annotation-row', { selected: selectedAnnotation?.id === item.id || selectedAnnotations.classId === item.id }]"
            role="button"
            tabindex="0"
            @click="item.type === 'classification' ? setClassification(item.classId) : selectAnnotation(item.type, item.id)"
            @keyup.enter="item.type === 'classification' ? setClassification(item.classId) : selectAnnotation(item.type, item.id)"
          >
            <span class="color-dot" :style="{ backgroundColor: findClass(item.classId)?.color || item.color }"></span>
            <span>{{ findClass(item.classId)?.name || 'Unknown' }}</span>
            <span class="type-chip">{{ item.type }}</span>
            <button class="row-delete" type="button" title="Delete annotation" @click.stop="deleteAnnotation(item.type, item.id)">
              <Trash2 :size="14" />
            </button>
          </div>
          <p v-if="annotationItems().length === 0 && !selectedAnnotations.null" class="empty-state">No annotations yet.</p>
        </div>
      </section>

      <section v-if="selectedDetail" class="inspector-section">
        <div class="section-title">
          <h3>Selected</h3>
        </div>
        <label class="field-label">
          Class
          <select
            :value="selectedDetail.classId"
            @change="replaceAnnotations({
              ...selectedAnnotations,
              [selectedAnnotation.type === 'bbox' ? 'bboxes' : selectedAnnotation.type === 'polygon' ? 'polygons' : 'skeletons']:
                selectedAnnotations[selectedAnnotation.type === 'bbox' ? 'bboxes' : selectedAnnotation.type === 'polygon' ? 'polygons' : 'skeletons'].map((item) => item.id === selectedDetail.id ? { ...item, classId: $event.target.value, color: findClass($event.target.value)?.color || item.color } : item)
            })"
          >
            <option v-for="item in projectClasses" :key="item.id" :value="item.id">{{ item.name }}</option>
          </select>
        </label>
      </section>

      <section class="inspector-section">
        <div class="section-title">
          <h3>Image</h3>
        </div>
        <dl class="meta-list">
          <div><dt>Status</dt><dd>{{ selectedImage?.status || '-' }}</dd></div>
          <div><dt>Size</dt><dd>{{ imageMetrics.naturalWidth || '-' }} x {{ imageMetrics.naturalHeight || '-' }}</dd></div>
          <div><dt>Tool</dt><dd>{{ activeTool }}</dd></div>
        </dl>
      </section>
    </aside>

    <div v-if="showShortcuts" class="shortcut-overlay" @click.self="showShortcuts = false">
      <div class="shortcut-panel" role="dialog" aria-label="Keyboard shortcuts">
        <div class="shortcut-head">
          <strong>Shortcuts</strong>
          <button class="text-btn" type="button" @click="showShortcuts = false">[esc]</button>
        </div>
        <dl class="shortcut-list">
          <div><dt>V</dt><dd>Select tool</dd></div>
          <div><dt>B</dt><dd>Box</dd></div>
          <div><dt>P</dt><dd>Polygon</dd></div>
          <div><dt>K</dt><dd>Pose</dd></div>
          <div><dt>1–9</dt><dd>Active class</dd></div>
          <div><dt>Space</dt><dd>Pan (hold)</dd></div>
          <div><dt>⌫</dt><dd>Drop last point · delete vertex / shape</dd></div>
          <div><dt>Ctrl+Z</dt><dd>Undo</dd></div>
          <div><dt>Ctrl+Y</dt><dd>Redo</dd></div>
          <div><dt>Esc</dt><dd>Cancel / close panel</dd></div>
          <div><dt>?</dt><dd>This panel</dd></div>
        </dl>
      </div>
    </div>
  </div>
</template>

<style scoped>
.annotation-shell {
  display: grid;
  grid-template-columns: minmax(190px, 240px) minmax(0, 1fr) minmax(230px, 280px);
  min-height: calc(100vh - 150px);
  border: 1px solid var(--border-color, #646262);
  background: var(--bg-color, #fdfcfc);
  color: var(--text-color, #201d1d);
}

button,
input,
select {
  font: inherit;
}

button {
  cursor: pointer;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

.queue-panel,
.inspector-panel {
  min-width: 0;
  display: flex;
  flex-direction: column;
  border-color: var(--border-color, #646262);
  background: var(--bg-color, #fdfcfc);
}

.queue-panel {
  border-right: 1px solid var(--border-color, #646262);
}

.inspector-panel {
  border-left: 1px solid var(--border-color, #646262);
  overflow-y: auto;
}

.panel-header,
.toolbar,
.canvas-footer,
.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.panel-header {
  justify-content: space-between;
  min-height: 48px;
  padding: 0.65rem;
  border-bottom: 1px dashed var(--border-color, #646262);
}

.icon-text-btn,
.tool-btn,
.primary-btn,
.icon-btn,
.text-btn {
  min-height: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  border: 1px solid transparent;
  border-radius: 4px;
  background: transparent;
  color: inherit;
  padding: 0.25rem 0.55rem;
  transition: background 160ms ease, color 160ms ease;
}

.icon-btn {
  width: 34px;
  padding: 0;
}

.text-btn {
  min-height: 28px;
  border: none;
  padding: 0;
  color: #646262;
}

.tool-btn:hover,
.icon-btn:hover,
.icon-text-btn:hover {
  background: var(--hover-bg);
}

.tool-btn.active,
.primary-btn,
.queue-tabs button.active {
  background: var(--text-color, #201d1d);
  color: var(--bg-color, #fdfcfc);
  border-color: var(--text-color, #201d1d);
}

.danger {
  color: #ff3b30;
}

.task-pill,
.type-chip,
.asset-status,
.zoom-readout {
  color: #646262;
  font-size: 0.75rem;
}

.queue-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  border-bottom: 1px dashed var(--border-color, #646262);
}

.queue-tabs button {
  min-height: 36px;
  border: none;
  border-right: 1px dashed var(--border-color, #646262);
  background: transparent;
  color: inherit;
}

.queue-tabs button:last-child {
  border-right: none;
}

.asset-list,
.class-list,
.annotation-list {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  padding: 0.55rem;
}

.asset-list {
  min-height: 0;
  overflow-y: auto;
  flex: 1;
}

.asset-row,
.class-row,
.annotation-row {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 0.45rem;
  border: 1px solid var(--border-color, #646262);
  background: transparent;
  color: inherit;
  padding: 0.45rem;
  text-align: left;
}

.asset-row {
  align-items: center;
}

.asset-row-footer {
  width: auto;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-left: auto;
}

.asset-row.selected,
.class-row.active,
.annotation-row.selected {
  background: #201d1d;
  color: #fdfcfc;
}

.asset-name {
  min-width: 0;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row-delete {
  width: 26px;
  height: 26px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-left: auto;
  border: 1px solid transparent;
  border-radius: 4px;
  background: transparent;
  color: #ff3b30;
}

.row-delete:hover {
  border-color: currentColor;
  background: rgba(255, 59, 48, 0.08);
}

.studio-panel {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.toolbar {
  flex-wrap: wrap;
  min-height: 52px;
  padding: 0.5rem 0.65rem;
  border-bottom: 1px solid var(--border-color, #646262);
}

.toolbar-group {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
}

.toolbar-group + .toolbar-group {
  padding-left: 0.45rem;
  border-left: 1px solid var(--hairline, rgba(15, 0, 0, 0.12));
}

.toolbar-spacer {
  flex: 1;
}

.canvas-wrap {
  min-height: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.canvas-viewport {
  position: relative;
  min-height: 520px;
  flex: 1;
  overflow: hidden;
  background:
    linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px),
    #171515;
  background-size: 32px 32px;
}

.canvas-stage {
  position: absolute;
  inset: 0;
}

.canvas-image,
.annotation-layer {
  position: absolute;
  user-select: none;
}

.canvas-image {
  object-fit: contain;
  pointer-events: none;
}

.annotation-layer {
  inset: 0;
  overflow: visible;
}

.annotation-box,
.annotation-polygon {
  fill: rgba(255, 255, 255, 0.09);
  stroke-width: 1.5;
  vector-effect: non-scaling-stroke;
  pointer-events: auto;
}

.annotation-box.selected,
.annotation-polygon.selected {
  stroke-width: 2;
}

.draft-shape,
.draft-line {
  fill: rgba(255, 255, 255, 0.06);
  stroke-width: 1.5;
  stroke-dasharray: 6;
  vector-effect: non-scaling-stroke;
  pointer-events: none;
}

.label-text {
  font-size: 12px;
  font-weight: 700;
  paint-order: stroke;
  stroke: #171515;
  stroke-width: 3px;
  vector-effect: non-scaling-stroke;
  pointer-events: auto;
}

.resize-handle,
.vertex-handle,
.keypoint {
  fill: #fdfcfc;
  stroke: #201d1d;
  stroke-width: 1.5;
  vector-effect: non-scaling-stroke;
  pointer-events: auto;
}

.keypoint.hidden {
  opacity: 0.35;
}

.vertex-selected {
  fill: var(--accent, #007aff);
}

.insert-hint circle,
.insert-hint line {
  fill: none;
  stroke: var(--text-color, #201d1d);
  stroke-width: 1.5;
  vector-effect: non-scaling-stroke;
  pointer-events: none;
}

.skeleton-edge {
  stroke-width: 2;
  vector-effect: non-scaling-stroke;
}

.skeleton-edge-hit {
  stroke: transparent;
  stroke-width: 12;
  vector-effect: non-scaling-stroke;
  pointer-events: stroke;
}

.skeleton-move-box {
  fill: transparent;
  stroke: var(--mute, #6e6e73);
  stroke-width: 1;
  stroke-dasharray: 4 3;
  vector-effect: non-scaling-stroke;
  pointer-events: auto;
}

.vertex-close {
  fill: none;
  stroke: #fdfcfc;
  stroke-width: 2;
  vector-effect: non-scaling-stroke;
  pointer-events: none;
}

.cursor-guide {
  /* difference blend inverts against any backdrop: visible on dark canvas and white image alike */
  stroke: #ffffff;
  stroke-dasharray: 4 5;
  stroke-width: 1;
  mix-blend-mode: difference;
  vector-effect: non-scaling-stroke;
  pointer-events: none;
}

.null-banner,
.crosshair-hint {
  position: absolute;
  left: 1rem;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border: 1px solid rgba(255,255,255,0.2);
  border-radius: 4px;
  background: rgba(32, 29, 29, 0.84);
  color: #fdfcfc;
  padding: 0.45rem 0.65rem;
}

.null-banner {
  top: 1rem;
}

.crosshair-hint {
  bottom: 1rem;
}

.canvas-footer {
  min-height: 36px;
  justify-content: space-between;
  padding: 0.35rem 0.65rem;
  border-top: 1px solid var(--border-color, #646262);
  color: #646262;
  font-size: 0.8rem;
}

.inspector-section {
  padding: 0.75rem;
  border-bottom: 1px dashed var(--border-color, #646262);
}

.section-title {
  justify-content: space-between;
  margin-bottom: 0.55rem;
}

.section-title h3 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
}

.add-class {
  display: flex;
  gap: 0.35rem;
}

.add-class input,
.field-label select {
  min-width: 0;
  width: 100%;
  border: 1px solid var(--border-color, #646262);
  border-radius: 4px;
  background: #f8f7f7;
  color: inherit;
  padding: 0.45rem;
}

.class-row,
.annotation-row {
  justify-content: flex-start;
}

.row-action {
  margin-left: auto;
}

.color-dot {
  width: 12px;
  height: 12px;
  flex: 0 0 12px;
  border: 1px solid currentColor;
  border-radius: 999px;
  pointer-events: none;
}

.color-dot-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  flex: 0 0 20px;
  cursor: pointer;
}

.color-input {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  border: none;
  padding: 0;
  cursor: pointer;
}

.full-width {
  width: 100%;
}

.hint-text,
.empty-state {
  color: #646262;
  font-size: 0.82rem;
  line-height: 1.45;
}

.empty-state {
  margin: 0;
  padding: 0.4rem 0;
}

.field-label {
  display: grid;
  gap: 0.35rem;
  color: #646262;
  font-size: 0.8rem;
}

.meta-list {
  display: grid;
  gap: 0.45rem;
  margin: 0;
}

.meta-list div {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.meta-list dt,
.meta-list dd {
  margin: 0;
}

.meta-list dt {
  color: #646262;
}

.empty-canvas {
  flex: 1;
  display: grid;
  place-items: center;
  color: #646262;
}

.error-text {
  color: #ff3b30;
}

.queue-search-wrap {
  padding: 0.45rem;
  border-bottom: 1px dashed var(--border-color, #646262);
}

.queue-search {
  width: 100%;
  box-sizing: border-box;
  min-height: 30px;
  border: 1px solid var(--border-color, #646262);
  border-radius: 4px;
  background: var(--surface-soft, #f8f7f7);
  color: inherit;
  padding: 0.3rem 0.45rem;
  font: inherit;
}

.queue-thumb {
  width: 36px;
  height: 36px;
  flex: 0 0 36px;
  object-fit: cover;
  border-radius: 4px;
  background: var(--surface-soft, #f8f7f7);
}

.hotkey-badge {
  margin-left: 0.35rem;
  padding: 0 0.3rem;
  min-width: 16px;
  border: 1px solid var(--hairline, rgba(15, 0, 0, 0.12));
  border-radius: 4px;
  font-size: 0.7rem;
  color: var(--mute, #6e6e73);
  text-align: center;
}

.shortcut-overlay {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal, 1000);
  display: grid;
  place-items: center;
  background: rgba(32, 29, 29, 0.5);
  padding: 1rem;
}

.shortcut-panel {
  width: min(420px, 92vw);
  max-height: 86vh;
  overflow-y: auto;
  background: var(--bg-color, #fdfcfc);
  border: 1px solid var(--border-color, #646262);
  border-radius: 4px;
  padding: 1rem;
}

.shortcut-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px dashed var(--border-color, #646262);
}

.shortcut-list {
  display: grid;
  gap: 0.4rem;
  margin: 0;
}

.shortcut-list div {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
}

.shortcut-list dt {
  flex: 0 0 64px;
  margin: 0;
  color: var(--mute, #6e6e73);
}

.shortcut-list dd {
  margin: 0;
}

@media (max-width: 1024px) {
  .annotation-shell {
    grid-template-columns: minmax(160px, 210px) minmax(0, 1fr);
  }

  .inspector-panel {
    grid-column: 1 / -1;
    border-top: 1px solid var(--border-color, #646262);
    border-left: none;
    max-height: 280px;
  }
}

@media (max-width: 720px) {
  .annotation-shell {
    grid-template-columns: 1fr;
  }

  .queue-panel {
    border-right: none;
    border-bottom: 1px solid var(--border-color, #646262);
  }

  .asset-list {
    max-height: 160px;
    overflow-y: auto;
  }

  .canvas-viewport {
    min-height: 420px;
  }
}
</style>
