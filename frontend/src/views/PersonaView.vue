<template>
  <div class="persona-view">
    <StepProgress :scenario-id="$route.params.id" current-step="personas" />
    <div class="view-header">
      <div><h1 class="page-title">MBTI Personas</h1><p class="page-subtitle">Psychologically profiled stakeholders with decision styles, intent signals, and seduction types.</p></div>
      <button class="btn btn-primary" @click="buildPersonas" :disabled="building">{{ building ? 'Building…' : '+ Build Personas' }}</button>
    </div>

    <div class="persona-filters">
      <button v-for="t in types" :key="t" class="filter-btn" :class="{ active: typeFilter === t }" @click="typeFilter = t">{{ t }}</button>
    </div>

    <div class="personas-grid" v-if="filteredPersonas.length">
      <div class="persona-card card" v-for="p in filteredPersonas" :key="p.id" @click="selected=p">
        <div class="persona-header">
          <div class="mbti-circle" :class="`mbti-${temperament(p.mbti_type)}`">{{ p.mbti_type || '?' }}</div>
          <div class="type-badge badge" :class="`badge-${typeColor(p.persona_type)}`">{{ p.persona_type }}</div>
        </div>
        <div class="persona-name">{{ p.name }}</div>
        <div class="persona-role">{{ p.role }}</div>
        <div v-if="p.seduction_type" class="seduction-type">🌹 {{ p.seduction_type }}</div>
        <div class="influence-bar">
          <div class="prob-bar">
            <div class="prob-fill" :style="{ width: ((p.influence_score||0)*100)+'%', background: 'var(--accent-purple)' }" />
          </div>
          <span class="influence-label">Influence {{ Math.round((p.influence_score||0)*100) }}%</span>
        </div>
      </div>
    </div>
    <div v-else class="empty card"><p>No personas yet. Build personas to see MBTI profiles.</p></div>

    <!-- Persona Modal -->
    <div class="modal-overlay" v-if="selected" @click.self="selected=null">
      <div class="modal-panel card">
        <div class="modal-header">
          <div class="modal-title">{{ selected.name }}</div>
          <button class="btn-close" @click="selected=null">✕</button>
        </div>
        <div class="modal-body">
          <div class="profile-grid">
            <div class="profile-item"><span class="pi-label">MBTI</span><span class="pi-val">{{ selected.mbti_type }}</span></div>
            <div class="profile-item"><span class="pi-label">Type</span><span class="pi-val">{{ selected.persona_type }}</span></div>
            <div class="profile-item"><span class="pi-label">Role</span><span class="pi-val">{{ selected.role }}</span></div>
            <div class="profile-item"><span class="pi-label">Age</span><span class="pi-val">{{ selected.age_range }}</span></div>
            <div class="profile-item"><span class="pi-label">Seduction Type</span><span class="pi-val" style="color:var(--accent-gold)">{{ selected.seduction_type }}</span></div>
            <div class="profile-item"><span class="pi-label">Influence</span><span class="pi-val">{{ Math.round((selected.influence_score||0)*100) }}%</span></div>
          </div>
          <div class="bio" v-if="selected.bio">{{ selected.bio }}</div>
          <div class="modal-section" v-if="selected.mbti_reasoning">
            <div class="ms-title">MBTI Reasoning</div><div class="ms-content">{{ selected.mbti_reasoning }}</div>
          </div>
          <div class="modal-section" v-if="selected.decision_style">
            <div class="ms-title">Decision Style</div><div class="ms-content">{{ selected.decision_style }}</div>
          </div>
          <div class="modal-section" v-if="selected.stress_reaction">
            <div class="ms-title">Under Stress</div><div class="ms-content">{{ selected.stress_reaction }}</div>
          </div>
          <div class="lists-grid">
            <div v-if="selected.goals?.length"><div class="ms-title">Goals</div><div v-for="g in selected.goals" :key="g" class="list-item">→ {{ g }}</div></div>
            <div v-if="selected.objections?.length"><div class="ms-title">Objections</div><div v-for="o in selected.objections" :key="o" class="list-item">⚠ {{ o }}</div></div>
          </div>
        </div>
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
const personas = ref([])
const selected = ref(null)
const building = ref(false)
const typeFilter = ref('all')
const types = ['all', 'customer', 'opponent', 'ally', 'neutral']

const filteredPersonas = computed(() =>
  typeFilter.value === 'all' ? personas.value : personas.value.filter(p => p.persona_type === typeFilter.value)
)

onMounted(async () => {
  const res = await scenariosApi.listPersonas(route.params.id)
  personas.value = res.data || []
})

async function buildPersonas() {
  building.value = true
  try {
    await scenariosApi.buildPersonas(route.params.id)
    setTimeout(async () => {
      const res = await scenariosApi.listPersonas(route.params.id)
      personas.value = res.data || []
    }, 5000)
  } catch {} finally { building.value = false }
}

function temperament(mbti) {
  if (!mbti) return 'unknown'
  const first = mbti[0]
  return { I: 'analyst', E: 'diplomat', S: 'sentinel', N: 'explorer' }[first] || 'unknown'
}
function typeColor(t) { return { customer: 'win', opponent: 'critical', ally: 'medium', neutral: 'low' }[t] || 'medium' }
</script>

<style scoped>
.view-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px; }
.persona-filters { display: flex; gap: 8px; margin-bottom: 24px; }
.filter-btn { background: var(--bg-secondary); border: 1px solid var(--border); color: var(--text-secondary); padding: 6px 14px; border-radius: 20px; cursor: pointer; font-size: 13px; }
.filter-btn.active { border-color: var(--accent-blue); color: var(--accent-blue); background: rgba(59,130,246,0.1); }
.personas-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.persona-card { cursor: pointer; transition: border-color 0.2s; }
.persona-card:hover { border-color: var(--accent-blue); }
.persona-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.mbti-circle { width: 44px; height: 44px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 800; }
.mbti-analyst { background: rgba(59,130,246,0.2); color: var(--accent-blue); }
.mbti-diplomat { background: rgba(16,185,129,0.2); color: var(--accent-green); }
.mbti-sentinel { background: rgba(245,158,11,0.2); color: var(--accent-amber); }
.mbti-explorer { background: rgba(139,92,246,0.2); color: var(--accent-purple); }
.mbti-unknown { background: var(--border); color: var(--text-secondary); }
.persona-name { font-size: 16px; font-weight: 700; margin-bottom: 4px; }
.persona-role { font-size: 12px; color: var(--text-secondary); margin-bottom: 8px; }
.seduction-type { font-size: 12px; color: var(--accent-gold); margin-bottom: 10px; }
.influence-bar { display: flex; flex-direction: column; gap: 4px; }
.influence-label { font-size: 11px; color: var(--text-secondary); }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 200; display: flex; align-items: center; justify-content: center; padding: 40px; }
.modal-panel { width: 100%; max-width: 720px; max-height: 85vh; overflow-y: auto; }
.modal-header { display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px; }
.modal-title { font-size: 22px; font-weight: 700; }
.btn-close { background: none; border: 1px solid var(--border); color: var(--text-primary); width: 32px; height: 32px; border-radius: 6px; cursor: pointer; }
.profile-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px; }
.profile-item { background: var(--bg-secondary); border-radius: 8px; padding: 10px; }
.pi-label { display: block; font-size: 11px; color: var(--text-secondary); margin-bottom: 4px; }
.pi-val { font-size: 14px; font-weight: 600; }
.bio { font-size: 14px; line-height: 1.8; color: var(--text-secondary); margin-bottom: 20px; }
.modal-section { margin-bottom: 16px; }
.ms-title { font-size: 12px; font-weight: 700; color: var(--accent-blue); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
.ms-content { font-size: 13px; color: var(--text-secondary); line-height: 1.6; }
.lists-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 16px; }
.list-item { font-size: 13px; color: var(--text-secondary); margin-bottom: 4px; }
.empty { text-align: center; padding: 60px; color: var(--text-secondary); }
</style>
