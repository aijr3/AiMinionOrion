<template>
  <div class="history-view">
    <div class="view-header">
      <div><h1 class="page-title">All Scenarios</h1></div>
      <RouterLink to="/scenarios/new" class="btn btn-primary">+ New Scenario</RouterLink>
    </div>
    <div class="scenarios-table card" v-if="scenarios.length">
      <div class="table-row table-header">
        <span>Name</span><span>Type</span><span>Industry</span><span>Status</span><span>Created</span><span></span>
      </div>
      <div class="table-row" v-for="s in scenarios" :key="s.id">
        <span class="row-name">{{ s.name }}</span>
        <span>{{ s.scenario_type }}</span>
        <span>{{ s.industry || '—' }}</span>
        <span><span class="badge" :class="`badge-${statusColor(s.status)}`">{{ s.status }}</span></span>
        <span style="font-size:12px;color:var(--text-secondary)">{{ formatDate(s.created_at) }}</span>
        <span><RouterLink :to="`/scenarios/${s.id}/dashboard`" class="btn btn-secondary" style="font-size:12px;padding:6px 12px">Open →</RouterLink></span>
      </div>
    </div>
    <div v-else class="empty card">No scenarios yet. <RouterLink to="/scenarios/new">Create one →</RouterLink></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { scenariosApi } from '../api/scenarios.js'

const scenarios = ref([])
onMounted(async () => {
  const res = await scenariosApi.list()
  scenarios.value = res.data || []
})
function statusColor(s) { return { created: 'medium', analyzing: 'high', ready: 'win', archived: 'exit' }[s] || 'medium' }
function formatDate(iso) { return iso ? new Date(iso).toLocaleDateString() : '' }
</script>

<style scoped>
.view-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px; }
.scenarios-table { padding: 0; overflow: hidden; }
.table-row { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr 100px; gap: 16px; padding: 14px 20px; align-items: center; border-bottom: 1px solid var(--border); }
.table-row:last-child { border-bottom: none; }
.table-header { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-secondary); background: var(--bg-secondary); }
.row-name { font-weight: 600; }
.empty { text-align: center; padding: 60px; color: var(--text-secondary); }
</style>
