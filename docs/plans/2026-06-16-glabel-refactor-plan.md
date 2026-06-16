# Glabel Refactoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the new Global Sidebar Layout and the End-to-End "Open Vision" Studio workflow as defined in the refactoring PRD.

**Architecture:** Vue 3 Composition API with Vue Router. We will wrap the app in a global layout containing a Sidebar. Existing views will be refactored into the new routing structure.

**Tech Stack:** Vue 3, Vue Router, Vite.

---

### Task 1: Global App Layout & Routing Setup

**Files:**
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/main.js`
- Create: `frontend/src/components/layout/Sidebar.vue`

- [ ] **Step 1: Create Global Sidebar Component**
Create `Sidebar.vue`. It should have austere styling (1px right border, cream bg).
Include navigation links using `router-link` for: Open Vision (`/`), Playgrounds (`/playgrounds`), Models (`/models`), Settings (`/settings`).

```vue
<!-- frontend/src/components/layout/Sidebar.vue -->
<template>
  <aside class="sidebar">
    <div class="logo">[Glabel]</div>
    <nav class="nav-links">
      <router-link to="/" class="nav-item">Open Vision</router-link>
      <router-link to="/playgrounds" class="nav-item">Playgrounds</router-link>
      <router-link to="/models" class="nav-item">Models</router-link>
      <router-link to="/settings" class="nav-item">Settings</router-link>
    </nav>
  </aside>
</template>
<style scoped>
.sidebar { width: 250px; border-right: 1px solid #646262; display: flex; flex-direction: column; background: #fdfcfc; font-family: 'Berkeley Mono', monospace; height: 100vh; }
.logo { padding: 1rem; font-weight: bold; border-bottom: 1px solid #646262; }
.nav-links { display: flex; flex-direction: column; padding: 1rem 0; }
.nav-item { padding: 0.5rem 1rem; color: #201d1d; text-decoration: none; display: block; }
.nav-item:hover, .router-link-active { background: rgba(15,0,0,0.05); }
</style>
```

- [ ] **Step 2: Update App.vue Layout**
Wrap `<router-view>` with a flex container holding the `Sidebar`.

```vue
<!-- frontend/src/App.vue -->
<template>
  <div class="app-layout">
    <Sidebar />
    <main class="main-content">
      <router-view></router-view>
    </main>
  </div>
</template>
<script setup>
import Sidebar from './components/layout/Sidebar.vue'
</script>
<style>
body { margin: 0; background: #fdfcfc; color: #201d1d; font-family: 'Berkeley Mono', monospace; }
.app-layout { display: flex; height: 100vh; overflow: hidden; }
.main-content { flex: 1; overflow-y: auto; position: relative; }
</style>
```

- [ ] **Step 3: Update Routing**
In `frontend/src/main.js`, update routes:
- `/` points to `Dashboard.vue` (Open Vision).
- `/playgrounds` points to the existing `Workspace.vue`.
- Remove `/journey`.

```javascript
// frontend/src/main.js (partial)
import Dashboard from './views/Dashboard.vue'
import Workspace from './views/Workspace.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/playgrounds', component: Workspace }
]
```

- [ ] **Step 4: Commit**
```bash
git add frontend/
git commit -m "feat: setup global sidebar layout and routing"
```

### Task 2: Open Vision Dashboard & Split Modal

**Files:**
- Modify: `frontend/src/views/Dashboard.vue`
- Modify: `frontend/src/main.js`

- [ ] **Step 1: Refactor Dashboard View**
Replace current Dashboard content with a list/grid of Open Vision Projects.
Add a `[+] New Project` button that toggles a `showModal` ref.

- [ ] **Step 2: Create Split-Panel Modal**
Add a modal `div` (conditionally rendered via `showModal`).
Inside the modal box, use CSS flex to split into two columns:
- Left column: Textarea for "AI Assistant Prompt".
- Right column: Grid of manual task buttons (Object Detection, Segmentation, OCR).

- [ ] **Step 3: Handle Modal Submission**
When a manual task is clicked, route the user to `/project/new`.
Update router in `main.js` to support `{ path: '/project/:id', component: () => import('./views/ProjectView.vue') }`.

- [ ] **Step 4: Commit**
```bash
git add frontend/
git commit -m "feat: implement open vision dashboard and creation modal"
```

### Task 3: Project Workspace (Dataset Tabs)

**Files:**
- Create: `frontend/src/views/ProjectView.vue`

- [ ] **Step 1: ProjectView Shell & Internal Nav**
Create `ProjectView.vue`. Add an internal tab bar at the top: `[Dataset]`, `[Versions]`, `[Train]`. Use an `activeTab` ref (default `'dataset'`) to switch content.

- [ ] **Step 2: Implement Dataset Tab**
When `activeTab === 'dataset'`:
- Show a sub-nav for `Unannotated` and `Annotated` (use `datasetState` ref).
- Provide an `[Upload Media]` button.
- If `Unannotated` is active, show a mock gallery of images.
- Add a button `[Auto-Annotate All (SAM3)]` that moves mock images to the `Annotated` tab.

- [ ] **Step 3: Commit**
```bash
git add frontend/
git commit -m "feat: implement project workspace and dataset tabs"
```

### Task 4: Dataset Versioning & Training Wizard

**Files:**
- Modify: `frontend/src/views/ProjectView.vue`

- [ ] **Step 1: Implement Versions Tab**
When `activeTab === 'versions'`:
- Add `[Generate New Version]` button that opens an inline 3-step wizard.
- Wizard Step 1: Text "Train/Valid/Test Split (70/20/10)".
- Wizard Step 2: Checkboxes for Preprocessing (Resize, Grayscale).
- Wizard Step 3: Checkboxes for Augmentations (Flip, Rotate) and input for Multiplier.
- Button `[Generate]` saves it as a mock "Version 1" list item.

- [ ] **Step 2: Implement Train Tab**
When `activeTab === 'train'`:
- Button `[Start Training]`.
- Simulate training progress (0 to 100%) using `setInterval`.
- When 100% reached, show button `[Test in Playground]` that calls `router.push('/playgrounds')`.

- [ ] **Step 3: Commit**
```bash
git add frontend/src/views/ProjectView.vue
git commit -m "feat: implement versioning wizard and training dashboard"
```
