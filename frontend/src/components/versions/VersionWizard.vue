<template>
  <div class="wizard-container">
    <!-- Header -->
    <div class="wizard-header">
      <div 
        v-for="(stepName, i) in steps" 
        :key="i"
        class="step-indicator"
        :class="{ active: currentStep === i + 1, completed: currentStep > i + 1 }"
        @click="currentStep > i + 1 ? currentStep = i + 1 : null"
      >
        <span class="bracket" v-if="currentStep === i + 1">[</span><span class="bracket" v-else-if="currentStep > i + 1">[x]</span><span class="bracket" v-else>[ ]</span>
        <span class="step-label">{{ stepName }}</span>
        <span class="separator" v-if="i < steps.length - 1">·</span>
      </div>
    </div>

    <!-- Step 1: Split -->
    <div v-if="currentStep === 1" class="step-content">
      <div class="step-title-block">
        <h3>Dataset Split</h3>
        <p>Divide your annotated images into training, validation, and testing sets.</p>
      </div>
      
      <SplitBar :train="splitTrain" :valid="splitValid" :test="splitTest" class="split-visualizer" />
      
      <div class="split-inputs">
        <div class="input-group">
          <label>Train (%)</label>
          <div class="slider-row">
            <input type="range" v-model.number="splitTrain" min="0" max="100" class="split-slider" />
            <input type="number" v-model.number="splitTrain" min="0" max="100" class="text-input small" />
          </div>
        </div>
        <div class="input-group">
          <label>Validation (%)</label>
          <div class="slider-row">
            <input type="range" v-model.number="splitValid" min="0" max="100" class="split-slider" />
            <input type="number" v-model.number="splitValid" min="0" max="100" class="text-input small" />
          </div>
        </div>
        <div class="input-group">
          <label>Test (%)</label>
          <div class="slider-row">
            <input type="range" v-model.number="splitTest" min="0" max="100" class="split-slider" />
            <input type="number" v-model.number="splitTest" min="0" max="100" class="text-input small" />
          </div>
        </div>
      </div>
    </div>

    <!-- Step 2: Preprocessing -->
    <div v-else-if="currentStep === 2" class="step-content">
      <div class="step-title-block">
        <h3>Preprocessing</h3>
        <p>Applied to all images before augmentation.</p>
      </div>
      
      <div class="options-list">
        <div v-for="(prep, idx) in preprocessingOptions" :key="prep.key" class="option-row" :class="{ active: prep.enabled }">
          <div class="option-header" @click="prep.enabled = !prep.enabled" :title="hoverTips[prep.key]">
            <span class="bracket">{{ prep.enabled ? '[x]' : '[ ]' }}</span>
            <label class="option-label" :title="hoverTips[prep.key]">
              {{ prep.key.replace('_', ' ') }}
              <span class="help-icon" :title="hoverTips[prep.key]">[?]</span>
            </label>
          </div>
          <div v-if="prep.enabled && Object.keys(prep.params).length > 0" class="option-params">
            <div v-for="(val, pKey) in prep.params" :key="pKey" class="input-group row-input">
              <label>{{ pKey }}</label>
              <input type="number" v-model.number="prep.params[pKey]" class="text-input small" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 3: Augmentations -->
    <div v-else-if="currentStep === 3" class="step-content">
      <div class="step-title-row">
        <div class="step-title-block">
          <h3>Augmentations</h3>
          <p>Generate multiple variations of each training image.</p>
        </div>
        <div class="mode-tabs">
          <button 
            @click="augmentationMode = 'basic'" 
            class="tab-btn"
            :class="{ active: augmentationMode === 'basic' }"
          >Basic</button>
          <button 
            @click="augmentationMode = 'advanced'" 
            class="tab-btn"
            :class="{ active: augmentationMode === 'advanced' }"
          >Advanced</button>
        </div>
      </div>

      <div v-if="augmentationMode === 'basic'" class="options-grid">
        <div 
          v-for="preset in ['light', 'medium', 'heavy']" 
          :key="preset"
          @click="setPreset(preset)"
          class="preset-card"
          :class="{ active: augmentationPreset === preset }"
        >
          <div class="preset-name">{{ preset }}</div>
          <div class="preset-desc">
            {{ preset === 'light' ? '1x images' : preset === 'medium' ? '3x images' : '5x images' }}
          </div>
        </div>
      </div>

      <div v-else class="advanced-options">
        <div class="options-list">
          <div v-for="(aug, idx) in augmentationOptions" :key="aug.key" class="option-row" :class="{ active: aug.enabled }">
            <div class="option-header-row">
              <div class="option-header" @click="aug.enabled = !aug.enabled" :title="hoverTips[aug.key]">
                <span class="bracket">{{ aug.enabled ? '[x]' : '[ ]' }}</span>
                <label class="option-label" :title="hoverTips[aug.key]">
                  {{ aug.key.replace('_', ' ') }}
                  <span class="help-icon" :title="hoverTips[aug.key]">[?]</span>
                </label>
              </div>
              <button v-if="aug.enabled" @click="openPreview(aug)" class="preview-btn">
                [ Preview ]
              </button>
            </div>
          </div>
        </div>
        
        <div class="multiplier-row">
          <label>Output Multiplier:</label>
          <input type="number" v-model.number="multiplier" min="1" max="10" class="text-input small" />
          <span class="multiplier-hint">Generate {{ multiplier }} versions per training image</span>
        </div>
      </div>
    </div>

    <!-- Step 4: Summary -->
    <div v-else-if="currentStep === 4" class="step-content">
      <div class="step-title-block">
        <h3>Summary & Generation</h3>
        <p>Review your settings and name this version.</p>
      </div>
      
      <div class="summary-inputs">
        <div class="input-group">
          <label>Version Name</label>
          <input type="text" v-model="name" placeholder="e.g. v1-baseline" class="text-input" />
        </div>
        <div class="input-group">
          <label>Description</label>
          <textarea v-model="description" rows="2" placeholder="Optional notes about this version" class="text-input textarea"></textarea>
        </div>
      </div>

      <div class="summary-box">
        <div class="summary-row">
          <span class="summary-key">Split (T/V/T):</span>
          <span class="summary-val">{{ splitTrain }}% / {{ splitValid }}% / {{ splitTest }}%</span>
        </div>
        <div class="summary-row">
          <span class="summary-key">Preprocessing:</span>
          <span class="summary-val">{{ activePreprocessing.length }} steps applied</span>
        </div>
        <div class="summary-row">
          <span class="summary-key">Augmentations:</span>
          <span class="summary-val" v-if="augmentationMode === 'basic'">Basic ({{ augmentationPreset }})</span>
          <span class="summary-val" v-else>{{ activeAugmentations.length }} methods applied</span>
        </div>
        <div class="summary-row">
          <span class="summary-key">Total Output (Est):</span>
          <span class="summary-val">{{ Math.floor(annotatedCount * (splitTrain/100) * multiplier) }} training images</span>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="wizard-footer">
      <button @click="$emit('cancel')" class="btn-secondary">Cancel</button>
      <div class="footer-actions">
        <button v-if="currentStep > 1" @click="currentStep--" class="btn-secondary">Back</button>
        <button v-if="currentStep < 4" @click="nextStep" :disabled="currentStep === 1 && splitError" class="btn-primary">Next</button>
        <button v-if="currentStep === 4" @click="generate" :disabled="!name" class="btn-primary">Generate</button>
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
import { ref, computed, watch } from 'vue'
import SplitBar from './SplitBar.vue'
import AugmentationPreview from './AugmentationPreview.vue'

const props = defineProps({
  annotatedCount: { type: Number, default: 0 },
  existingVersionCount: { type: Number, default: 0 },
  projectId: { type: String, required: true }
})

const emit = defineEmits(['generate', 'cancel'])

const hoverTips = {
  auto_orient: 'Fixes image orientation based on EXIF data. Required for mobile uploads to prevent sideways images.',
  resize: 'Resizes all images to 640x640 (standard for YOLO). Recommended to reduce training memory.',
  grayscale: 'Converts images to single-channel black and white. Useful if color is irrelevant to your classes.',
  auto_contrast: 'Automatically adjusts contrast to maximize dynamic range using histogram equalization.',
  filter_null: 'Removes images that lack any bounding box or polygon annotations to prevent background bias.',
  flip_horizontal: 'Mirrors images horizontally. Useful for symmetric objects like cars or faces.',
  flip_vertical: 'Mirrors images vertically. Use only if upside-down orientations occur in the real world.',
  rotation: 'Rotates images randomly up to the specified degrees to improve model rotational invariance.',
  brightness: 'Adjusts brightness up or down randomly. Helps the model generalize to different lighting conditions.',
  blur: 'Applies Gaussian blur to reduce sharp details. Simulates out-of-focus camera conditions.',
  noise: 'Adds random salt and pepper noise. Forces the model to learn robust features instead of exact pixels.',
  cutout: 'Adds random black boxes to obscure parts of the image, simulating object occlusion.',
  hsv_shift: 'Randomly shifts Hue, Saturation, and Value. Highly recommended for robustness against color variations.'
}

const steps = ['Split', 'Preprocessing', 'Augmentations', 'Summary']
const currentStep = ref(1)

const splitTrain = ref(70)
const splitValid = ref(20)
const splitTest = ref(10)

watch(splitTrain, (newVal) => {
  let remainder = 100 - newVal
  if (splitValid.value > remainder) {
    splitValid.value = remainder
  }
  splitTest.value = 100 - splitTrain.value - splitValid.value
})

watch(splitValid, (newVal) => {
  let remainder = 100 - newVal
  if (splitTrain.value > remainder) {
    splitTrain.value = remainder
  }
  splitTest.value = 100 - splitTrain.value - splitValid.value
})

watch(splitTest, (newVal) => {
  let remainder = 100 - newVal
  if (splitTrain.value > remainder) {
    splitTrain.value = remainder
  }
  splitValid.value = 100 - splitTrain.value - splitTest.value
})

const splitError = computed(() => null) // Removed as auto-adjust guarantees 100%

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

<style scoped>
.wizard-container {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.wizard-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--hairline);
}

.step-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.9rem;
  color: var(--mute);
}

.step-indicator.completed {
  cursor: pointer;
  color: var(--text-color);
}

.step-indicator.completed:hover {
  text-decoration: underline;
}

.step-indicator.active {
  color: var(--text-color);
  font-weight: 500;
}

.bracket {
  opacity: 0.7;
}

.separator {
  color: var(--hairline);
  margin-left: 8px;
}

.step-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.step-title-block h3 {
  margin: 0 0 4px 0;
  font-size: 1.1rem;
  font-weight: 700;
}

.step-title-block p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--mute);
}

.split-visualizer {
  margin: 16px 0;
}

.split-inputs {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.slider-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.split-slider {
  flex-grow: 1;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  font-size: 0.9rem;
  font-weight: 500;
}

.text-input {
  background: var(--surface-soft);
  color: var(--text-color);
  border: 1px solid var(--hairline);
  border-radius: 4px;
  padding: 8px 12px;
  font-family: inherit;
  font-size: 0.9rem;
}

.text-input:focus {
  background: var(--bg-color);
  border-color: var(--text-color);
  outline: none;
}

.text-input.small {
  padding: 4px 8px;
  width: 80px;
}

.textarea {
  resize: vertical;
}

.error-text {
  color: var(--danger);
  font-size: 0.9rem;
  margin-top: 8px;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-row {
  border: 1px solid var(--hairline);
  border-radius: 4px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-row.active {
  background: var(--hover-bg);
}

.option-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.option-header {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: 500;
  text-transform: capitalize;
}

.option-label {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}

.help-icon {
  font-family: 'Berkeley Mono', monospace;
  font-size: 0.8rem;
  color: var(--mute);
  cursor: help;
}

.help-icon:hover {
  color: var(--text-color);
}

.option-params {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding-left: 28px;
}

.row-input {
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

.row-input label {
  text-transform: capitalize;
  font-size: 0.85rem;
  color: var(--body);
}

.step-title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.mode-tabs {
  display: flex;
  border: 1px solid var(--hairline);
  border-radius: 4px;
  padding: 2px;
  background: var(--surface-soft);
}

.tab-btn {
  background: transparent;
  border: none;
  color: var(--mute);
  padding: 6px 16px;
  font-family: inherit;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  border-radius: 2px;
}

.tab-btn.active {
  background: var(--bg-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.preset-card {
  border: 1px solid var(--hairline);
  border-radius: 4px;
  padding: 16px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  transition: background 0.2s;
}

.preset-card:hover {
  background: var(--hover-bg);
}

.preset-card.active {
  border-color: var(--text-color);
  background: var(--hover-bg);
}

.preset-name {
  font-weight: 500;
  text-transform: capitalize;
}

.preset-desc {
  font-size: 0.85rem;
  color: var(--mute);
}

.advanced-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.preview-btn {
  background: transparent;
  border: none;
  color: var(--text-color);
  font-family: inherit;
  font-size: 0.85rem;
  cursor: pointer;
}

.preview-btn:hover {
  text-decoration: underline;
}

.multiplier-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  font-weight: 500;
}

.multiplier-hint {
  font-size: 0.85rem;
  color: var(--mute);
  font-weight: 400;
}

.summary-inputs {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.summary-box {
  background: var(--surface-soft);
  border: 1px solid var(--hairline);
  border-radius: 4px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
  font-size: 0.9rem;
}

.summary-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.summary-key {
  color: var(--mute);
}

.summary-val {
  font-weight: 500;
}

.wizard-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--hairline);
}

.footer-actions {
  display: flex;
  gap: 12px;
}

.btn-primary {
  background: var(--text-color);
  color: var(--bg-color);
  border: none;
  border-radius: 4px;
  padding: 8px 20px;
  font-family: inherit;
  font-weight: 500;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: transparent;
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 8px 20px;
  font-family: inherit;
  font-weight: 500;
  cursor: pointer;
}

.btn-secondary:hover {
  background: var(--hover-bg);
}
</style>
