<template>
  <div class="bg-white rounded-xl shadow border p-6 flex flex-col gap-6">
    <!-- Header -->
    <div class="flex items-center gap-2 text-sm font-medium mb-4">
      <div 
        v-for="(stepName, i) in steps" 
        :key="i"
        class="flex items-center gap-2"
        :class="currentStep === i + 1 ? 'text-blue-600' : (currentStep > i + 1 ? 'text-gray-800 cursor-pointer hover:text-blue-600' : 'text-gray-400')"
        @click="currentStep > i + 1 ? currentStep = i + 1 : null"
      >
        <div class="w-6 h-6 rounded-full flex items-center justify-center border" 
             :class="currentStep === i + 1 ? 'border-blue-600 bg-blue-50' : (currentStep > i + 1 ? 'border-gray-800' : 'border-gray-300')">
          {{ i + 1 }}
        </div>
        <span>{{ stepName }}</span>
        <ChevronRightIcon v-if="i < steps.length - 1" class="w-4 h-4 text-gray-300" />
      </div>
    </div>

    <!-- Step 1: Split -->
    <div v-if="currentStep === 1" class="flex flex-col gap-6">
      <div>
        <h3 class="text-lg font-semibold mb-1">Dataset Split</h3>
        <p class="text-sm text-gray-500">Divide your annotated images into training, validation, and testing sets.</p>
      </div>
      
      <SplitBar :train="splitTrain" :valid="splitValid" :test="splitTest" class="my-4" />
      
      <div class="grid grid-cols-3 gap-6">
        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium">Train (%)</label>
          <input type="number" v-model.number="splitTrain" class="border rounded px-3 py-2" />
        </div>
        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium">Validation (%)</label>
          <input type="number" v-model.number="splitValid" class="border rounded px-3 py-2" />
        </div>
        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium">Test (%)</label>
          <input type="number" v-model.number="splitTest" class="border rounded px-3 py-2" />
        </div>
      </div>
      <div v-if="splitError" class="text-red-500 text-sm mt-2">{{ splitError }}</div>
    </div>

    <!-- Step 2: Preprocessing -->
    <div v-else-if="currentStep === 2" class="flex flex-col gap-6">
      <div>
        <h3 class="text-lg font-semibold mb-1">Preprocessing</h3>
        <p class="text-sm text-gray-500">Applied to all images before augmentation.</p>
      </div>
      
      <div class="flex flex-col gap-4">
        <div v-for="(prep, idx) in preprocessingOptions" :key="prep.key" class="border rounded-lg p-4 flex flex-col gap-3">
          <div class="flex items-center gap-3">
            <input type="checkbox" v-model="prep.enabled" :id="'prep-'+idx" class="w-4 h-4 text-blue-600 rounded" />
            <label :for="'prep-'+idx" class="font-medium capitalize cursor-pointer flex-1">
              {{ prep.key.replace('_', ' ') }}
            </label>
          </div>
          <div v-if="prep.enabled && Object.keys(prep.params).length > 0" class="pl-7 grid grid-cols-2 gap-4">
            <div v-for="(val, pKey) in prep.params" :key="pKey" class="flex flex-col gap-1">
              <label class="text-sm text-gray-600 capitalize">{{ pKey }}</label>
              <input type="number" v-model.number="prep.params[pKey]" class="border rounded px-2 py-1 text-sm" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 3: Augmentations -->
    <div v-else-if="currentStep === 3" class="flex flex-col gap-6">
      <div class="flex justify-between items-start">
        <div>
          <h3 class="text-lg font-semibold mb-1">Augmentations</h3>
          <p class="text-sm text-gray-500">Generate multiple variations of each training image.</p>
        </div>
        <div class="flex bg-gray-100 p-1 rounded-lg">
          <button 
            @click="augmentationMode = 'basic'" 
            class="px-4 py-1.5 text-sm font-medium rounded-md transition-shadow"
            :class="augmentationMode === 'basic' ? 'bg-white shadow text-gray-900' : 'text-gray-500 hover:text-gray-700'"
          >Basic</button>
          <button 
            @click="augmentationMode = 'advanced'" 
            class="px-4 py-1.5 text-sm font-medium rounded-md transition-shadow"
            :class="augmentationMode === 'advanced' ? 'bg-white shadow text-gray-900' : 'text-gray-500 hover:text-gray-700'"
          >Advanced</button>
        </div>
      </div>

      <div v-if="augmentationMode === 'basic'" class="flex flex-col gap-4">
        <div class="grid grid-cols-3 gap-4">
          <div 
            v-for="preset in ['light', 'medium', 'heavy']" 
            :key="preset"
            @click="setPreset(preset)"
            class="border rounded-lg p-4 cursor-pointer flex flex-col items-center gap-2 transition-colors hover:border-blue-300"
            :class="augmentationPreset === preset ? 'border-blue-600 bg-blue-50 ring-1 ring-blue-600' : 'border-gray-200'"
          >
            <div class="capitalize font-medium">{{ preset }}</div>
            <div class="text-sm text-gray-500">
              {{ preset === 'light' ? '1x images' : preset === 'medium' ? '3x images' : '5x images' }}
            </div>
          </div>
        </div>
      </div>

      <div v-else class="flex flex-col gap-4">
        <div v-for="(aug, idx) in augmentationOptions" :key="aug.key" class="border rounded-lg p-4 flex flex-col gap-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <input type="checkbox" v-model="aug.enabled" :id="'aug-'+idx" class="w-4 h-4 text-blue-600 rounded" />
              <label :for="'aug-'+idx" class="font-medium capitalize cursor-pointer">
                {{ aug.key.replace('_', ' ') }}
              </label>
            </div>
            <button v-if="aug.enabled" @click="openPreview(aug)" class="text-sm text-blue-600 hover:text-blue-800 px-3 py-1 bg-blue-50 rounded transition-colors">
              Preview
            </button>
          </div>
        </div>
        
        <div class="mt-4 flex items-center gap-4">
          <label class="font-medium">Output Multiplier</label>
          <input type="number" v-model.number="multiplier" min="1" max="10" class="border rounded px-3 py-2 w-24" />
          <span class="text-sm text-gray-500">Generate {{ multiplier }} versions per training image</span>
        </div>
      </div>
    </div>

    <!-- Step 4: Summary -->
    <div v-else-if="currentStep === 4" class="flex flex-col gap-6">
      <div>
        <h3 class="text-lg font-semibold mb-1">Summary & Generation</h3>
        <p class="text-sm text-gray-500">Review your settings and name this version.</p>
      </div>
      
      <div class="flex flex-col gap-4">
        <div class="flex flex-col gap-2">
          <label class="font-medium">Version Name</label>
          <input type="text" v-model="name" placeholder="e.g. v1-baseline" class="border rounded px-3 py-2" />
        </div>
        <div class="flex flex-col gap-2">
          <label class="font-medium">Description</label>
          <textarea v-model="description" rows="2" placeholder="Optional notes about this version" class="border rounded px-3 py-2"></textarea>
        </div>
      </div>

      <div class="bg-gray-50 border rounded-lg p-4 flex flex-col gap-3 mt-2 text-sm">
        <div class="grid grid-cols-2">
          <span class="text-gray-500">Split (T/V/T):</span>
          <span class="font-medium">{{ splitTrain }}% / {{ splitValid }}% / {{ splitTest }}%</span>
        </div>
        <div class="grid grid-cols-2">
          <span class="text-gray-500">Preprocessing:</span>
          <span class="font-medium">{{ activePreprocessing.length }} steps applied</span>
        </div>
        <div class="grid grid-cols-2">
          <span class="text-gray-500">Augmentations:</span>
          <span class="font-medium" v-if="augmentationMode === 'basic'">Basic ({{ augmentationPreset }})</span>
          <span class="font-medium" v-else>{{ activeAugmentations.length }} methods applied</span>
        </div>
        <div class="grid grid-cols-2">
          <span class="text-gray-500">Total Output (Est):</span>
          <span class="font-medium">{{ Math.floor(annotatedCount * (splitTrain/100) * multiplier) }} training images</span>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="flex justify-between mt-4 pt-4 border-t">
      <button @click="$emit('cancel')" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg font-medium transition-colors">Cancel</button>
      <div class="flex gap-3">
        <button v-if="currentStep > 1" @click="currentStep--" class="px-4 py-2 border rounded-lg font-medium hover:bg-gray-50 transition-colors">Back</button>
        <button v-if="currentStep < 4" @click="nextStep" :disabled="currentStep === 1 && splitError" class="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors">Next</button>
        <button v-if="currentStep === 4" @click="generate" :disabled="!name" class="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 transition-colors">Generate</button>
      </div>
    </div>

    <AugmentationPreview 
      v-if="previewAug"
      :visible="!!previewAug"
      :projectId="projectId"
      :augmentationKey="previewAug.key"
      :params="previewAug.params"
      @update:params="updatePreviewParams"
      @close="previewAug = null"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ChevronRight as ChevronRightIcon } from 'lucide-vue-next'
import SplitBar from './SplitBar.vue'
import AugmentationPreview from './AugmentationPreview.vue'

const props = defineProps({
  annotatedCount: { type: Number, default: 0 },
  existingVersionCount: { type: Number, default: 0 },
  projectId: { type: String, required: true }
})

const emit = defineEmits(['generate', 'cancel'])

const steps = ['Split', 'Preprocessing', 'Augmentations', 'Summary']
const currentStep = ref(1)

const splitTrain = ref(70)
const splitValid = ref(20)
const splitTest = ref(10)
const splitError = computed(() => {
  if (splitTrain.value + splitValid.value + splitTest.value !== 100) {
    return 'Total split must equal 100%'
  }
  return null
})

const preprocessingOptions = ref([
  { key: 'auto_orient', enabled: true, params: {} },
  { key: 'resize', enabled: true, params: { width: 640, height: 640 } },
  { key: 'grayscale', enabled: false, params: {} },
  { key: 'auto_contrast', enabled: false, params: {} },
  { key: 'filter_null', enabled: false, params: {} }
])

const augmentationMode = ref('basic')
const augmentationPreset = ref('light')
const multiplier = ref(1)

const augmentationOptions = ref([
  { key: 'flip_horizontal', enabled: false, params: { probability: 0.5 } },
  { key: 'flip_vertical', enabled: false, params: { probability: 0.5 } },
  { key: 'rotation', enabled: false, params: { degrees: 15, probability: 0.5 } },
  { key: 'brightness', enabled: false, params: { factor: 0.2, probability: 0.5 } },
  { key: 'blur', enabled: false, params: { kernel_size: 5, probability: 0.5 } },
  { key: 'noise', enabled: false, params: { amount: 0.05, probability: 0.5 } },
  { key: 'cutout', enabled: false, params: { holes: 3, length: 20, probability: 0.5 } },
  { key: 'hsv_shift', enabled: false, params: { h: 0.015, s: 0.7, v: 0.4, probability: 0.5 } }
])

const name = ref(`v${props.existingVersionCount + 1}`)
const description = ref('')

const previewAug = ref(null)

const activePreprocessing = computed(() => preprocessingOptions.value.filter(p => p.enabled))
const activeAugmentations = computed(() => augmentationOptions.value.filter(a => a.enabled))

function setPreset(preset) {
  augmentationPreset.value = preset
  if (preset === 'light') multiplier.value = 1
  else if (preset === 'medium') multiplier.value = 3
  else if (preset === 'heavy') multiplier.value = 5
}

function nextStep() {
  if (currentStep.value === 1 && splitError.value) return
  currentStep.value++
}

function openPreview(aug) {
  previewAug.value = aug
}

function updatePreviewParams(newParams) {
  if (previewAug.value) {
    const target = augmentationOptions.value.find(a => a.key === previewAug.value.key)
    if (target) {
      target.params = newParams
    }
  }
}

function generate() {
  const payload = {
    name: name.value,
    description: description.value,
    split: {
      train: splitTrain.value,
      valid: splitValid.value,
      test: splitTest.value
    },
    preprocessing: activePreprocessing.value.map(p => ({
      key: p.key,
      params: p.params
    }))
  }
  
  if (augmentationMode.value === 'basic') {
    payload.augmentation = {
      mode: 'basic',
      preset: augmentationPreset.value,
      multiplier: multiplier.value
    }
  } else {
    payload.augmentation = {
      mode: 'advanced',
      multiplier: multiplier.value,
      steps: activeAugmentations.value.map(a => ({
        key: a.key,
        params: a.params
      }))
    }
  }
  
  emit('generate', payload)
}
</script>
