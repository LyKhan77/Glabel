<template>
  <div class="dashboard-container">
    <header class="header">
      <h1>[Glabel]</h1>
      <p>Computer Vision Node-Based Pipeline Builder</p>
    </header>

    <main class="main-content">
      <section class="actions-section">
        <h2>Actions</h2>
        <div class="actions">
          <button class="btn action-btn" @click="newPlayground">
            <span class="icon">[+]</span> New Inference Playground
          </button>
          <button class="btn action-btn" @click="openVisionSolution">
            <span class="icon">[Folder]</span> Open Vision Solution
          </button>
        </div>
      </section>

      <section class="recent-workspaces-section">
        <h2>Recent Workspaces</h2>
        <table class="workspace-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Path</th>
              <th>Last Modified</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ws in recentWorkspaces" :key="ws.id">
              <td>{{ ws.id }}</td>
              <td>{{ ws.name }}</td>
              <td class="path">{{ ws.path }}</td>
              <td>{{ ws.lastModified }}</td>
              <td>
                <button class="btn sm-btn" @click="removeWorkspace(ws.id)">[-] Remove</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const newPlayground = () => {
  router.push('/workspace')
}

const openVisionSolution = () => {
  alert('Mock: Opening File Picker...')
}

const recentWorkspaces = ref([
  { id: 'ws-001', name: 'Face Detection Prod', path: '/home/user/glabel-projects/face-detect', lastModified: '2026-06-15 14:32' },
  { id: 'ws-002', name: 'Object Tracking Test', path: '/home/user/glabel-projects/obj-track', lastModified: '2026-06-14 09:15' },
  { id: 'ws-003', name: 'OCR Pipeline', path: '/home/user/glabel-projects/ocr-pipe', lastModified: '2026-06-10 11:45' }
])

const removeWorkspace = (id) => {
  recentWorkspaces.value = recentWorkspaces.value.filter(ws => ws.id !== id)
}
</script>

<style scoped>
.dashboard-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  margin-bottom: 2rem;
  border-bottom: 1px solid #646262;
  padding-bottom: 1rem;
}

.header h1 {
  font-size: 1.5rem;
  margin: 0;
}

.header p {
  margin: 0.5rem 0 0 0;
  color: #646262;
}

section {
  margin-bottom: 3rem;
}

h2 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  border-bottom: 1px dashed #646262;
  padding-bottom: 0.5rem;
}

.actions {
  display: flex;
  gap: 1rem;
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

.sm-btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.85rem;
}

.workspace-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #646262;
}

.workspace-table th,
.workspace-table td {
  border: 1px solid #646262;
  padding: 0.75rem;
  text-align: left;
}

.workspace-table th {
  background: rgba(15,0,0,0.05);
}

.path {
  color: #646262;
  font-size: 0.9rem;
}
</style>
