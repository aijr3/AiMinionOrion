<template>
  <div class="intake">
    <h1 class="page-title">New Scenario</h1>
    <p class="page-subtitle">Describe your situation. The app will apply 8 analytical frameworks to build your strategy.</p>

    <div class="intake-grid">
      <div class="form-panel card">
        <div class="form-step" v-show="step === 1">
          <h3 class="step-heading">1. What type of scenario is this?</h3>
          <div class="type-grid">
            <button
              v-for="t in scenarioTypes" :key="t.value"
              class="type-btn" :class="{ active: form.scenario_type === t.value }"
              @click="form.scenario_type = t.value"
            >
              <span>{{ t.icon }}</span> {{ t.label }}
            </button>
          </div>
          <div class="form-group">
            <label>Scenario Name</label>
            <input v-model="form.name" placeholder="e.g. Market Entry vs Competitor X, Negotiation with Partner Y" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Industry</label>
              <input v-model="form.industry" placeholder="e.g. SaaS, Retail, Politics" />
            </div>
            <div class="form-group">
              <label>Geography</label>
              <input v-model="form.geography" placeholder="e.g. US, Global, APAC" />
            </div>
            <div class="form-group">
              <label>Time Horizon</label>
              <input v-model="form.time_horizon" placeholder="e.g. Q3 2025 – Q2 2026" />
            </div>
          </div>
          <button class="btn btn-primary" @click="step = 2" :disabled="!form.name">Next →</button>
        </div>

        <div class="form-step" v-show="step === 2">
          <h3 class="step-heading">2. Describe the scenario</h3>
          <div class="form-group">
            <label>Brief Description</label>
            <textarea v-model="form.description" rows="3" placeholder="Summarize the situation in 2–3 sentences." />
          </div>
          <div class="form-group">
            <label>Market Context / Research (paste documents, data, news, competitor info)</label>
            <textarea v-model="form.market_context" rows="8"
              placeholder="Paste any research, market data, competitor info, news, or context. The more you provide, the more accurate the strategy." />
          </div>
          <div class="form-actions">
            <button class="btn btn-secondary" @click="step = 1">← Back</button>
            <button class="btn btn-primary" @click="step = 3">Next →</button>
          </div>
        </div>

        <div class="form-step" v-show="step === 3">
          <h3 class="step-heading">3. What are your goals?</h3>
          <div class="goals-list">
            <div class="goal-row" v-for="(g, i) in form.goals" :key="i">
              <input v-model="form.goals[i]" :placeholder="`Goal ${i + 1}`" />
              <button class="btn-remove" @click="removeGoal(i)">✕</button>
            </div>
          </div>
          <button class="btn btn-secondary" style="margin-bottom:20px" @click="addGoal">+ Add Goal</button>

          <div class="mirofish-toggle">
            <label class="toggle-label">
              <input type="checkbox" v-model="form.mirofish_enabled" />
              <span>Enable MiroFish AI simulation (multi-agent prediction)</span>
            </label>
          </div>

          <div class="form-actions">
            <button class="btn btn-secondary" @click="step = 2">← Back</button>
            <button class="btn btn-primary btn-lg" @click="submit" :disabled="submitting">
              {{ submitting ? 'Launching Analysis...' : '🚀 Launch Strategic Analysis' }}
            </button>
          </div>
        </div>
      </div>

      <div class="preview-panel">
        <div class="card preview-card">
          <div class="preview-label">Scenario Preview</div>
          <div class="preview-type">{{ typeLabel }}</div>
          <div class="preview-name">{{ form.name || 'Untitled Scenario' }}</div>
          <div class="preview-meta" v-if="form.industry">{{ form.industry }} · {{ form.geography }}</div>
          <div class="preview-horizon" v-if="form.time_horizon">⏱ {{ form.time_horizon }}</div>
          <div class="preview-goals" v-if="form.goals.filter(Boolean).length">
            <div class="preview-goals-label">Goals:</div>
            <div v-for="g in form.goals.filter(Boolean)" :key="g" class="preview-goal">→ {{ g }}</div>
          </div>
          <div class="frameworks-preview">
            <div class="frameworks-preview-label">Frameworks that will be applied:</div>
            <div class="fw-tag" v-for="fw in activeFrameworks" :key="fw">{{ fw }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { scenariosApi } from '../api/scenarios.js'

const router = useRouter()
const step = ref(1)
const submitting = ref(false)

const form = ref({
  name: '',
  description: '',
  market_context: '',
  goals: [''],
  scenario_type: 'business',
  industry: '',
  geography: '',
  time_horizon: '',
  mirofish_enabled: false,
})

const scenarioTypes = [
  { value: 'business', label: 'Business', icon: '🏢' },
  { value: 'political', label: 'Political', icon: '🏛' },
  { value: 'personal', label: 'Personal', icon: '👤' },
  { value: 'negotiation', label: 'Negotiation', icon: '🤝' },
  { value: 'product_launch', label: 'Product Launch', icon: '🚀' },
  { value: 'market_entry', label: 'Market Entry', icon: '🌍' },
]

const typeLabel = computed(() => scenarioTypes.find(t => t.value === form.value.scenario_type)?.label || '')
const activeFrameworks = ['Sun Tzu / OODA', '48 Laws of Power', 'MBTI Psychology', 'Google Ads / AIDA', "Porter's Five Forces", 'Bayesian Probability', 'Laws of Human Nature', 'Art of Seduction']

function addGoal() { form.value.goals.push('') }
function removeGoal(i) { form.value.goals.splice(i, 1) }

async function submit() {
  submitting.value = true
  try {
    const res = await scenariosApi.create({
      ...form.value,
      goals: form.value.goals.filter(Boolean),
    })
    const scenarioId = res.data.id
    await scenariosApi.runAnalysis(scenarioId)
    router.push(`/scenarios/${scenarioId}/dashboard`)
  } catch (e) {
    alert('Error: ' + e.message)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.intake { padding: 32px 0; }
.intake-grid { display: grid; grid-template-columns: 1fr 360px; gap: 24px; align-items: start; }
.form-panel { }
.step-heading { font-size: 18px; font-weight: 700; margin: 0 0 20px; }
.type-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 24px; }
.type-btn {
  background: var(--bg-secondary); border: 1px solid var(--border);
  color: var(--text-primary); padding: 12px; border-radius: 8px;
  cursor: pointer; font-size: 13px; display: flex; flex-direction: column; align-items: center; gap: 6px; transition: all 0.2s;
}
.type-btn.active { border-color: var(--accent-blue); background: rgba(59,130,246,0.1); color: var(--accent-blue); }
.type-btn span { font-size: 20px; }
.form-group { margin-bottom: 16px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
.form-actions { display: flex; gap: 12px; margin-top: 24px; }
.goals-list { display: flex; flex-direction: column; gap: 10px; margin-bottom: 16px; }
.goal-row { display: flex; gap: 8px; align-items: center; }
.btn-remove { background: transparent; border: 1px solid var(--border); color: var(--accent-red); width: 32px; height: 36px; border-radius: 6px; cursor: pointer; }
.mirofish-toggle { background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; padding: 12px 16px; margin-bottom: 20px; }
.toggle-label { display: flex; align-items: center; gap: 10px; font-size: 13px; cursor: pointer; }

.preview-card { position: sticky; top: 80px; }
.preview-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: var(--text-secondary); margin-bottom: 12px; }
.preview-type { font-size: 12px; color: var(--accent-blue); font-weight: 600; margin-bottom: 4px; }
.preview-name { font-size: 20px; font-weight: 700; margin-bottom: 8px; }
.preview-meta { font-size: 13px; color: var(--text-secondary); margin-bottom: 6px; }
.preview-horizon { font-size: 12px; color: var(--accent-green); margin-bottom: 16px; }
.preview-goals-label { font-size: 12px; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px; }
.preview-goal { font-size: 13px; margin-bottom: 4px; }
.frameworks-preview { margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--border); }
.frameworks-preview-label { font-size: 11px; color: var(--text-secondary); margin-bottom: 10px; }
.fw-tag { display: inline-block; background: rgba(59,130,246,0.1); border: 1px solid rgba(59,130,246,0.2); color: var(--accent-blue); font-size: 11px; padding: 3px 10px; border-radius: 20px; margin: 3px 4px 3px 0; }
</style>
