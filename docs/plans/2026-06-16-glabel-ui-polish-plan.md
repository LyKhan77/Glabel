# Glabel UI Polish & Enhancements Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement UI/UX feedback to enhance mock data, routing structure, branding, themes, and canvas features.

**Architecture:** Vue 3 Composition API with Vue Router.

---

### Task 1: Theming, Branding, & App Layout Updates

**Files:**
- Modify: `frontend/index.html`
- Modify: `frontend/src/App.vue`
- Modify: `frontend/src/components/layout/Sidebar.vue`

- [ ] **Step 1: Setup Branding & Favicon**
In `index.html`, add `<link rel="icon" type="image/png" href="/glabel-logo-transparent.png" />`.

- [ ] **Step 2: Theme Variables & Transitions in App.vue**
In `App.vue`, replace the hardcoded body styles with CSS variables for Light and Dark modes.
```css
:root {
  --bg-color: #fdfcfc;
  --text-color: #201d1d;
  --border-color: #646262;
  --hover-bg: rgba(15,0,0,0.05);
}
[data-theme='dark'] {
  --bg-color: #1a1a1a;
  --text-color: #e0e0e0;
  --border-color: #4a4a4a;
  --hover-bg: rgba(255,255,255,0.05);
}
body { margin: 0; background-color: var(--bg-color); color: var(--text-color); font-family: 'Berkeley Mono', monospace; transition: background-color 0.3s ease, color 0.3s ease; }
* { transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease; }
```
Make sure `Sidebar` and other components use `var(--bg-color)`, `var(--text-color)`, and `var(--border-color)` instead of hardcoded hex values.

- [ ] **Step 3: Theme Toggle & Logo in Sidebar**
In `Sidebar.vue`, update the `<div class="logo">` to display `<img src="/glabel-logo-transparent.png" alt="Glabel" style="height: 40px; filter: grayscale(100%);" />`.
Add a toggle button at the bottom of the sidebar: `[Toggle Theme]`.
In the script setup, implement the toggle logic:
```javascript
import { ref, onMounted } from 'vue'
const isDark = ref(false)
const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
}
```

- [ ] **Step 4: Commit**
`git add frontend/`
`git commit -m "feat: add dark mode theme, transitions, and logo branding"`

### Task 2: Open Vision Enhancements

**Files:**
- Modify: `frontend/src/views/Dashboard.vue`
- Modify: `frontend/src/views/ProjectView.vue`

- [ ] **Step 1: Dashboard Workspace Name Input**
In `Dashboard.vue`, within the `showModal` structure, add an input field `<input type="text" placeholder="Workspace Name" class="austere-input" />` above the split-panel.
Update austere styling for inputs to have `1px solid var(--border-color)`, `background: transparent`, `color: var(--text-color)`.

- [ ] **Step 2: ProjectView Upload Media Modal**
In `ProjectView.vue`, add a `showUploadModal` ref. When `[Upload Media]` is clicked, set it to true.
Create the modal overlay (similar to Dashboard). Inside the modal, show two options:
1. "Upload Images" (mock button).
2. "Upload Video". If video is selected, show an input `<input type="number" placeholder="Frames per second" />`.
Add an `[Upload]` button that pushes new mock items to the `Unannotated` images array and closes the modal.

- [ ] **Step 3: Commit**
`git add frontend/`
`git commit -m "feat: enhance open vision dashboard modal and upload media modal"`

### Task 3: Playgrounds Dashboard & Canvas Updates

**Files:**
- Create: `frontend/src/views/PlaygroundsDashboard.vue`
- Modify: `frontend/src/views/Workspace.vue`
- Modify: `frontend/src/main.js`

- [ ] **Step 1: Playgrounds Dashboard**
Create `PlaygroundsDashboard.vue` with a list/grid of existing mock Playgrounds (e.g. "Counting Logic", "Face Blur Pipeline").
Add a `[+] New Playground Workspace` button that routes to `/playgrounds/new`.

- [ ] **Step 2: Canvas Background & Zoom Tools**
In `Workspace.vue`, add a "crumpled paper" background pattern to `.canvas-area`. We will use a subtle SVG noise filter or repeating SVG background for the `.vue-flow__pane`.
```css
.canvas-area {
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.05'/%3E%3C/svg%3E");
}
```
Import `useVueFlow` to get `zoomIn` and `zoomOut`.
```javascript
import { useVueFlow } from '@vue-flow/core'
const { zoomIn, zoomOut } = useVueFlow()
```
Add a floating toolbar on the canvas with `[+] Zoom In` and `[-] Zoom Out` buttons connected to these functions.

- [ ] **Step 3: Update Routing**
In `main.js`, update routes:
- `/playgrounds` -> `PlaygroundsDashboard`
- `/playgrounds/:id` -> `Workspace`

- [ ] **Step 4: Commit**
`git add frontend/`
`git commit -m "feat: add playgrounds dashboard, canvas noise bg, and zoom tools"`

### Task 4: Models & Settings Views

**Files:**
- Create: `frontend/src/views/ModelsView.vue`
- Create: `frontend/src/views/SettingsView.vue`
- Modify: `frontend/src/main.js`

- [ ] **Step 1: Models View**
Create `ModelsView.vue`. Display austere text: "No models trained yet. Go to Open Vision to train a new model."

- [ ] **Step 2: Settings View**
Create `SettingsView.vue`. Add mock UI:
- "Hardware Target": Select dropdown (Auto, CPU, GPU).
- "Data Directory": Input field showing `./glabel_data`.

- [ ] **Step 3: Update Routing & Commit**
In `main.js`, add routes for `/models` and `/settings`.
`git add frontend/`
`git commit -m "feat: add models and settings views"`
