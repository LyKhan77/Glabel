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
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const currentStep = ref(1)

const cancel = () => {
  router.push('/')
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
</style>
