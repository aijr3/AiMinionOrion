<template>
  <div class="pain-view">
    <StepProgress :scenario-id="$route.params.id" current-step="pain-points" />
    <div class="view-header">
      <div><h1 class="page-title">Pain Points</h1><p class="page-subtitle">Strategic friction identified with root causes, solutions, and psychological dimensions.</p></div>
      <button class="btn btn-primary" @click="extract" :disabled="extracting">{{ extracting ? 'Extracting…' : '+ Extract Pain Points' }}</button>
    </div>
    <div v-if="grouped.critical.length || grouped.high.length || grouped.medium.length || grouped.low.length">
      <div v-for="sev in ['critical','high','medium','low']" :key="sev">
        <div class="severity-group" v-if="grouped[sev].length">
          <div class="severity-header">
            <span class="badge" :class="`badge-${sev}`">{{ sev.toUpperCase() }}</span>
            <span class="count">{{ grouped[sev].length }} issues</span>
          </div>
          <div class="pp-list">
            <div class="pp-card card" v-for="pp in grouped[sev]" :key="pp.id">
              <div class="pp-header">
                <div>
                  <div class="pp-title">{{ pp.title }}</div>
                  <div class="pp-cat">{{ pp.category }}</div>
                </div>
                <span class="pp-effort">Effort: {{ pp.effort_to_fix }}</span>
              </div>
              <div class="pp-desc">{{ pp.description }}</div>
              <div v-if="pp.root_cause" class="pp-root">🔍 Root Cause: {{ pp.root_cause }}</div>
              <div v-if="pp.proposed_solution" class="pp-solution">✅ Solution: {{ pp.proposed_solution }}</div>
              <div v-if="pp.if_unresolved_impact" class="pp-impact">⚠ If unresolved: {{ pp.if_unresolved_impact }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="empty card"><p>Extract pain points to identify strategic friction.</p></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { scenariosApi } from '../api/scenarios.js'
import StepProgress from '../components/StepProgress.vue'

const route = useRoute()
const painPoints = ref([])
const extracting = ref(false)

const grouped = computed(() => {
  const g = { critical: [], high: [], medium: [], low: [] }
  for (const pp of painPoints.value) g[pp.severity]?.push(pp)
  return g
})

onMounted(async () => {
  const res = await scenariosApi.listPainPoints(route.params.id)
  painPoints.value = res.data || []
})

async function extract() {
  extracting.value = true
  try {
    await scenariosApi.extractPainPoints(route.params.id)
    setTimeout(async () => {
      const res = await scenariosApi.listPainPoints(route.params.id)
      painPoints.value = res.data || []
    }, 5000)
  } catch {} finally { extracting.value = false }
}
</script>

<style scoped>
.view-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px; }
.severity-group { margin-bottom: 28px; }
.severity-header { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
.count { font-size: 13px; color: var(--text-secondary); }
.pp-list { display: flex; flex-direction: column; gap: 12px; }
.pp-card { }
.pp-header { display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px; }
.pp-title { font-size: 15px; font-weight: 700; margin-bottom: 4px; }
.pp-cat { font-size: 12px; color: var(--text-secondary); }
.pp-effort { font-size: 12px; color: var(--text-secondary); }
.pp-desc { font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; }
.pp-root { font-size: 13px; color: var(--accent-amber); margin-bottom: 6px; }
.pp-solution { font-size: 13px; color: var(--accent-green); margin-bottom: 6px; }
.pp-impact { font-size: 13px; color: var(--accent-red); }
.empty { text-align: center; padding: 60px; color: var(--text-secondary); }
</style>
