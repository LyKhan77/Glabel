<script setup>
import { computed } from 'vue'
import SplitBar from './SplitBar.vue'

const props = defineProps({
  version: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['click', 'delete', 'export', 'duplicate'])

const timeAgo = (dateStr) => {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const minutes = Math.floor(diff / 60000)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}
</script>

<template>
  <div class="version-card" @click="emit('click', version)">
    <div class="card-header">
      <div class="title-group">
        <h4>{{ version.name }}</h4>
        <span class="time">{{ timeAgo(version.created_at) }}</span>
      </div>
      <div class="actions">
        <button class="icon-btn" @click.stop="emit('export', version)" title="Export">Export</button>
        <button class="icon-btn" @click.stop="emit('duplicate', version)" title="Duplicate">Duplicate</button>
        <button class="icon-btn danger" @click.stop="emit('delete', version)" title="Delete">Delete</button>
      </div>
    </div>
    
    <div class="card-body">
      <div class="stat">{{ version.asset_count }} assets</div>
      <div class="split-wrapper" v-if="version.split">
        <SplitBar :train="version.split.train" :valid="version.split.valid" :test="version.split.test" />
      </div>
      <div class="chips" v-if="version.preprocessing?.length || version.augmentations?.length">
        <span class="chip" v-for="p in version.preprocessing" :key="p">{{ p }}</span>
        <span class="chip" v-for="a in version.augmentations" :key="a">{{ a }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.version-card {
  border: 1px solid var(--border-color, #646262);
  border-radius: 6px;
  padding: 1rem;
  background: var(--card-bg, #1a1a1a);
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}

.version-card:hover {
  border-color: var(--text-color, #fdfcfc);
  background: var(--hover-bg, #2a2a2a);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.title-group h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
}

.time {
  font-size: 0.8rem;
  color: var(--mute, #888);
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.icon-btn {
  background: transparent;
  border: 1px solid #646262;
  color: inherit;
  font-size: 0.8rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
}

.icon-btn:hover {
  background: #333;
}

.icon-btn.danger {
  color: #e06c75;
  border-color: #e06c75;
}

.icon-btn.danger:hover {
  background: rgba(224, 108, 117, 0.1);
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.stat {
  font-size: 0.9rem;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.chip {
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border: 1px solid #646262;
  border-radius: 12px;
  background: #201d1d;
}
</style>
