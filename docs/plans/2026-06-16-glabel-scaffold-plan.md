# Glabel Scaffold & Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Set up the monorepo structure (FastAPI + Vue 3) and build the initial Terminal-Style Dashboard.

**Architecture:** Monorepo dengan folder `backend/` untuk FastAPI dan `frontend/` untuk Vue 3 + Vite. Komunikasi awal menggunakan WebSocket.

**Tech Stack:** Python, FastAPI, Uvicorn, Vue 3, Vite, TailwindCSS (untuk styling utility), Vue Router.

---

### Task 1: Initialize Backend (FastAPI)

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/main.py`
- Test: `backend/test_main.py`

- [ ] **Step 1: Create requirements.txt**

```text
fastapi==0.103.1
uvicorn==0.23.2
pytest==7.4.2
httpx==0.25.0
websockets==11.0.3
```

- [ ] **Step 2: Write the failing test for health endpoint**

```python
# backend/test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest backend/test_main.py`
Expected: FAIL with "ModuleNotFoundError: No module named 'main'"

- [ ] **Step 4: Write minimal implementation**

```python
# backend/main.py
from fastapi import FastAPI, WebSocket

app = FastAPI(title="Glabel API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("Connected to Glabel Engine")
    await websocket.close()
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest backend/test_main.py`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add backend/
git commit -m "chore: init fastapi backend and health check"
```

### Task 2: Scaffold Frontend (Vue 3 + Vite)

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`

- [ ] **Step 1: Create package.json & install deps**
*(Note: We use plain files to simulate scaffolding without interactive CLI)*

```json
{
  "name": "glabel-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.3.4",
    "vue-router": "^4.2.4",
    "@vue-flow/core": "^1.29.2"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.2.3",
    "vite": "^4.4.5"
  }
}
```

- [ ] **Step 2: Configure Vite**

```javascript
// frontend/vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000
  }
})
```

- [ ] **Step 3: Setup minimal Vue entry point**

```html
<!-- frontend/index.html -->
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Glabel</title>
  </head>
  <body style="margin: 0; background: #fdfcfc; font-family: monospace;">
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

```javascript
// frontend/src/main.js
import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
```

```vue
<!-- frontend/src/App.vue -->
<template>
  <div>
    <h1>Glabel UI Loading...</h1>
  </div>
</template>

<script setup>
</script>
```

- [ ] **Step 4: Verify UI starts**

Run: `cd frontend && npm install && npm run dev`
Expected: Server running on localhost:3000

- [ ] **Step 5: Commit**

```bash
git add frontend/
git commit -m "chore: scaffold vue 3 frontend"
```

### Task 3: Implement Dashboard (Terminal-Style)

**Files:**
- Create: `frontend/src/views/Dashboard.vue`
- Modify: `frontend/src/main.js`
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: Setup Vue Router in main.js**

```javascript
// frontend/src/main.js
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Dashboard from './views/Dashboard.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Dashboard }
  ]
})

createApp(App).use(router).mount('#app')
```

- [ ] **Step 2: Update App.vue for routing**

```vue
<!-- frontend/src/App.vue -->
<template>
  <router-view></router-view>
</template>
```

- [ ] **Step 3: Create Terminal-Style Dashboard**

```vue
<!-- frontend/src/views/Dashboard.vue -->
<template>
  <div class="dashboard-container" style="padding: 2rem; color: #1e1e1e;">
    <h1 style="font-size: 1.5rem; margin-bottom: 2rem;">Glabel // Computer Vision Workspace</h1>
    
    <div style="display: flex; flex-direction: column; gap: 1rem; max-width: 400px;">
      <button @click="newPlayground" style="padding: 1rem; border: 1px solid #1e1e1e; background: transparent; cursor: pointer; text-align: left; font-family: monospace;">
        [+] New Inference Playground
      </button>
      
      <button style="padding: 1rem; border: 1px solid #1e1e1e; background: transparent; cursor: pointer; text-align: left; font-family: monospace;">
        [Folder] Open Vision Solution
      </button>
    </div>

    <div style="margin-top: 3rem;">
      <h2 style="font-size: 1rem; color: #666; border-bottom: 1px solid #ddd; padding-bottom: 0.5rem;">Recent Workspaces</h2>
      <p style="color: #999; margin-top: 1rem; font-style: italic;">No recent workspaces found.</p>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const newPlayground = () => {
  // We will route to canvas view here later
  console.log("Navigating to new playground...")
}
</script>
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/
git commit -m "feat: add terminal style dashboard view"
```
