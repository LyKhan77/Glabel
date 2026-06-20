<template>
  <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
    <div class="bg-white rounded-xl shadow-2xl w-[900px] max-w-[95vw] max-h-[90vh] flex flex-col overflow-hidden">
      <div class="px-6 py-4 border-b flex justify-between items-center bg-gray-50">
        <h3 class="text-lg font-semibold">Preview: {{ augmentationKey }}</h3>
        <button @click="$emit('close')" class="text-gray-500 hover:text-gray-700">
          <XIcon class="w-5 h-5" />
        </button>
      </div>
      
      <div class="p-6 flex-1 overflow-y-auto flex flex-col gap-6">
        <div class="grid grid-cols-2 gap-4">
          <!-- Original -->
          <div class="flex flex-col gap-2">
            <span class="text-sm font-medium text-gray-700">Original</span>
            <div class="bg-gray-100 rounded-lg aspect-video flex items-center justify-center overflow-hidden border">
              <img v-if="originalUrl" :src="originalUrl" class="w-full h-full object-contain" />
              <div v-else class="text-gray-400">Loading...</div>
            </div>
          </div>
          <!-- Preview -->
          <div class="flex flex-col gap-2">
            <span class="text-sm font-medium text-gray-700">Preview</span>
            <div class="bg-gray-100 rounded-lg aspect-video flex items-center justify-center overflow-hidden border relative">
              <img v-if="previewUrl" :src="previewUrl" class="w-full h-full object-contain" />
              <div v-if="loadingPreview" class="absolute inset-0 bg-white/50 flex items-center justify-center">
                <span class="text-gray-800 font-medium bg-white px-3 py-1 rounded shadow">Loading...</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Controls -->
        <div class="bg-gray-50 p-4 rounded-lg border">
          <div class="flex justify-between items-center mb-4">
            <h4 class="font-medium">Parameters</h4>
            <button @click="fetchPreview" class="text-sm px-3 py-1 bg-white border rounded hover:bg-gray-50">
              Regenerate (Random Preview)
            </button>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="(val, key) in localParams" :key="key" class="flex flex-col gap-1">
              <label class="text-sm text-gray-600 capitalize flex justify-between">
                <span>{{ key.replace('_', ' ') }}</span>
                <span class="font-mono">{{ localParams[key] }}</span>
              </label>
              <input 
                type="range" 
                v-model.number="localParams[key]" 
                :min="getMin(key)" 
                :max="getMax(key)" 
                :step="getStep(key)"
                @input="onParamChange"
                class="w-full"
              />
            </div>
          </div>
        </div>
      </div>
      
      <div class="px-6 py-4 border-t bg-gray-50 flex justify-end gap-3">
        <button @click="$emit('close')" class="px-4 py-2 border rounded-lg text-sm font-medium hover:bg-gray-100">
          Cancel
        </button>
        <button @click="apply" class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700">
          Apply
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { X as XIcon } from 'lucide-vue-next'
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
})

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
