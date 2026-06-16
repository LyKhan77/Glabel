<script setup>
import { ref } from 'vue'

const sysInfo = ref(null)

const detectSystem = () => {
  // Mock detection
  sysInfo.value = "Detected: Windows 11 | GPU: NVIDIA RTX 4090 (CUDA Available) | CPU: AMD Ryzen 9"
  alert("System detected successfully. Once the backend is implemented, this will fetch real hardware information via WebSocket/API.")
}
</script>

<template>
  <div class="settings-container">
    <header class="header">
      <h1>Settings</h1>
      <p>Local Configuration</p>
    </header>

    <main class="main-content">
      <div class="settings-section">
        <h3>Hardware Target</h3>
        <div style="display: flex; gap: 1rem; align-items: center; margin-bottom: 0.5rem;">
          <select class="austere-input" style="flex: 1; margin-bottom: 0;">
            <option>Auto (Detect)</option>
            <option>CPU</option>
            <option>GPU (CUDA)</option>
            <option>MPS (Apple Silicon)</option>
          </select>
          <button class="btn" @click="detectSystem">[Detect System]</button>
        </div>
        <p v-if="sysInfo" class="desc sys-info">{{ sysInfo }}</p>
      </div>

      <div class="settings-section">
        <h3>Data Directory</h3>
        <p class="desc">Location where local datasets and models are saved.</p>
        <input type="text" value="./glabel_data" class="austere-input" />
      </div>

      <div class="settings-section">
        <button class="btn">[Save Configuration]</button>
      </div>
    </main>
  </div>
</template>

<style scoped>
.settings-container {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.header {
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--border-color, #646262);
  padding-bottom: 1rem;
}

.header h1 {
  font-size: 1.5rem;
  margin: 0;
}

.header p {
  margin: 0.5rem 0 0 0;
  color: var(--border-color, #646262);
}

.settings-section {
  margin-bottom: 2rem;
}

.settings-section h3 {
  margin-bottom: 0.5rem;
}

.desc {
  color: var(--border-color, #646262);
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.austere-input {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid var(--border-color, #646262);
  background: transparent;
  color: var(--text-color, #201d1d);
  padding: 0.5rem;
  font-family: inherit;
}
.austere-input:focus {
  outline: 1px solid var(--text-color, #201d1d);
}

select.austere-input option {
  background-color: var(--bg-color, #fdfcfc);
  color: var(--text-color, #201d1d);
}

.sys-info {
  margin-top: 0.5rem;
  color: #4caf50;
}

.btn {
  background: transparent;
  color: var(--text-color, #201d1d);
  border: 1px solid var(--border-color, #646262);
  border-radius: 4px;
  padding: 0.5rem 1rem;
  font-family: inherit;
  font-size: inherit;
  cursor: pointer;
}

.btn:hover {
  background: var(--text-color, #201d1d);
  color: var(--bg-color, #fdfcfc);
}
</style>
