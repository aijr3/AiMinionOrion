<template>
  <div class="campaign-view">
    <StepProgress :scenario-id="$route.params.id" current-step="campaigns" />
    <div class="view-header">
      <div><h1 class="page-title">Campaigns</h1><p class="page-subtitle">Google Ads-compatible AIDA campaigns with KPIs, timelines, and seduction elements.</p></div>
      <button class="btn btn-primary" @click="planCampaigns" :disabled="planning">{{ planning ? 'Planning…' : '+ Plan Campaigns' }}</button>
    </div>

    <!-- AIDA Funnel visual -->
    <div class="aida-funnel card">
      <div class="aida-stage" v-for="(stage, i) in aidaStages" :key="stage.key">
        <div class="aida-label">{{ stage.label }}</div>
        <div class="aida-bar" :style="{ width: (100-i*15)+'%', background: stage.color }">
          <span class="aida-count">{{ campaignsByPhase(stage.key).length }} campaigns</span>
        </div>
      </div>
    </div>

    <div v-if="campaigns.length" class="campaigns-grid">
      <div class="campaign-card card" v-for="c in campaigns" :key="c.id">
        <div class="campaign-header">
          <div>
            <div class="campaign-name">{{ c.name }}</div>
            <div class="campaign-obj">{{ c.objective }}</div>
          </div>
          <div class="campaign-meta">
            <span class="badge badge-medium">{{ c.aida_phase }}</span>
            <span class="badge badge-win" v-if="c.google_ads_compatible">Google Ads</span>
          </div>
        </div>
        <div class="campaign-details">
          <div class="detail-item" v-if="c.owner">👤 {{ c.owner }}</div>
          <div class="detail-item" v-if="c.start_date">📅 {{ c.start_date }} → {{ c.end_date }}</div>
          <div class="detail-item" v-if="c.budget">${{ c.budget?.toLocaleString() }}</div>
        </div>
        <div class="channels" v-if="c.channels?.length">
          <span class="channel-tag" v-for="ch in c.channels" :key="ch">{{ ch }}</span>
        </div>
        <div class="kpis-section" v-if="c.kpis?.length">
          <div class="kpis-title">KPIs</div>
          <div class="kpi-row" v-for="kpi in c.kpis" :key="kpi.id">
            <div class="kpi-name">{{ kpi.name }}</div>
            <div class="prob-bar kpi-prog">
              <div class="prob-fill" :style="{ width: (kpi.progress_pct||0)+'%', background: 'var(--accent-green)' }" />
            </div>
            <div class="kpi-nums">{{ kpi.current_value }} / {{ kpi.target_value }} {{ kpi.unit }}</div>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="empty card"><p>Generate strategies first, then plan campaigns.</p></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { scenariosApi } from '../api/scenarios.js'
import api from '../api/index.js'
import StepProgress from '../components/StepProgress.vue'

const route = useRoute()
const campaigns = ref([])
const planning = ref(false)

const aidaStages = [
  { key: 'awareness', label: 'Awareness', color: 'rgba(59,130,246,0.7)' },
  { key: 'interest', label: 'Interest', color: 'rgba(139,92,246,0.7)' },
  { key: 'desire', label: 'Desire', color: 'rgba(245,158,11,0.7)' },
  { key: 'action', label: 'Action', color: 'rgba(16,185,129,0.7)' },
  { key: 'retention', label: 'Retention', color: 'rgba(212,175,55,0.7)' },
]

onMounted(load)

async function load() {
  try {
    const res = await scenariosApi.listStrategies(route.params.id)
    const strategies = res.data || []
    const all = []
    for (const s of strategies) {
      const cr = await api.get(`/strategies/${s.id}/campaigns`)
      all.push(...(cr.data || []))
    }
    campaigns.value = all
  } catch {}
}

async function planCampaigns() {
  planning.value = true
  try {
    const res = await scenariosApi.listStrategies(route.params.id)
    const strategies = res.data || []
    if (strategies.length) {
      await api.post(`/strategies/${strategies[0].id}/campaigns/plan`)
      setTimeout(load, 5000)
    }
  } catch {} finally { planning.value = false }
}

function campaignsByPhase(phase) { return campaigns.value.filter(c => c.aida_phase === phase) }
</script>

<style scoped>
.view-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px; }
.aida-funnel { margin-bottom: 24px; display: flex; flex-direction: column; gap: 8px; }
.aida-stage { display: flex; align-items: center; gap: 12px; }
.aida-label { width: 80px; font-size: 12px; font-weight: 600; color: var(--text-secondary); text-align: right; }
.aida-bar { height: 32px; border-radius: 6px; display: flex; align-items: center; padding: 0 12px; transition: width 0.5s ease; }
.aida-count { font-size: 12px; font-weight: 600; color: white; }
.campaigns-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.campaign-card { }
.campaign-header { display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px; }
.campaign-name { font-size: 16px; font-weight: 700; margin-bottom: 4px; }
.campaign-obj { font-size: 12px; color: var(--text-secondary); }
.campaign-meta { display: flex; flex-direction: column; gap: 4px; align-items: flex-end; }
.campaign-details { display: flex; gap: 16px; margin-bottom: 10px; }
.detail-item { font-size: 12px; color: var(--text-secondary); }
.channels { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
.channel-tag { background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2); color: var(--accent-blue); font-size: 11px; padding: 2px 8px; border-radius: 4px; }
.kpis-title { font-size: 12px; font-weight: 700; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 8px; }
.kpi-row { display: grid; grid-template-columns: 1fr 80px 80px; gap: 8px; align-items: center; margin-bottom: 6px; }
.kpi-name { font-size: 12px; }
.kpi-prog { height: 6px; }
.kpi-nums { font-size: 11px; color: var(--text-secondary); text-align: right; }
.empty { text-align: center; padding: 60px; color: var(--text-secondary); }
</style>
