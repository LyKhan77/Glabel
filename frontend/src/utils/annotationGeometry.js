export const COCO_KEYPOINTS = [
  'nose',
  'left_eye',
  'right_eye',
  'left_ear',
  'right_ear',
  'left_shoulder',
  'right_shoulder',
  'left_elbow',
  'right_elbow',
  'left_wrist',
  'right_wrist',
  'left_hip',
  'right_hip',
  'left_knee',
  'right_knee',
  'left_ankle',
  'right_ankle'
]

export const COCO_EDGES = [
  [15, 13],
  [13, 11],
  [16, 14],
  [14, 12],
  [11, 12],
  [5, 11],
  [6, 12],
  [5, 6],
  [5, 7],
  [6, 8],
  [7, 9],
  [8, 10],
  [1, 2],
  [0, 1],
  [0, 2],
  [1, 3],
  [2, 4],
  [3, 5],
  [4, 6]
]

export const TASK_LABELS = {
  classification: 'Classification',
  object_detection: 'Object Detection',
  segmentation: 'Segmentation',
  pose_estimation: 'Pose Estimation'
}

export function getTaskTools(taskType) {
  const selectTool = { id: 'select', label: 'Select', shortcut: 'V' }
  if (taskType === 'object_detection') return [selectTool, { id: 'bbox', label: 'Box', shortcut: 'B' }]
  if (taskType === 'segmentation') return [selectTool, { id: 'polygon', label: 'Polygon', shortcut: 'P' }]
  if (taskType === 'pose_estimation') return [selectTool, { id: 'pose', label: 'Pose', shortcut: 'K' }]
  return [selectTool]
}

export function createEmptyAnnotations(taskType) {
  if (taskType === 'classification') return { classId: '', null: false }
  if (taskType === 'object_detection') return { bboxes: [], null: false }
  if (taskType === 'segmentation') return { polygons: [], null: false }
  if (taskType === 'pose_estimation') return { skeletons: [], null: false }
  return { null: false }
}

export function normalizeAnnotations(taskType, annotations = {}) {
  return { ...createEmptyAnnotations(taskType), ...(annotations || {}) }
}

export function isAnnotationComplete(taskType, annotations = {}) {
  if (annotations?.null) return true
  if (taskType === 'classification') return Boolean(annotations.classId)
  if (taskType === 'object_detection') return Boolean(annotations.bboxes?.length)
  if (taskType === 'segmentation') return Boolean(annotations.polygons?.length)
  if (taskType === 'pose_estimation') return Boolean(annotations.skeletons?.length)
  return false
}

export function getContainedImageRect({ viewportWidth, viewportHeight, naturalWidth, naturalHeight }) {
  if (!viewportWidth || !viewportHeight || !naturalWidth || !naturalHeight) {
    return { x: 0, y: 0, width: 0, height: 0, scale: 1 }
  }
  const scale = Math.min(viewportWidth / naturalWidth, viewportHeight / naturalHeight)
  const width = naturalWidth * scale
  const height = naturalHeight * scale
  return {
    x: (viewportWidth - width) / 2,
    y: (viewportHeight - height) / 2,
    width,
    height,
    scale
  }
}

export function pointerToImagePoint({
  clientX,
  clientY,
  containerRect,
  pan,
  zoom,
  imageRect,
  naturalWidth,
  naturalHeight
}) {
  const viewportX = (clientX - containerRect.left - pan.x) / zoom
  const viewportY = (clientY - containerRect.top - pan.y) / zoom
  const imageX = (viewportX - imageRect.x) / imageRect.scale
  const imageY = (viewportY - imageRect.y) / imageRect.scale

  return {
    x: clamp(Math.round(imageX), 0, naturalWidth),
    y: clamp(Math.round(imageY), 0, naturalHeight)
  }
}

export function clampBox(box, naturalWidth, naturalHeight, minSize = 5) {
  const x1 = clamp(box.x, 0, naturalWidth)
  const y1 = clamp(box.y, 0, naturalHeight)
  const x2 = clamp(box.x + box.width, 0, naturalWidth)
  const y2 = clamp(box.y + box.height, 0, naturalHeight)
  const normalized = {
    x: Math.min(x1, x2),
    y: Math.min(y1, y2),
    width: Math.abs(x2 - x1),
    height: Math.abs(y2 - y1)
  }
  if (normalized.width < minSize || normalized.height < minSize) return null
  return normalized
}

export function createPoseSkeleton({ id, classId, color, center }) {
  const layout = [
    [0, -72],
    [-18, -82],
    [18, -82],
    [-34, -72],
    [34, -72],
    [-48, -28],
    [48, -28],
    [-70, 28],
    [70, 28],
    [-78, 84],
    [78, 84],
    [-34, 54],
    [34, 54],
    [-36, 124],
    [36, 124],
    [-38, 192],
    [38, 192]
  ]

  return {
    id,
    classId,
    color,
    keypoints: COCO_KEYPOINTS.map((name, index) => ({
      name,
      x: Math.round(center.x + layout[index][0]),
      y: Math.round(center.y + layout[index][1]),
      visible: true
    }))
  }
}

export function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max)
}

// Nearest point on segment ab to p, with projection param t (0..1) and distance.
export function pointOnSegment(p, a, b) {
  const dx = b.x - a.x
  const dy = b.y - a.y
  const lenSq = dx * dx + dy * dy
  let t = lenSq === 0 ? 0 : ((p.x - a.x) * dx + (p.y - a.y) * dy) / lenSq
  t = clamp(t, 0, 1)
  const x = a.x + t * dx
  const y = a.y + t * dy
  return { x, y, t, dist: Math.hypot(p.x - x, p.y - y) }
}
