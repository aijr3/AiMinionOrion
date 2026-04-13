<template>
  <header class="app-header">
    <div class="header-inner">
      <RouterLink to="/" class="logo">
        <span class="logo-icon">⚔</span>
        <span class="logo-text">Miro<span class="logo-accent">Strategy</span></span>
      </RouterLink>

      <nav class="header-nav" v-if="scenarioId">
        <RouterLink :to="`/scenarios/${scenarioId}/analysis`" class="nav-link">Analysis</RouterLink>
        <RouterLink :to="`/scenarios/${scenarioId}/frameworks`" class="nav-link">Frameworks</RouterLink>
        <RouterLink :to="`/scenarios/${scenarioId}/personas`" class="nav-link">Personas</RouterLink>
        <RouterLink :to="`/scenarios/${scenarioId}/strategy`" class="nav-link">Strategy</RouterLink>
        <RouterLink :to="`/scenarios/${scenarioId}/pain-points`" class="nav-link">Pain Points</RouterLink>
        <RouterLink :to="`/scenarios/${scenarioId}/campaigns`" class="nav-link">Campaigns</RouterLink>
        <RouterLink :to="`/scenarios/${scenarioId}/roadmap`" class="nav-link">Roadmap</RouterLink>
        <RouterLink :to="`/scenarios/${scenarioId}/dashboard`" class="nav-link">Dashboard</RouterLink>
        <RouterLink :to="`/scenarios/${scenarioId}/greene`" class="nav-link nav-greene">Greene</RouterLink>
      </nav>

      <div class="header-actions">
        <!-- API key status indicator + settings button -->
        <button class="settings-btn" @click="showSettings = true" :title="keySet ? 'API key configured — click to update' : 'No API key — click to add'">
          <span class="key-dot" :class="keySet ? 'dot-green' : 'dot-amber'" />
          <span class="settings-label">{{ keySet ? 'API: ✓' : 'API Key' }}</span>
          <span class="gear-icon">⚙</span>
        </button>

        <RouterLink to="/scenarios" class="btn btn-secondary" style="font-size:13px;padding:8px 16px;">All Scenarios</RouterLink>
        <RouterLink to="/scenarios/new" class="btn btn-primary" style="font-size:13px;padding:8px 16px;">+ New Scenario</RouterLink>
      </div>
    </div>
  </header>

  <SettingsModal v-if="showSettings" @close="showSettings = false" @saved="onSaved" />
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '../api/index.js'
import SettingsModal from './SettingsModal.vue'

const route = useRoute()
const scenarioId = computed(() => route.params.id || null)

const showSettings = ref(false)
const keySet = ref(false)

onMounted(async () => {
  try {
    const res = await api.get('/settings')
    keySet.value = (res.data || res).llm_api_key_set || false
  } catch {}
})

function onSaved({ keySet: k }) {
  keySet.value = k
}
</script>

<style scoped>
.app-header {
  background: rgba(10,14,26,0.95);
  border-bottom: 1px solid var(--border);
  position: sticky; top: 0; z-index: 100;
  backdrop-filter: blur(12px);
}
.header-inner {
  max-width: 1400px; margin: 0 auto;
  display: flex; align-items: center; gap: 24px;
  padding: 0 24px; height: 60px;
}
.logo { display: flex; align-items: center; gap: 8px; text-decoration: none; }
.logo-icon { font-size: 20px; }
.logo-text { font-size: 18px; font-weight: 800; color: var(--text-primary); }
.logo-accent { color: var(--accent-blue); }
.header-nav { display: flex; gap: 4px; flex: 1; }
.nav-link {
  padding: 6px 12px; border-radius: 6px; font-size: 13px;
  text-decoration: none; color: var(--text-secondary);
  transition: all 0.2s;
}
.nav-link:hover, .nav-link.router-link-active {
  color: var(--text-primary); background: var(--bg-card);
}
.nav-greene { color: var(--accent-gold) !important; }
.nav-greene:hover, .nav-greene.router-link-active { background: rgba(212,175,55,0.1) !important; }
.header-actions { display: flex; gap: 8px; align-items: center; margin-left: auto; }

/* Settings button */
.settings-btn {
  display: flex; align-items: center; gap: 6px;
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 8px; padding: 6px 12px;
  color: var(--text-secondary); font-size: 13px; font-weight: 500;
  cursor: pointer; transition: all 0.2s;
}
.settings-btn:hover { border-color: var(--accent-blue); color: var(--text-primary); }
.key-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.dot-green { background: var(--accent-green); box-shadow: 0 0 5px var(--accent-green); }
.dot-amber { background: var(--accent-amber); box-shadow: 0 0 5px var(--accent-amber); }
.settings-label { font-size: 12px; }
.gear-icon { font-size: 14px; opacity: 0.7; }
</style>
