import assert from 'node:assert/strict'
import { test } from 'node:test'

import {
  COCO_KEYPOINTS,
  clampBox,
  createEmptyAnnotations,
  createPoseSkeleton,
  getContainedImageRect,
  getTaskTools,
  isAnnotationComplete,
  pointerToImagePoint
} from '../src/utils/annotationGeometry.js'

test('maps viewport pointer coordinates into natural image pixels', () => {
  const imageRect = getContainedImageRect({
    viewportWidth: 1000,
    viewportHeight: 500,
    naturalWidth: 400,
    naturalHeight: 400
  })

  assert.deepEqual(imageRect, {
    x: 250,
    y: 0,
    width: 500,
    height: 500,
    scale: 1.25
  })

  assert.deepEqual(
    pointerToImagePoint({
      clientX: 630,
      clientY: 250,
      containerRect: { left: 10, top: 20 },
      pan: { x: 5, y: -10 },
      zoom: 2,
      imageRect,
      naturalWidth: 400,
      naturalHeight: 400
    }),
    { x: 46, y: 96 }
  )
})

test('creates task-specific empty annotation containers', () => {
  assert.deepEqual(createEmptyAnnotations('classification'), { classId: '', null: false })
  assert.deepEqual(createEmptyAnnotations('object_detection'), { bboxes: [], null: false })
  assert.deepEqual(createEmptyAnnotations('segmentation'), { polygons: [], null: false })
  assert.deepEqual(createEmptyAnnotations('pose_estimation'), { skeletons: [], null: false })
})

test('detects whether an asset has usable annotations for each task type', () => {
  assert.equal(isAnnotationComplete('classification', { classId: 'person' }), true)
  assert.equal(isAnnotationComplete('object_detection', { bboxes: [{ id: 'a' }] }), true)
  assert.equal(isAnnotationComplete('segmentation', { polygons: [{ id: 'a' }] }), true)
  assert.equal(isAnnotationComplete('pose_estimation', { skeletons: [{ id: 'a' }] }), true)
  assert.equal(isAnnotationComplete('object_detection', { null: true }), true)
  assert.equal(isAnnotationComplete('classification', { classId: '' }), false)
})

test('creates centered COCO skeletons with stable keypoint names', () => {
  const skeleton = createPoseSkeleton({
    id: 'skeleton-1',
    classId: 'person',
    color: '#007aff',
    center: { x: 320, y: 240 }
  })

  assert.equal(skeleton.id, 'skeleton-1')
  assert.equal(skeleton.classId, 'person')
  assert.equal(skeleton.keypoints.length, 17)
  assert.deepEqual(skeleton.keypoints.map((point) => point.name), COCO_KEYPOINTS)
  assert.equal(skeleton.keypoints.every((point) => point.visible === true), true)
})

test('clamps boxes to image bounds and drops tiny boxes', () => {
  assert.deepEqual(
    clampBox({ x: -10, y: 5, width: 40, height: 30 }, 100, 80),
    { x: 0, y: 5, width: 30, height: 30 }
  )
  assert.equal(clampBox({ x: 10, y: 10, width: 2, height: 3 }, 100, 80), null)
})

test('returns task-aware toolbar tool ids', () => {
  assert.deepEqual(getTaskTools('classification').map((tool) => tool.id), ['select'])
  assert.deepEqual(getTaskTools('object_detection').map((tool) => tool.id), ['select', 'bbox'])
  assert.deepEqual(getTaskTools('segmentation').map((tool) => tool.id), ['select', 'polygon'])
  assert.deepEqual(getTaskTools('pose_estimation').map((tool) => tool.id), ['select', 'pose'])
})
