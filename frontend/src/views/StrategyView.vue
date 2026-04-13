<template>
  <div class="strategy-view">
    <StepProgress :scenario-id="$route.params.id" current-step="strategy" />
    <div class="view-header">
      <div>
        <h1 class="page-title">Strategy</h1>
        <p class="page-subtitle">Win paths, pivot options, and graceful exit strategies with probabilities.</p>
      </div>
      <div class="view-actions">
        <div class="path-toggle">
          <button :class="{ active: pathFilter === 'all' }" @click="pathFilter='all'">All</button>
          <button :class="{ active: pathFilter === 'win' }" @click="pathFilter='win'">Win Paths</button>
          <button :class="{ active: pathFilter === 'graceful' }" @click="pathFilter='graceful'">Graceful Forward</button>
        </div>
        <button class="btn btn-primary" @click="generate" :disabled="generating">
          {{ generating ? 'Generating…' : '+ Generate Strategies' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading strategies…</div>
    <div v-else-if="filteredStrategies.length" class="strategies-list">
      <div
        class="strategy-card card"
        v-for="s in filteredStrategies"
        :key="s.id"
        :class="`type-${s.strategy_type}`"
      >
        <div class="strategy-header">
          <div class="strategy-meta">
            <span class="badge" :class="typeBadge(s.strategy_type)">{{ s.strategy_type?.replace('_', ' ') }}</span>
            <span class="approach-tag">{{ s.approach }}</span>
          </div>
          <div class="win-prob" :style="{ color: probColor(s.win_probability) }">
            {{ pct(s.win_probability) }}
          </div>
        </div>
        <h3 class="strategy-title">{{ s.title }}</h3>
        <p class="strategy-summary">{{ s.summary }}</p>

        <div v-if="s.frameworks_applied?.length" class="frameworks-row">
          <span v-for="fw in s.frameworks_applied" :key="fw" class="fw-tag">{{ fw }}</span>
        </div>

        <div class="prob-bar" style="margin:16px 0 8px">
          <div class="prob-fill" :style="{ width: pct(s.win_probability), background: probColor(s.win_probability) }" />
        </div>
        <div class="ci-text" v-if="s.confidence_interval?.lower">
          90% CI: {{ pct(s.confidence_interval.lower) }} – {{ pct(s.confidence_interval.upper) }}
        </div>

        <div v-if="s.greene_laws_applied?.length" class="greene-laws">
          <div class="greene-laws-title">👑 Greene Laws Applied</div>
          <div v-for="law in s.greene_laws_applied" :key="law" class="greene-law-tag">{{ law }}</div>
        </div>

        <div v-if="s.sun_tzu_principles?.length" class="sun-tzu">
          <div class="sun-tzu-title">⚔ Sun Tzu Principles</div>
          <div v-for="p in s.sun_tzu_principles" :key="p" class="sun-tzu-item">{{ p }}</div>
        </div>

        <div class="tactics-section" v-if="s.tactics?.length">
          <div class="tactics-title">Tactics ({{ s.tactics.length }})</div>
          <div class="tactic-row" v-for="t in s.tactics" :key="t.id">
            <div class="tactic-info">
              <div class="tactic-name">{{ t.title }}</div>
              <div class="tactic-desc">{{ t.description }}</div>
            </div>
            <div class="tactic-badges">
              <span class="badge" :class="`badge-${t.priority}`">{{ t.priority }}</span>
              <span class="tactic-source">{{ t.framework_source }}</span>
            </div>
          </div>
        </div>

        <button class="btn btn-secondary" style="margin-top:16px" @click="viewLogic(s)">
          View Full Logic & Reasoning →
        </button>
      </div>
    </div>
    <div v-else class="empty card">
      <p>No strategies yet. Run analysis first, then generate strategies.</p>
    </div>

    <!-- Logic Modal -->
    <div class="modal-overlay" v-if="logicModal" @click.self="logicModal=null">
      <div class="modal-panel card">
        <div class="modal-header">
          <h3>{{ logicModal.title }}</h3>
          <button class="btn-close" @click="logicModal=null">✕</button>
        </div>
        <div class="logic-content">{{ logicModal.logic_explanation }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { scenariosApi } from '../api/scenarios.js'
import StepProgress from '../components/StepProgress.vue'

const route = useRoute()
const strategies = ref([])
const loading = ref(true)
const generating = ref(false)
const pathFilter = ref('all')
const logicModal = ref(null)

const filteredStrategies = computed(() => {
  if (pathFilter.value === 'win') return strategies.value.filter(s => s.strategy_type === 'win')
  if (pathFilter.value === 'graceful') return strategies.value.filter(s => ['graceful_exit', 'pivot', 'coexistence'].includes(s.strategy_type))
  return strategies.value
})

onMounted(load)

async function load() {
  loading.value = true
  try {
    const res = await scenariosApi.listStrategies(route.params.id)
    strategies.value = res.data || []
  } catch {} finally { loading.value = false }
}

async function generate() {
  generating.value = true
  try {
    await scenariosApi.generateStrategies(route.params.id)
    setTimeout(load, 3000)
  } catch {} finally { generating.value = false }
}

async function viewLogic(s) {
  if (!s.logic_explanation) {
    const res = await scenariosApi.getStrategyExplanation(route.params.id, s.id)
    s.logic_explanation = res.data?.logic_explanation
  }
  logicModal.value = s
}

function typeBadge(type) {
  return { win: 'badge-win', graceful_exit: 'badge-exit', pivot: 'badge-pivot', coexistence: 'badge-medium' }[type] || 'badge-medium'
}
function pct(val) { return val != null ? Math.round(val * 100) + '%' : '?' }
function probColor(val) {
  if (val == null) return 'var(--text-secondary)'
  if (val >= 0.7) return 'var(--accent-green)'
  if (val >= 0.4) return 'var(--accent-amber)'
  return 'var(--accent-red)'
}
</script>

<style scoped>
.view-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px; }
.view-actions { display: flex; gap: 12px; align-items: center; }
.path-toggle { display: flex; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.path-toggle button { background: none; border: none; color: var(--text-secondary); padding: 8px 14px; cursor: pointer; font-size: 13px; }
.path-toggle button.active { background: var(--accent-blue); color: white; }
.strategies-list { display: flex; flex-direction: column; gap: 20px; }
.strategy-card { }
.strategy-card.type-graceful_exit { border-left: 3px solid var(--accent-purple); }
.strategy-card.type-win { border-left: 3px solid var(--accent-green); }
.strategy-card.type-pivot { border-left: 3px solid var(--accent-amber); }
.strategy-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.strategy-meta { display: flex; gap: 8px; align-items: center; }
.approach-tag { font-size: 12px; color: var(--text-secondary); background: var(--bg-secondary); padding: 2px 8px; border-radius: 4px; }
.win-prob { font-size: 28px; font-weight: 800; }
.strategy-title { font-size: 20px; font-weight: 700; margin: 0 0 10px; }
.strategy-summary { color: var(--text-secondary); margin: 0 0 12px; font-size: 14px; line-height: 1.6; }
.frameworks-row { display: flex; flex-wrap: wrap; gap: 6px; }
.fw-tag { background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2); color: var(--accent-blue); font-size: 11px; padding: 2px 8px; border-radius: 20px; }
.ci-text { font-size: 12px; color: var(--text-secondary); }
.greene-laws { margin-top: 14px; padding: 12px; background: rgba(212,175,55,0.05); border: 1px solid rgba(212,175,55,0.2); border-radius: 8px; }
.greene-laws-title { font-size: 12px; font-weight: 600; color: var(--accent-gold); margin-bottom: 8px; }
.greene-law-tag { display: inline-block; background: rgba(212,175,55,0.1); color: var(--accent-gold); font-size: 11px; padding: 2px 8px; border-radius: 4px; margin: 2px 4px 2px 0; }
.sun-tzu { margin-top: 10px; }
.sun-tzu-title { font-size: 12px; font-weight: 600; color: var(--accent-amber); margin-bottom: 6px; }
.sun-tzu-item { font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; }
.tactics-section { margin-top: 16px; padding-top: 16px; border-top: 1px solid var(--border); }
.tactics-title { font-size: 13px; font-weight: 600; margin-bottom: 12px; }
.tactic-row { display: flex; justify-content: space-between; align-items: start; padding: 10px 0; border-bottom: 1px solid rgba(45,55,72,0.5); }
.tactic-name { font-size: 13px; font-weight: 600; margin-bottom: 4px; }
.tactic-desc { font-size: 12px; color: var(--text-secondary); }
.tactic-badges { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; }
.tactic-source { font-size: 11px; color: var(--text-secondary); }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 200; display: flex; align-items: center; justify-content: center; padding: 40px; }
.modal-panel { width: 100%; max-width: 800px; max-height: 80vh; overflow-y: auto; }
.modal-header { display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px; }
.btn-close { background: none; border: 1px solid var(--border); color: var(--text-primary); width: 32px; height: 32px; border-radius: 6px; cursor: pointer; }
.logic-content { font-size: 14px; line-height: 1.8; color: var(--text-secondary); white-space: pre-wrap; }
.loading, .empty { text-align: center; padding: 60px; color: var(--text-secondary); }
</style>
