<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const playgrounds = ref([
  { id: 'play-001', name: 'Counting Logic', description: 'Zone counting with Object Detection' },
  { id: 'play-002', name: 'Face Blur Pipeline', description: 'Face detection and blur node' }
])

const openPlayground = (id) => {
  router.push(`/playgrounds/${id}`)
}

const newPlayground = () => {
  router.push('/playgrounds/new')
}
</script>

<template>
  <div class="dashboard-container">
    <header class="header">
      <h1>Playgrounds</h1>
      <p>Visual Node Builder</p>
      <button class="btn action-btn" @click="newPlayground">
        <span class="icon">[+]</span> New Playground Workspace
      </button>
    </header>

    <main class="main-content">
      <section class="projects-section">
        <h2>Saved Playgrounds</h2>
        <div class="projects-grid">
          <div class="project-card" v-for="play in playgrounds" :key="play.id" @click="openPlayground(play.id)">
            <h3>{{ play.name }}</h3>
            <p class="desc">{{ play.description }}</p>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.dashboard-container {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
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
  background-color: var(--hover-bg, rgba(15,0,0,0.05));
}

.btn {
  background: transparent;
  color: var(--text-color, #201d1d);
  border: 1px solid var(--border-color, #646262);
  border-radius: 0;
  padding: 0.5rem 1rem;
  font-family: inherit;
  font-size: inherit;
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
</style>
