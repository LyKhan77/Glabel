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
        <div v-if="errorMessage" class="empty-state error-state" style="margin-bottom: 1rem; padding: 0.5rem; background: #ffebeb; border: 1px solid #8a1f11;">{{ errorMessage }}</div>
        <div class="tabs" style="margin-bottom: 1rem; border-bottom: 1px solid var(--border-color, #646262); padding-bottom: 0.5rem;">
          <button class="btn sm-btn" :class="{ active: activeTab === 'manual' }" @click="activeTab = 'manual'" style="margin-right: 0.5rem;" :style="activeTab === 'manual' ? 'background: var(--text-color, #201d1d); color: var(--bg-color, #fdfcfc);' : ''">Manual Setup</button>
          <button class="btn sm-btn" :class="{ active: activeTab === 'assistant' }" @click="activeTab = 'assistant'" :style="activeTab === 'assistant' ? 'background: var(--text-color, #201d1d); color: var(--bg-color, #fdfcfc);' : ''">Glabel Assistant</button>
        </div>

        <!-- Manual Setup Tab -->
        <div v-if="activeTab === 'manual'">
          <div style="margin-bottom: 1rem;">
            <input v-model="newProjectForm.name" type="text" placeholder="Project Name" class="austere-input" />
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
          <button class="btn" @click="submitNewProject()">Create Project</button>
        </div>

        <!-- Assistant Tab -->
        <div v-if="activeTab === 'assistant'">
          <div v-if="!isConfigured">
            <h3>Configure Assistant</h3>
            <div style="margin-bottom: 1rem;">
              <label>Base URL:<input v-model="assistantConfig.baseUrl" type="text" class="austere-input" /></label>
            </div>
            <div style="margin-bottom: 1rem;">
              <label>API Key (optional):<input v-model="assistantConfig.apiKey" type="password" class="austere-input" /></label>
            </div>
            <div style="margin-bottom: 1rem;">
              <label>Model:<input v-model="assistantConfig.model" type="text" class="austere-input" /></label>
            </div>
            <button class="btn" @click="saveConfig">Save Configuration</button>
          </div>
          <div v-else>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
              <h3 style="margin: 0; border: none; padding: 0;">Ask Glabel Assistant</h3>
              <button class="btn sm-btn" @click="isConfigured = false">Edit Config</button>
            </div>
            <div style="margin-bottom: 1rem;">
              <textarea v-model="assistantPrompt" placeholder="Describe your vision pipeline..." class="austere-input" style="width: 100%; min-height: 100px; box-sizing: border-box;"></textarea>
            </div>
            <div v-if="isAssistantLoading" style="margin-bottom: 1rem; font-style: italic; color: var(--border-color, #646262);">Assistant is thinking...</div>
            <button v-else class="btn" @click="askAssistant">Ask Assistant</button>
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
import { askGlabelAssistant } from '../api/llmService'

const router = useRouter()

const showModal = ref(false)
const newProjectForm = ref({ name: '', task_type: 'object_detection' })
const errorMessage = ref('')
const isLoading = ref(false)

const openVisionProjects = ref([])

const activeTab = ref('manual') // 'manual' or 'assistant'
const assistantConfig = ref({ baseUrl: 'http://localhost:11434/v1', apiKey: '', model: 'llama3' })
const isConfigured = ref(false)
const assistantPrompt = ref('')
const isAssistantLoading = ref(false)

const saveConfig = () => {
  localStorage.setItem('glabel_agent_config', JSON.stringify(assistantConfig.value))
  isConfigured.value = true
}

const askAssistant = async () => {
  isAssistantLoading.value = true
  errorMessage.value = ''
  try {
    const result = await askGlabelAssistant(assistantPrompt.value, assistantConfig.value)
    // Pre-fill the form and switch to manual tab to let them review and submit
    newProjectForm.value.name = result.project_name
    newProjectForm.value.task_type = result.task_type
    activeTab.value = 'manual'
  } catch (err) {
    errorMessage.value = err.message
  } finally {
    isAssistantLoading.value = false
  }
}

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

const submitNewProject = async () => {
  errorMessage.value = ''
  const nameToUse = newProjectForm.value.name.trim() || newProjectForm.value.task_type
  try {
    const project = await createProject({
      name: nameToUse,
      description: "",
      task_type: newProjectForm.value.task_type
    })
    showModal.value = false
    newProjectForm.value = { name: '', task_type: 'object_detection' }
    router.push(`/project/${project.id}`)
  } catch (error) {
    errorMessage.value = 'Could not create project. Check backend status.'
  }
}

onMounted(() => {
  loadProjects()
  const saved = localStorage.getItem('glabel_agent_config')
  if (saved) {
    assistantConfig.value = JSON.parse(saved)
    isConfigured.value = true
  }
})
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
