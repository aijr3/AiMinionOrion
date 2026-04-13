<template>
  <div class="analysis-view">
    <StepProgress :scenario-id="$route.params.id" current-step="analysis" />
    <div class="view-header">
      <div><h1 class="page-title">Competitive Analysis</h1><p class="page-subtitle">Key player profiles, positioning, Porter's Five Forces, MBTI types, and centers of gravity.</p></div>
      <button class="btn btn-primary" @click="runAnalysis" :disabled="running">{{ running ? 'Analyzing…' : '↻ Re-run Analysis' }}</button>
    </div>

    <div v-if="loading" class="loading">Loading analysis…</div>
    <div v-else>
      <div v-if="competitors.length" class="competitors-grid">
        <div class="competitor-card card" v-for="c in competitors" :key="c.id">
          <div class="comp-header">
            <div>
              <div class="comp-name">{{ c.name }}</div>
              <div class="comp-positioning">{{ c.positioning }}</div>
            </div>
            <div class="comp-right">
              <span class="badge" :class="`badge-${c.threat_level || 'medium'}`">{{ c.threat_level }}</span>
              <div class="mbti-badge" v-if="c.mbti_type">{{ c.mbti_type }}</div>
            </div>
          </div>
          <div v-if="c.market_share" class="market-share">
            <div class="ms-label">Market Share</div>
            <div class="prob-bar">
              <div class="prob-fill" :style="{ width: (c.market_share*100)+'%', background: 'var(--accent-blue)' }" />
            </div>
            <div class="ms-pct">{{ Math.round(c.market_share*100) }}%</div>
          </div>
          <div class="swot-grid">
            <div>
              <div class="swot-title strengths">Strengths</div>
              <div v-for="s in c.strengths" :key="s" class="swot-item">{{ s }}</div>
            </div>
            <div>
              <div class="swot-title weaknesses">Weaknesses</div>
              <div v-for="w in c.weaknesses" :key="w" class="swot-item">{{ w }}</div>
            </div>
          </div>
          <div v-if="c.center_of_gravity" class="cog">
            <span class="cog-label">⚔ Center of Gravity:</span> {{ c.center_of_gravity }}
          </div>
        </div>
      </div>
      <div v-else class="empty card"><p>Run analysis to identify and profile key players.</p></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { scenariosApi } from '../api/scenarios.js'
import StepProgress from '../components/StepProgress.vue'

const route = useRoute()
const competitors = ref([])
const loading = ref(true)
const running = ref(false)

onMounted(async () => {
  try {
    const res = await scenariosApi.getAnalysis(route.params.id)
    competitors.value = res.data?.competitors || []
  } catch {} finally { loading.value = false }
})

async function runAnalysis() {
  running.value = true
  try {
    await scenariosApi.runCompetitiveAnalysis(route.params.id)
    setTimeout(async () => {
      const res = await scenariosApi.getAnalysis(route.params.id)
      competitors.value = res.data?.competitors || []
    }, 5000)
  } catch {} finally { running.value = false }
}
</script>

<style scoped>
.view-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px; }
.competitors-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.competitor-card { }
.comp-header { display: flex; justify-content: space-between; margin-bottom: 16px; }
.comp-name { font-size: 18px; font-weight: 700; margin-bottom: 4px; }
.comp-positioning { font-size: 13px; color: var(--text-secondary); }
.comp-right { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; }
.mbti-badge { background: rgba(139,92,246,0.2); color: var(--accent-purple); padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 700; }
.market-share { display: grid; grid-template-columns: 80px 1fr 40px; gap: 8px; align-items: center; margin-bottom: 16px; }
.ms-label { font-size: 12px; color: var(--text-secondary); }
.ms-pct { font-size: 12px; font-weight: 600; text-align: right; }
.swot-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
.swot-title { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.swot-title.strengths { color: var(--accent-green); }
.swot-title.weaknesses { color: var(--accent-red); }
.swot-item { font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; padding-left: 10px; position: relative; }
.swot-item::before { content: '·'; position: absolute; left: 0; }
.cog { font-size: 12px; color: var(--accent-amber); padding-top: 10px; border-top: 1px solid var(--border); }
.cog-label { font-weight: 600; }
.loading, .empty { text-align: center; padding: 60px; color: var(--text-secondary); }
</style>
