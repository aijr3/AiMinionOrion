<template>
  <div class="framework-view">
    <StepProgress :scenario-id="$route.params.id" current-step="frameworks" />
    <h1 class="page-title">Framework Analysis</h1>
    <p class="page-subtitle">All analytical frameworks applied to your scenario with applicability scores and key insights.</p>
    <div class="fw-grid" v-if="frameworks.length">
      <div class="fw-card card" v-for="fw in frameworks" :key="fw.id">
        <div class="fw-card-header">
          <div>
            <div class="fw-type-badge">{{ fw.framework_type }}</div>
            <div class="fw-name">{{ fw.framework_name }}</div>
          </div>
          <div class="fw-score-ring" v-if="fw.applicability_score">
            <svg width="56" height="56" viewBox="0 0 56 56">
              <circle cx="28" cy="28" r="24" fill="none" stroke="var(--border)" stroke-width="4"/>
              <circle cx="28" cy="28" r="24" fill="none" stroke="var(--accent-blue)" stroke-width="4"
                stroke-dasharray="150.8" :stroke-dashoffset="150.8*(1-fw.applicability_score)"
                stroke-linecap="round" transform="rotate(-90 28 28)"/>
              <text x="28" y="34" text-anchor="middle" fill="white" font-size="13" font-weight="bold">{{ Math.round(fw.applicability_score*100) }}%</text>
            </svg>
          </div>
        </div>
        <p class="fw-summary">{{ fw.summary }}</p>
        <div class="insights-list" v-if="fw.key_insights?.length">
          <div class="insight-item" v-for="ins in fw.key_insights" :key="ins">→ {{ ins }}</div>
        </div>
      </div>
    </div>
    <div v-else class="empty card"><p>Framework analysis will appear after running the full analysis pipeline.</p></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { scenariosApi } from '../api/scenarios.js'
import StepProgress from '../components/StepProgress.vue'

const route = useRoute()
const frameworks = ref([])
onMounted(async () => {
  try {
    const res = await scenariosApi.getAnalysis(route.params.id)
    frameworks.value = res.data?.framework_summaries || []
  } catch {}
})
</script>

<style scoped>
.fw-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.fw-card { }
.fw-card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px; }
.fw-type-badge { font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--accent-blue); letter-spacing: 0.5px; margin-bottom: 4px; }
.fw-name { font-size: 16px; font-weight: 700; }
.fw-summary { font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin: 0 0 12px; }
.insights-list { display: flex; flex-direction: column; gap: 6px; }
.insight-item { font-size: 13px; color: var(--text-secondary); }
.empty { text-align: center; padding: 60px; color: var(--text-secondary); }
</style>
