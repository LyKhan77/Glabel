<template>
  <div class="journey-container">
    <header class="header">
      <h1>Vision Solution Journey</h1>
      <button class="btn" @click="cancel">[<] Cancel</button>
    </header>

    <main class="main-content">
      <div v-if="currentStep === 1" class="step-container">
        <h2>1. Define Task</h2>
        <div class="form-group">
          <label for="taskName">Task Name</label>
          <input type="text" id="taskName" placeholder="e.g. Defect Detection" class="input-field" />
        </div>
        <div class="form-group">
          <label for="taskType">Task Type</label>
          <select id="taskType" class="input-field">
            <option value="object_detection">Object Detection</option>
            <option value="segmentation">Segmentation</option>
          </select>
        </div>
        <div class="step-actions">
          <button class="btn primary-btn" @click="currentStep = 2">[>] Start Journey</button>
        </div>
      </div>

      <div v-if="currentStep === 2" class="step-container">
        <h2>2. Data Ingestion & Annotation</h2>
        <div class="split-view">
          <div class="left-pane">
            <h3>Uploaded Images (10)</h3>
            <ul class="mock-list">
              <li>image_001.jpg</li>
              <li>image_002.jpg</li>
              <li>image_003.jpg</li>
              <li>...</li>
            </ul>
          </div>
          <div class="right-pane">
            <h3>Label Assist (SAM3)</h3>
            <p>Accelerate your labeling by using Segment Anything Model 3.</p>
            <button class="btn" @click="autoAnnotate">[Auto-Annotate via SAM3]</button>
          </div>
        </div>
        <div class="step-actions">
          <button class="btn primary-btn" @click="currentStep = 3">[>] Next: Versioning</button>
        </div>
      </div>

      <div v-if="currentStep === 3" class="step-container">
        <h2>3. Dataset Versioning & Augmentation</h2>
        <div class="form-group checkbox-group">
          <label><input type="checkbox" checked /> Resize 640x640</label>
          <label><input type="checkbox" /> Grayscale</label>
          <label><input type="checkbox" /> Flip</label>
          <label><input type="checkbox" /> Rotate</label>
        </div>
        <div class="form-group">
          <label for="multiplier">Multiplier (e.g. 3x)</label>
          <input type="text" id="multiplier" placeholder="3x" class="input-field" />
        </div>
        <div class="step-actions">
          <button class="btn primary-btn" @click="currentStep = 4">[>] Create Version & Train</button>
        </div>
      </div>

      <div v-if="currentStep === 4" class="step-container">
        <h2>4. Local Training Dashboard</h2>
        <div class="training-ui">
          <p>Status: {{ progress < 100 ? 'Training Model...' : 'Training Complete' }}</p>
          <div class="progress-bar-container">
            <div class="progress-bar" :style="{ width: progress + '%' }"></div>
          </div>
          <div class="metrics">
            <span>Progress: {{ progress }}%</span>
            <span>mAP: {{ mapScore.toFixed(2) }}</span>
          </div>
        </div>
        <div class="step-actions" v-if="progress >= 100">
          <button class="btn primary-btn" @click="openWorkspace">[🚀] Open in Playground</button>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const currentStep = ref(1)

const progress = ref(0)
const mapScore = ref(0.0)

watch(currentStep, (newStep) => {
  if (newStep === 4) {
    const interval = setInterval(() => {
      if (progress.value < 100) {
        progress.value += 10
        mapScore.value += Math.random() * 0.1
        if (mapScore.value > 0.95) mapScore.value = 0.95
      } else {
        clearInterval(interval)
      }
    }, 500)
  }
})

const cancel = () => {
  router.push('/')
}

const autoAnnotate = () => {
  alert('Mock: Annotating images...')
}

const openWorkspace = () => {
  router.push('/workspace')
}
</script>

<style scoped>
.journey-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  font-family: 'Berkeley Mono', monospace;
  background-color: #fdfcfc;
  color: #201d1d;
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  border-bottom: 1px solid #646262;
  padding-bottom: 1rem;
}

.header h1 {
  font-size: 1.5rem;
  margin: 0;
}

.btn {
  background: transparent;
  color: #201d1d;
  border: 1px solid #646262;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  font-family: 'Berkeley Mono', monospace;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn:hover {
  background: #201d1d;
  color: #fdfcfc;
}

.step-container {
  margin-top: 1rem;
}

.step-container h2 {
  font-size: 1.25rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px dashed #646262;
  padding-bottom: 0.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-field {
  padding: 0.5rem;
  font-family: 'Berkeley Mono', monospace;
  border: 1px solid #646262;
  background: transparent;
  color: #201d1d;
  border-radius: 4px;
}

.step-actions {
  margin-top: 2rem;
  display: flex;
  justify-content: flex-end;
}

.primary-btn {
  background: #201d1d;
  color: #fdfcfc;
}

.primary-btn:hover {
  background: transparent;
  color: #201d1d;
}

.split-view {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.left-pane, .right-pane {
  flex: 1;
  border: 1px solid #646262;
  padding: 1rem;
  border-radius: 4px;
}

.left-pane h3, .right-pane h3 {
  margin-top: 0;
  border-bottom: 1px dashed #646262;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}

.mock-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.mock-list li {
  padding: 0.25rem 0;
  border-bottom: 1px solid #e0e0e0;
}

.checkbox-group {
  flex-direction: row;
  gap: 1.5rem;
  align-items: center;
}

.training-ui {
  border: 1px solid #646262;
  padding: 1.5rem;
  border-radius: 4px;
}

.progress-bar-container {
  width: 100%;
  height: 20px;
  border: 1px solid #646262;
  margin: 1rem 0;
}

.progress-bar {
  height: 100%;
  background: #201d1d;
  transition: width 0.3s ease;
}

.metrics {
  display: flex;
  justify-content: space-between;
  font-family: 'Berkeley Mono', monospace;
}
</style>
