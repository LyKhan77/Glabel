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
        <button class="icon-btn" @click.stop="emit('export', version)" title="Export">[ Export ]</button>
        <button class="icon-btn" @click.stop="emit('duplicate', version)" title="Duplicate">[ Dup ]</button>
        <button class="icon-btn danger" @click.stop="emit('delete', version)" title="Delete">[ X ]</button>
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
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 16px;
  background: var(--bg-color);
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.version-card:hover {
  border-color: var(--text-color);
  background: var(--hover-bg);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.title-group h4 {
  margin: 0 0 4px 0;
  font-size: 1.1rem;
  font-weight: 700;
}

.time {
  font-size: 0.85rem;
  color: var(--mute);
}

.actions {
  display: flex;
  gap: 8px;
}

.icon-btn {
  background: transparent;
  border: none;
  color: var(--mute);
  font-family: inherit;
  font-size: 0.85rem;
  padding: 0;
  cursor: pointer;
}

.icon-btn:hover {
  color: var(--text-color);
}

.icon-btn.danger:hover {
  color: var(--danger);
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stat {
  font-size: 0.9rem;
  color: var(--body);
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  font-size: 0.8rem;
  padding: 2px 8px;
  border: 1px solid var(--hairline);
  border-radius: 4px;
  background: var(--surface-soft);
  color: var(--body);
}
</style>
