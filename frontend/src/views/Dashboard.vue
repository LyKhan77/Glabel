<template>
  <div class="dashboard-container">
    <header class="header">
      <h1>[Glabel]</h1>
      <p>Open Vision Studio</p>
      <button class="btn action-btn" @click="showModal = true">
        <span class="icon">[+]</span> New Project
      </button>
    </header>

    <main class="main-content">
      <section class="projects-section">
        <h2>Open Vision Projects</h2>
        <div v-if="isLoading" class="empty-state">Loading projects...</div>
        <div v-else-if="errorMessage" class="empty-state error-state">{{ errorMessage }}</div>
        <div v-else-if="openVisionProjects.length === 0" class="empty-state">No projects yet.</div>
        <div v-else class="projects-grid">
          <div class="project-card" v-for="project in openVisionProjects" :key="project.id" @click="openProject(project.id)">
            <h3>{{ project.name }}</h3>
            <p class="path">{{ project.description }}</p>
          </div>
        </div>
      </section>
    </main>

    <!-- Modal Overlay -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Create New Project</h2>
          <button class="btn sm-btn" @click="showModal = false">[x] Close</button>
        </div>
        <div style="margin-bottom: 1rem;">
          <input v-model="newProjectForm.name" type="text" placeholder="Workspace Name" class="austere-input" />
        </div>
        <div style="margin-bottom: 1rem;">
          <label>
            Task Type:
            <select v-model="newProjectForm.task_type" class="austere-input">
              <option value="classification">Classification</option>
              <option value="object_detection">Object Detection</option>
              <option value="segmentation">Segmentation</option>
              <option value="pose_estimation">Pose Estimation</option>
            </select>
          </label>
        </div>
        <div class="modal-split">
          <!-- Left Column -->
          <div class="modal-col">
            <h3>AI Assistant</h3>
            <textarea v-model="newProjectForm.description" placeholder="Describe your vision pipeline..."></textarea>
            <button class="btn" @click="submitNewProject()">Generate Pipeline</button>
          </div>
          <!-- Right Column -->
          <div class="modal-col">
            <h3>Manual Tasks</h3>
            <div class="task-grid">
            <button class="btn" @click="submitQuickTask('object_detection', 'Object Detection')">Object Detection</button>
            <button class="btn" @click="submitQuickTask('segmentation', 'Segmentation')">Segmentation</button>
            <button class="btn" @click="submitQuickTask('pose_estimation', 'Pose Estimation')">Pose Estimation</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createProject, listProjects } from '../api/client'

const router = useRouter()

const showModal = ref(false)
const newProjectForm = ref({ name: '', description: '', task_type: 'object_detection' })
const errorMessage = ref('')
const isLoading = ref(false)

const openVisionProjects = ref([])

const loadProjects = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    openVisionProjects.value = await listProjects()
  } catch (error) {
    errorMessage.value = 'Backend unavailable. Start FastAPI on http://127.0.0.1:8000.'
  } finally {
    isLoading.value = false
  }
}

const openProject = (id) => {
  router.push(`/project/${id}`)
}

const submitQuickTask = (typeEnum, description) => {
  newProjectForm.value.task_type = typeEnum
  submitNewProject(description)
}

const submitNewProject = async (taskType = 'Generated Pipeline') => {
  errorMessage.value = ''
  const fallbackName = newProjectForm.value.description.trim() || taskType
  try {
    const project = await createProject({
      name: newProjectForm.value.name.trim() || fallbackName,
      description: newProjectForm.value.description.trim() || taskType,
      task_type: newProjectForm.value.task_type
    })
    showModal.value = false
    newProjectForm.value = { name: '', description: '', task_type: 'object_detection' }
    router.push(`/project/${project.id}`)
  } catch (error) {
    errorMessage.value = 'Could not create project. Check backend status.'
  }
}

onMounted(loadProjects)
</script>

<style scoped>
.dashboard-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  font-family: 'Berkeley Mono', monospace;
  color: var(--text-color, #201d1d);
  background-color: var(--bg-color, #fdfcfc);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.projects-section {
  margin-bottom: 3rem;
}

h2 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  border-bottom: 1px dashed var(--border-color, #646262);
  padding-bottom: 0.5rem;
}

h3 {
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.project-card {
  border: 1px solid var(--border-color, #646262);
  padding: 1rem;
  cursor: pointer;
  background-color: transparent;
}

.project-card:hover {
  background-color: rgba(32, 29, 29, 0.05);
}

.empty-state {
  color: var(--border-color, #646262);
  font-style: italic;
  padding: 1rem 0;
}

.error-state {
  color: #8a1f11;
}

.btn {
  background: transparent;
  color: var(--text-color, #201d1d);
  border: 1px solid var(--border-color, #646262);
  border-radius: 0;
  padding: 0.5rem 1rem;
  font-family: 'Berkeley Mono', monospace;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn:hover {
  background: var(--text-color, #201d1d);
  color: var(--bg-color, #fdfcfc);
}

.sm-btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.85rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(32, 29, 29, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-color, #fdfcfc);
  border: 1px solid var(--border-color, #646262);
  width: 800px;
  max-width: 90vw;
  padding: 1.5rem;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--border-color, #646262);
  padding-bottom: 0.5rem;
}

.modal-header h2 {
  margin: 0;
  border: none;
  padding: 0;
}

.modal-split {
  display: flex;
  gap: 2rem;
}

.modal-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

textarea {
  flex: 1;
  min-height: 150px;
  background: transparent;
  border: 1px solid var(--border-color, #646262);
  color: var(--text-color, #201d1d);
  font-family: 'Berkeley Mono', monospace;
  padding: 0.5rem;
  resize: vertical;
}

textarea:focus {
  outline: 1px solid var(--text-color, #201d1d);
}

.task-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.5rem;
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
</style>
