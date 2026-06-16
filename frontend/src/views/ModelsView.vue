<template>
  <div class="models-container">
    <header class="header">
      <h1>Models</h1>
      <p>Local Model Repository</p>
    </header>

    <main class="main-content">
      <div class="empty-state">
        <p>No models trained yet.</p>
        <p>Go to <router-link to="/">Open Vision</router-link> to train a new model.</p>
      </div>
    </main>
  </div>
</template>

<style scoped>
.models-container {
  padding: 2rem;
  max-width: 1200px;
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

.empty-state {
  border: 1px dashed var(--border-color, #646262);
  padding: 4rem 2rem;
  text-align: center;
  color: var(--border-color, #646262);
}

.empty-state a {
  color: var(--text-color, #201d1d);
  text-decoration: underline;
}
</style>
