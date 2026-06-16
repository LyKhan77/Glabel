<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const activeTab = ref('dataset') // 'dataset', 'versions', 'train'

// Dataset state
const datasetState = ref('unannotated') // 'unannotated', 'annotated'

const images = ref([
  { id: 1, annotated: false },
  { id: 2, annotated: false },
  { id: 3, annotated: false },
  { id: 4, annotated: false }
])

const unannotatedImages = computed(() => images.value.filter(img => !img.annotated))
const annotatedImages = computed(() => images.value.filter(img => img.annotated))

const goBack = () => {
  router.push('/')
}

const autoAnnotateAll = () => {
  images.value.forEach(img => {
    img.annotated = true
  })
}
</script>

<template>
  <div class="project-view">
    <!-- Header / Nav -->
    <header class="header">
      <button class="nav-btn" @click="goBack">[&lt;] Back</button>
      <div class="tabs">
        <button 
          :class="['tab-btn', { active: activeTab === 'dataset' }]"
          @click="activeTab = 'dataset'"
        >[Dataset]</button>
        <button 
          :class="['tab-btn', { active: activeTab === 'versions' }]"
          @click="activeTab = 'versions'"
        >[Versions]</button>
        <button 
          :class="['tab-btn', { active: activeTab === 'train' }]"
          @click="activeTab = 'train'"
        >[Train]</button>
      </div>
      <div class="spacer"></div>
    </header>

    <main class="content">
      <div v-if="activeTab === 'dataset'" class="dataset-view">
        <div class="dataset-subnav">
          <div class="subtabs">
            <button 
              :class="['subtab-btn', { active: datasetState === 'unannotated' }]"
              @click="datasetState = 'unannotated'"
            >[Unannotated]</button>
            <button 
              :class="['subtab-btn', { active: datasetState === 'annotated' }]"
              @click="datasetState = 'annotated'"
            >[Annotated]</button>
          </div>
          <div class="actions">
            <button class="action-btn" v-if="datasetState === 'unannotated'" @click="autoAnnotateAll">
              [Auto-Annotate All (SAM3)]
            </button>
            <button class="action-btn">[Upload Media]</button>
          </div>
        </div>

        <div class="grid-container">
          <div v-if="datasetState === 'unannotated'" class="image-grid">
            <div class="image-card" v-for="img in unannotatedImages" :key="img.id">
              <div class="image-placeholder">Image {{ img.id }}</div>
            </div>
            <div v-if="unannotatedImages.length === 0" class="empty-state">
              No unannotated images.
            </div>
          </div>
          <div v-if="datasetState === 'annotated'" class="image-grid">
            <div class="image-card" v-for="img in annotatedImages" :key="img.id">
              <div class="image-placeholder">Image {{ img.id }}<br>(Annotated)</div>
            </div>
            <div v-if="annotatedImages.length === 0" class="empty-state">
              No annotated images.
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="activeTab === 'versions'" class="versions-view">
        <p>[Versions Content]</p>
      </div>

      <div v-if="activeTab === 'train'" class="train-view">
        <p>[Train Content]</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
.project-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #646262;
  gap: 2rem;
}

.tabs {
  display: flex;
  gap: 1rem;
}

.spacer {
  flex-grow: 1;
}

button {
  background: transparent;
  border: none;
  font-family: inherit;
  font-size: inherit;
  color: inherit;
  cursor: pointer;
}

button:hover {
  text-decoration: underline;
}

.nav-btn, .tab-btn, .subtab-btn, .action-btn {
  padding: 0.25rem 0.5rem;
}

.tab-btn.active, .subtab-btn.active {
  background: #201d1d;
  color: #fdfcfc;
}

.content {
  flex-grow: 1;
  padding: 1.5rem;
}

.dataset-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.dataset-subnav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px dashed #646262;
  padding-bottom: 1rem;
}

.subtabs {
  display: flex;
  gap: 1rem;
}

.actions {
  display: flex;
  gap: 1rem;
}

.grid-container {
  flex-grow: 1;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
}

.image-card {
  aspect-ratio: 1;
  border: 1px solid #646262;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  text-align: center;
}

.image-placeholder {
  color: #646262;
}

.empty-state {
  color: #646262;
  font-style: italic;
  padding: 2rem 0;
}
</style>
