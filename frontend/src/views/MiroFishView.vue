<template>
  <div class="mirofish-view">
    <h1 class="page-title">MiroFish AI Simulation</h1>
    <p class="page-subtitle">Multi-agent simulation results — how autonomous agents representing each player in your scenario behave and interact.</p>

    <div class="mirofish-status card">
      <div class="status-icon">🔮</div>
      <div class="status-info">
        <div class="status-title">MiroFish Simulation Engine</div>
        <div class="status-desc">Powered by the MiroFish multi-agent prediction engine (github.com/666ghj/MiroFish) — 53k stars, AGPL-3.0</div>
      </div>
      <button class="btn btn-primary" @click="launch" :disabled="launching">
        {{ launching ? 'Launching…' : '🚀 Launch Simulation' }}
      </button>
    </div>

    <div v-if="results" class="results">
      <div class="results-header">Simulation Results</div>
      <pre class="results-json">{{ JSON.stringify(results, null, 2) }}</pre>
    </div>

    <div class="mirofish-info card">
      <h3>How MiroFish Enriches Your Strategy</h3>
      <div class="info-grid">
        <div class="info-item">
          <div class="info-icon">👥</div>
          <div class="info-title">Agent Seeding</div>
          <div class="info-desc">Your competitors and personas are converted into autonomous OASIS agents with personality and memory.</div>
        </div>
        <div class="info-item">
          <div class="info-icon">🔄</div>
          <div class="info-title">Emergent Behavior</div>
          <div class="info-desc">Thousands of interactions simulate how players actually behave — beyond linear assumptions.</div>
        </div>
        <div class="info-item">
          <div class="info-icon">📊</div>
          <div class="info-title">Probability Enrichment</div>
          <div class="info-desc">Simulation outcomes feed back into Bayesian probability estimates, refining win probability.</div>
        </div>
        <div class="info-item">
          <div class="info-icon">📝</div>
          <div class="info-title">Report Generation</div>
          <div class="info-desc">MiroFish's ReportAgent produces a narrative summary of predicted outcomes.</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { scenariosApi } from '../api/scenarios.js'

const route = useRoute()
const launching = ref(false)
const results = ref(null)

onMounted(async () => {
  try {
    const res = await scenariosApi.getSimulationResults(route.params.id)
    if (res.data?.status === 'complete') results.value = res.data.report
  } catch {}
})

async function launch() {
  launching.value = true
  try {
    await scenariosApi.launchSimulation(route.params.id)
    setTimeout(async () => {
      const res = await scenariosApi.getSimulationResults(route.params.id)
      results.value = res.data?.report || null
    }, 10000)
  } catch {} finally { launching.value = false }
}
</script>

<style scoped>
.mirofish-status { display: flex; gap: 20px; align-items: center; margin-bottom: 24px; }
.status-icon { font-size: 40px; }
.status-info { flex: 1; }
.status-title { font-size: 16px; font-weight: 700; margin-bottom: 4px; }
.status-desc { font-size: 13px; color: var(--text-secondary); }
.results { margin-bottom: 24px; }
.results-header { font-size: 14px; font-weight: 700; margin-bottom: 10px; }
.results-json { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; padding: 16px; font-size: 12px; color: var(--accent-green); overflow-x: auto; white-space: pre-wrap; max-height: 400px; overflow-y: auto; }
.info-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-top: 16px; }
.info-icon { font-size: 28px; margin-bottom: 8px; }
.info-title { font-size: 14px; font-weight: 700; margin-bottom: 6px; }
.info-desc { font-size: 12px; color: var(--text-secondary); line-height: 1.5; }
</style>
