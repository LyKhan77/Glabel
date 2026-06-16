<template>
  <div class="journey-container">
    <header class="header">
      <h1>Vision Solution Journey</h1>
      <button class="btn" @click="cancel">[<] Cancel</button>
    </header>

    <main class="main-content">
      <div v-if="currentStep === 1">
        <!-- Step 1 placeholder -->
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
</style>
