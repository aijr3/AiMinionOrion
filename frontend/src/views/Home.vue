<template>
  <div class="home">
    <!-- No API key warning -->
    <div v-if="!keySet" class="api-warning">
      <span class="warn-icon">⚠</span>
      <span>No OpenAI API key configured — the analysis pipeline won't run until you add one.</span>
      <button class="warn-btn" @click="showSettings = true">Add API Key</button>
    </div>

    <SettingsModal v-if="showSettings" @close="showSettings = false" @saved="onSaved" />

    <div class="hero">
      <div class="hero-badge">Universal Strategic Advisor</div>
      <h1 class="hero-title">Turn Any Scenario Into a<br /><span class="gradient-text">Winning Strategy</span></h1>
      <p class="hero-sub">
        Input your scenario. Receive a complete strategic analysis using Sun Tzu, Robert Greene's 48 Laws, MBTI psychology,
        Google Ads campaigns, Bayesian probability, and MiroFish AI simulation — all combined into one actionable playbook.
      </p>
      <div class="hero-actions">
        <RouterLink to="/scenarios/new" class="btn btn-primary btn-lg">Start New Scenario →</RouterLink>
        <RouterLink to="/scenarios" class="btn btn-secondary btn-lg">View Past Scenarios</RouterLink>
      </div>
    </div>

    <div class="frameworks-grid">
      <div class="framework-card" v-for="fw in frameworks" :key="fw.name">
        <div class="fw-icon">{{ fw.icon }}</div>
        <div class="fw-name">{{ fw.name }}</div>
        <div class="fw-desc">{{ fw.desc }}</div>
      </div>
    </div>

    <div v-if="recentScenarios.length" class="recent-section">
      <h2 class="section-title">Recent Scenarios</h2>
      <div class="scenarios-list">
        <div class="scenario-row" v-for="s in recentScenarios" :key="s.id" @click="openScenario(s)">
          <div class="scenario-info">
            <div class="scenario-name">{{ s.name }}</div>
            <div class="scenario-meta">{{ s.scenario_type }} · {{ s.industry || 'Unknown industry' }} · {{ s.geography || 'Global' }}</div>
          </div>
          <div class="scenario-right">
            <span class="badge" :class="`badge-${statusColor(s.status)}`">{{ s.status }}</span>
            <span class="scenario-date">{{ formatDate(s.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { scenariosApi } from '../api/scenarios.js'
import api from '../api/index.js'
import SettingsModal from '../components/SettingsModal.vue'

const router = useRouter()
const recentScenarios = ref([])
const keySet = ref(true)    // optimistic default (avoids flash)
const showSettings = ref(false)

function onSaved({ keySet: k }) { keySet.value = k }

const frameworks = [
  { icon: '⚔', name: 'War Strategy', desc: 'Sun Tzu Art of War, Clausewitz, OODA loop' },
  { icon: '👑', name: '48 Laws of Power', desc: 'Robert Greene — power dynamics & seduction' },
  { icon: '🧠', name: 'MBTI Psychology', desc: 'All 16 types — decision styles & intent modeling' },
  { icon: '📊', name: 'Google Ads / AIDA', desc: 'Funnel-based campaign planning' },
  { icon: '🎯', name: 'Target Research', desc: "Porter's Five Forces, TAM/SAM/SOM" },
  { icon: '🎲', name: 'Bayesian Stats', desc: 'Win probability + Monte Carlo simulation' },
  { icon: '🔮', name: 'MiroFish AI', desc: 'Multi-agent prediction engine' },
  { icon: '📖', name: 'Laws of Human Nature', desc: "Greene's 18 laws of irrational behavior" },
]

onMounted(async () => {
  try {
    const [scenRes, settRes] = await Promise.all([
      scenariosApi.list(0, 5),
      api.get('/settings'),
    ])
    recentScenarios.value = scenRes.data || []
    keySet.value = (settRes.data || settRes).llm_api_key_set || false
  } catch {}
})

function openScenario(s) {
  router.push(`/scenarios/${s.id}/dashboard`)
}

function statusColor(status) {
  return { created: 'medium', analyzing: 'high', ready: 'win', archived: 'exit' }[status] || 'medium'
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString()
}
</script>

<style scoped>
.home { padding: 48px 0; }

.api-warning {
  display: flex; align-items: center; gap: 12px;
  background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.3);
  border-radius: 10px; padding: 14px 20px; margin-bottom: 32px;
  color: var(--accent-amber); font-size: 14px;
}
.warn-icon { font-size: 18px; flex-shrink: 0; }
.api-warning span:nth-child(2) { flex: 1; }
.warn-btn {
  background: var(--accent-amber); color: #0a0e1a;
  border: none; border-radius: 6px; padding: 7px 14px;
  font-size: 13px; font-weight: 700; cursor: pointer;
  white-space: nowrap; transition: opacity 0.2s;
}
.warn-btn:hover { opacity: 0.9; }
.hero { text-align: center; padding: 60px 20px; max-width: 800px; margin: 0 auto 64px; }
.hero-badge {
  display: inline-block; background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.3);
  color: var(--accent-blue); padding: 6px 18px; border-radius: 20px; font-size: 13px; font-weight: 600; margin-bottom: 24px;
}
.hero-title { font-size: 52px; font-weight: 900; line-height: 1.1; margin: 0 0 20px; }
.gradient-text { background: linear-gradient(135deg, #3b82f6, #8b5cf6, #d4af37); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-sub { font-size: 18px; color: var(--text-secondary); line-height: 1.6; margin: 0 0 36px; }
.hero-actions { display: flex; gap: 16px; justify-content: center; }
.btn-lg { padding: 14px 28px; font-size: 16px; }

.frameworks-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 64px; }
.framework-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }
.fw-icon { font-size: 24px; margin-bottom: 10px; }
.fw-name { font-size: 14px; font-weight: 700; margin-bottom: 6px; }
.fw-desc { font-size: 12px; color: var(--text-secondary); line-height: 1.5; }

.recent-section { }
.scenarios-list { display: flex; flex-direction: column; gap: 12px; }
.scenario-row {
  display: flex; align-items: center; justify-content: space-between;
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px;
  padding: 16px 20px; cursor: pointer; transition: border-color 0.2s;
}
.scenario-row:hover { border-color: var(--accent-blue); }
.scenario-name { font-weight: 600; margin-bottom: 4px; }
.scenario-meta { font-size: 12px; color: var(--text-secondary); }
.scenario-right { display: flex; align-items: center; gap: 16px; }
.scenario-date { font-size: 12px; color: var(--text-secondary); }
</style>
