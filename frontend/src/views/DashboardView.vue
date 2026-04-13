<template>
  <div class="dashboard" v-if="scenario">
    <StepProgress :scenario-id="scenario.id" current-step="dashboard" @navigate="nav" />
    <h1 class="page-title">Strategy Dashboard</h1>
    <p class="page-subtitle">{{ scenario.name }}</p>

    <div class="status-bar card" :class="`status-${scenario.status}`">
      <div class="status-label">Pipeline Status</div>
      <div class="status-value">{{ scenario.status?.toUpperCase() }}</div>
      <div v-if="scenario.status === 'analyzing'" class="status-spinner">Analyzing…</div>
    </div>

    <div class="metrics-top" v-if="metrics">
      <div class="metric-card card">
        <div class="metric-label">Win Probability</div>
        <div class="metric-value prob" :style="{ color: probColor(metrics.overall_win_probability) }">
          {{ pct(metrics.overall_win_probability) }}
        </div>
        <div class="prob-bar" style="margin-top:10px">
          <div class="prob-fill" :style="{ width: pct(metrics.overall_win_probability), background: probColor(metrics.overall_win_probability) }" />
        </div>
        <div class="metric-ci" v-if="metrics.confidence_interval?.lower">
          CI: {{ pct(metrics.confidence_interval.lower) }} – {{ pct(metrics.confidence_interval.upper) }}
        </div>
      </div>

      <div class="metric-card card">
        <div class="metric-label">Roadmap Probability</div>
        <div class="metric-value" style="color:var(--accent-purple)">{{ pct(metrics.final_cumulative_probability) }}</div>
        <div class="prob-bar" style="margin-top:10px">
          <div class="prob-fill" :style="{ width: pct(metrics.final_cumulative_probability), background: 'var(--accent-purple)' }" />
        </div>
      </div>

      <div class="metric-card card">
        <div class="metric-label">Strategies</div>
        <div class="metric-value">{{ metrics.total_strategies }}</div>
      </div>

      <div class="metric-card card">
        <div class="metric-label">Campaigns</div>
        <div class="metric-value">{{ metrics.total_campaigns }}</div>
      </div>

      <div class="metric-card card">
        <div class="metric-label">Frameworks Applied</div>
        <div class="metric-value">{{ metrics.frameworks_applied }}</div>
      </div>

      <div class="metric-card card" v-if="metrics.total_budget">
        <div class="metric-label">Total Budget</div>
        <div class="metric-value">${{ (metrics.total_budget || 0).toLocaleString() }}</div>
      </div>
    </div>

    <div class="dashboard-grid">
      <div class="card framework-panel">
        <h3 class="section-title" style="font-size:16px">Frameworks Applied</h3>
        <div class="fw-list" v-if="metrics?.framework_summaries">
          <div class="fw-row" v-for="fw in metrics.framework_summaries" :key="fw.name">
            <div class="fw-info">
              <div class="fw-name">{{ fw.name }}</div>
              <div class="fw-summary">{{ fw.summary }}</div>
            </div>
            <div class="fw-score" v-if="fw.score">{{ Math.round((fw.score || 0) * 100) }}%</div>
          </div>
        </div>
      </div>

      <div class="card campaigns-panel">
        <h3 class="section-title" style="font-size:16px">Campaign KPIs</h3>
        <div v-if="metrics?.campaigns?.length">
          <div class="campaign-kpi" v-for="c in metrics.campaigns" :key="c.id">
            <div class="campaign-name">{{ c.name }} <span class="badge badge-medium">{{ c.aida_phase }}</span></div>
            <div v-for="kpi in (c.kpis || [])" :key="kpi.id" class="kpi-row">
              <div class="kpi-name">{{ kpi.name }}</div>
              <div class="prob-bar kpi-bar">
                <div class="prob-fill" :style="{ width: (kpi.progress_pct || 0) + '%', background: 'var(--accent-green)' }" />
              </div>
              <div class="kpi-values">{{ kpi.current_value }} / {{ kpi.target_value }} {{ kpi.unit }}</div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">Campaigns will appear after strategy generation.</div>
      </div>
    </div>

    <div class="nav-cards">
      <RouterLink :to="`/scenarios/${$route.params.id}/analysis`" class="nav-card card">
        <div class="nav-card-icon">🔍</div>
        <div class="nav-card-title">Competitive Analysis</div>
        <div class="nav-card-desc">Key player profiles, market positioning, Porter's Five Forces</div>
      </RouterLink>
      <RouterLink :to="`/scenarios/${$route.params.id}/greene`" class="nav-card card nav-card-gold">
        <div class="nav-card-icon">👑</div>
        <div class="nav-card-title">Robert Greene Analysis</div>
        <div class="nav-card-desc">48 Laws, 33 Strategies, Art of Seduction, Human Nature</div>
      </RouterLink>
      <RouterLink :to="`/scenarios/${$route.params.id}/personas`" class="nav-card card">
        <div class="nav-card-icon">🧠</div>
        <div class="nav-card-title">MBTI Personas</div>
        <div class="nav-card-desc">Psychological profiles with intent modeling</div>
      </RouterLink>
      <RouterLink :to="`/scenarios/${$route.params.id}/strategy`" class="nav-card card">
        <div class="nav-card-icon">⚔</div>
        <div class="nav-card-title">Strategy</div>
        <div class="nav-card-desc">Win paths, graceful exits, tactical playbooks</div>
      </RouterLink>
      <RouterLink :to="`/scenarios/${$route.params.id}/roadmap`" class="nav-card card">
        <div class="nav-card-icon">🗺</div>
        <div class="nav-card-title">Victory Roadmap</div>
        <div class="nav-card-desc">Step-by-step milestones with cumulative probability</div>
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { scenariosApi } from '../api/scenarios.js'
import StepProgress from '../components/StepProgress.vue'

const route = useRoute()
const router = useRouter()
const scenario = ref(null)
const metrics = ref(null)

onMounted(async () => {
  const id = route.params.id
  try {
    const sr = await scenariosApi.get(id)
    scenario.value = sr.data
    const mr = await scenariosApi.getMetrics(id)
    metrics.value = mr.data
  } catch {}
})

function nav(key) { router.push(`/scenarios/${route.params.id}/${key}`) }
function pct(val) { return val != null ? Math.round(val * 100) + '%' : 'N/A' }
function probColor(val) {
  if (val == null) return 'var(--text-secondary)'
  if (val >= 0.7) return 'var(--accent-green)'
  if (val >= 0.4) return 'var(--accent-amber)'
  return 'var(--accent-red)'
}
</script>

<style scoped>
.status-bar { display: flex; align-items: center; gap: 20px; padding: 12px 20px; margin-bottom: 24px; }
.status-label { font-size: 12px; color: var(--text-secondary); }
.status-value { font-weight: 700; font-size: 14px; }
.status-spinner { font-size: 12px; color: var(--accent-blue); animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100% { opacity:1 } 50% { opacity:0.4 } }

.metrics-top { display: grid; grid-template-columns: 2fr 2fr 1fr 1fr 1fr 1fr; gap: 16px; margin-bottom: 24px; }
.metric-card { }
.metric-label { font-size: 11px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
.metric-value { font-size: 32px; font-weight: 800; }
.metric-ci { font-size: 11px; color: var(--text-secondary); margin-top: 6px; }

.dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 32px; }
.fw-list { display: flex; flex-direction: column; gap: 12px; }
.fw-row { display: flex; align-items: start; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border); }
.fw-name { font-size: 13px; font-weight: 600; margin-bottom: 3px; }
.fw-summary { font-size: 12px; color: var(--text-secondary); }
.fw-score { font-size: 14px; font-weight: 700; color: var(--accent-blue); white-space: nowrap; }
.fw-info { flex: 1; }

.campaign-kpi { margin-bottom: 16px; }
.campaign-name { font-size: 13px; font-weight: 600; margin-bottom: 8px; }
.kpi-row { display: grid; grid-template-columns: 1fr 100px 80px; gap: 10px; align-items: center; margin-bottom: 6px; }
.kpi-name { font-size: 12px; color: var(--text-secondary); }
.kpi-bar { height: 6px; }
.kpi-values { font-size: 11px; color: var(--text-secondary); text-align: right; }

.nav-cards { display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; }
.nav-card { text-decoration: none; color: inherit; display: block; transition: border-color 0.2s; }
.nav-card:hover { border-color: var(--accent-blue); }
.nav-card-gold:hover { border-color: var(--accent-gold) !important; }
.nav-card-icon { font-size: 24px; margin-bottom: 10px; }
.nav-card-title { font-size: 14px; font-weight: 700; margin-bottom: 6px; }
.nav-card-desc { font-size: 12px; color: var(--text-secondary); line-height: 1.5; }
.nav-card-gold { border-color: rgba(212,175,55,0.3); }
.empty-state { color: var(--text-secondary); font-size: 13px; }
</style>
