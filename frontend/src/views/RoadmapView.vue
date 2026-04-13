<template>
  <div class="roadmap-view">
    <StepProgress :scenario-id="$route.params.id" current-step="roadmap" />
    <div class="view-header">
      <div><h1 class="page-title">Victory Roadmap</h1><p class="page-subtitle">Step-by-step milestones with cumulative Bayesian probability scores.</p></div>
      <div class="view-actions">
        <div class="path-toggle">
          <button :class="{ active: path === 'win' }" @click="path='win'">⚔ Win Path</button>
          <button :class="{ active: path === 'graceful_forward' }" @click="path='graceful_forward'">🕊 Graceful Forward</button>
        </div>
        <button class="btn btn-primary" @click="buildRoadmap" :disabled="building">{{ building ? 'Building…' : '+ Build Roadmap' }}</button>
      </div>
    </div>

    <div v-if="currentPath.length" class="roadmap-stats card">
      <div class="stat">
        <div class="stat-label">Steps</div>
        <div class="stat-val">{{ currentPath.length }}</div>
      </div>
      <div class="stat">
        <div class="stat-label">Final Probability</div>
        <div class="stat-val" :style="{ color: probColor(finalProb) }">{{ pct(finalProb) }}</div>
      </div>
      <div class="stat">
        <div class="stat-label">Completed</div>
        <div class="stat-val">{{ completedCount }} / {{ currentPath.length }}</div>
      </div>
    </div>

    <div class="roadmap-steps" v-if="currentPath.length">
      <div
        class="step-item card"
        v-for="step in currentPath"
        :key="step.id"
        :class="{ 'step-complete': step.is_complete }"
      >
        <div class="step-left">
          <div class="step-num" :class="{ 'num-complete': step.is_complete }">{{ step.step_number }}</div>
          <div v-if="step.step_number < currentPath.length" class="step-line" />
        </div>
        <div class="step-body">
          <div class="step-header">
            <div>
              <div class="step-title">{{ step.title }}</div>
              <div class="step-milestone">📌 {{ step.milestone }}</div>
            </div>
            <div class="step-probs">
              <div class="prob-pair">
                <span class="prob-label">Step</span>
                <span class="prob-val" :style="{ color: probColor(step.probability_of_success) }">{{ pct(step.probability_of_success) }}</span>
              </div>
              <div class="prob-pair">
                <span class="prob-label">Cumulative</span>
                <span class="prob-val" :style="{ color: probColor(step.cumulative_probability) }">{{ pct(step.cumulative_probability) }}</span>
              </div>
            </div>
          </div>
          <div class="step-desc">{{ step.description }}</div>
          <div class="step-meta">
            <span v-if="step.owner">👤 {{ step.owner }}</span>
            <span v-if="step.estimated_duration">⏱ {{ step.estimated_duration }}</span>
          </div>
          <div v-if="step.probability_rationale" class="step-rationale">{{ step.probability_rationale }}</div>
          <div class="step-actions">
            <button
              class="btn btn-secondary"
              style="font-size:12px;padding:6px 12px"
              @click="toggleComplete(step)"
            >{{ step.is_complete ? '✓ Mark Incomplete' : 'Mark Complete' }}</button>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="empty card"><p>Build the roadmap to see your path to victory.</p></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { scenariosApi } from '../api/scenarios.js'
import StepProgress from '../components/StepProgress.vue'
import api from '../api/index.js'

const route = useRoute()
const roadmap = ref({ win_path: [], graceful_forward_path: [] })
const path = ref('win')
const building = ref(false)

const currentPath = computed(() =>
  path.value === 'win' ? roadmap.value.win_path : roadmap.value.graceful_forward_path
)
const finalProb = computed(() => currentPath.value.at(-1)?.cumulative_probability ?? null)
const completedCount = computed(() => currentPath.value.filter(s => s.is_complete).length)

onMounted(load)

async function load() {
  const res = await scenariosApi.getRoadmap(route.params.id)
  roadmap.value = res.data || { win_path: [], graceful_forward_path: [] }
}

async function buildRoadmap() {
  building.value = true
  try {
    await scenariosApi.buildRoadmap(route.params.id)
    setTimeout(load, 5000)
  } catch {} finally { building.value = false }
}

async function toggleComplete(step) {
  await api.put(`/scenarios/${route.params.id}/roadmap/steps/${step.id}`, { is_complete: !step.is_complete })
  step.is_complete = !step.is_complete
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
.roadmap-stats { display: flex; gap: 40px; padding: 20px; margin-bottom: 24px; }
.stat-label { font-size: 11px; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.stat-val { font-size: 24px; font-weight: 800; }
.roadmap-steps { display: flex; flex-direction: column; gap: 0; }
.step-item { display: flex; gap: 0; padding: 0; margin-bottom: 0; border: none; background: transparent; }
.step-left { display: flex; flex-direction: column; align-items: center; width: 48px; padding-top: 20px; }
.step-num {
  width: 36px; height: 36px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  background: var(--bg-card); border: 2px solid var(--border);
  font-size: 14px; font-weight: 700; z-index: 1; flex-shrink: 0;
}
.num-complete { background: var(--accent-green); border-color: var(--accent-green); color: white; }
.step-line { width: 2px; background: var(--border); flex: 1; min-height: 40px; }
.step-body { flex: 1; background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; margin: 8px 0 8px 16px; }
.step-complete .step-body { border-color: var(--accent-green); opacity: 0.8; }
.step-header { display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px; }
.step-title { font-size: 16px; font-weight: 700; margin-bottom: 4px; }
.step-milestone { font-size: 12px; color: var(--accent-blue); }
.step-probs { display: flex; gap: 20px; }
.prob-pair { display: flex; flex-direction: column; align-items: center; }
.prob-label { font-size: 10px; color: var(--text-secondary); }
.prob-val { font-size: 18px; font-weight: 800; }
.step-desc { font-size: 13px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 10px; }
.step-meta { display: flex; gap: 16px; font-size: 12px; color: var(--text-secondary); margin-bottom: 8px; }
.step-rationale { font-size: 12px; color: var(--text-secondary); font-style: italic; margin-bottom: 10px; }
.step-actions { }
.empty { text-align: center; padding: 60px; color: var(--text-secondary); }
</style>
