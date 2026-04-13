<template>
  <div class="greene-view">
    <StepProgress :scenario-id="$route.params.id" current-step="greene" />
    <h1 class="page-title" style="color:var(--accent-gold)">Robert Greene Analysis</h1>
    <p class="page-subtitle">The full Greene library applied to your scenario — power, seduction, war strategy, and human nature.</p>

    <div v-if="loading" class="loading">Applying Robert Greene frameworks…</div>

    <div v-else-if="data" class="greene-content">
      <!-- 48 Laws of Power -->
      <section class="greene-section">
        <h2 class="section-title">⚡ The 48 Laws of Power</h2>
        <div class="laws-tabs">
          <button :class="{ active: lawsTab === 'active' }" @click="lawsTab='active'">Active Laws ({{ activeLaws.length }})</button>
          <button :class="{ active: lawsTab === 'opponent' }" @click="lawsTab='opponent'">Opponent Using ({{ opponentLaws.length }})</button>
          <button :class="{ active: lawsTab === 'recommended' }" @click="lawsTab='recommended'">Recommended for Us ({{ recommendedLaws.length }})</button>
        </div>
        <div class="laws-grid">
          <div class="law-card card" v-for="law in currentLaws" :key="law.law_number">
            <div class="law-number">Law {{ law.law_number }}</div>
            <div class="law-name">{{ law.law_name }}</div>
            <div class="law-detail" v-if="lawsTab === 'active'">{{ law.how_applied }}</div>
            <div class="law-detail" v-if="lawsTab === 'opponent'">{{ law.how_used_against_us }}<br/><span class="counter">Counter: {{ law.counter_move }}</span></div>
            <div class="law-detail" v-if="lawsTab === 'recommended'">{{ law.tactical_application }}<br/><span class="risk-text">⚠ {{ law.risk_if_misapplied }}</span></div>
          </div>
        </div>
      </section>

      <!-- 33 Strategies of War -->
      <section class="greene-section" v-if="warStrategies.length">
        <h2 class="section-title">⚔ 33 Strategies of War</h2>
        <div class="war-list">
          <div class="war-item card" v-for="ws in warStrategies" :key="ws.strategy_number">
            <div class="war-number">Strategy {{ ws.strategy_number }}</div>
            <div class="war-name">{{ ws.strategy_name }}</div>
            <div class="war-app">{{ ws.application }}</div>
            <div class="war-tactic">→ {{ ws.specific_tactic }}</div>
          </div>
        </div>
      </section>

      <!-- Art of Seduction -->
      <section class="greene-section" v-if="seduction">
        <h2 class="section-title">🌹 Art of Seduction</h2>
        <div class="seduction-grid">
          <div class="card seduction-role">
            <div class="sed-label">Our Seducer Role</div>
            <div class="sed-role">{{ seduction.our_seducer_role }}</div>
            <div class="sed-rationale">{{ seduction.seducer_role_rationale }}</div>
          </div>
          <div v-for="target in (seduction.key_targets || [])" :key="target.target_name" class="card">
            <div class="sed-label">{{ target.target_name }}</div>
            <div class="sed-type">Victim Type: {{ target.target_victim_type }}</div>
            <div class="sed-approach">{{ target.seduction_approach }}</div>
          </div>
        </div>
        <div v-if="seduction.anti_seduction_warnings?.length" class="warnings">
          <div class="warnings-title">⚠ Anti-Seduction Warnings</div>
          <div v-for="w in seduction.anti_seduction_warnings" :key="w" class="warning-item">{{ w }}</div>
        </div>
      </section>

      <!-- Laws of Human Nature -->
      <section class="greene-section" v-if="humanNature.length">
        <h2 class="section-title">🧬 Laws of Human Nature</h2>
        <div class="nature-list">
          <div class="nature-item card" v-for="law in humanNature" :key="law.law_number">
            <div class="nature-header">
              <div class="nature-number">Law {{ law.law_number }}</div>
              <div class="nature-name">{{ law.law_name }}</div>
            </div>
            <div class="nature-explains">{{ law.how_it_explains_behavior }}</div>
            <div class="nature-counter">Strategy: {{ law.counter_strategy }}</div>
          </div>
        </div>
      </section>

      <!-- Mastery + 50th Law -->
      <div class="mastery-grid">
        <section class="greene-section card" v-if="mastery">
          <h2 class="section-title" style="font-size:18px">📚 Mastery Phase</h2>
          <div class="mastery-phase" :class="`phase-${mastery.current_phase}`">{{ mastery.current_phase?.replace('_', ' ').toUpperCase() }}</div>
          <div class="mastery-text">{{ mastery.phase_rationale }}</div>
          <div class="mastery-rec">{{ mastery.phase_recommendation }}</div>
        </section>

        <section class="greene-section card" v-if="law50">
          <h2 class="section-title" style="font-size:18px">⚡ The 50th Law — Fearlessness</h2>
          <div class="law50-fear">Fear Assessment: {{ law50.fear_assessment }}</div>
          <div class="law50-moves">
            <div class="moves-title">Fearlessness Moves:</div>
            <div v-for="move in (law50.fearlessness_moves || [])" :key="move" class="move-item">→ {{ move }}</div>
          </div>
          <div class="law50-accept">Accept: {{ law50.worst_case_acceptance }}</div>
        </section>
      </div>

      <!-- Daily Laws -->
      <section class="greene-section" v-if="dailyLaws.length">
        <h2 class="section-title">📅 Daily Laws — Today's Focus</h2>
        <div class="daily-grid">
          <div class="daily-card card" v-for="dl in dailyLaws" :key="dl.law_reference">
            <div class="daily-ref">{{ dl.law_reference }}</div>
            <div class="daily-reminder">{{ dl.daily_reminder }}</div>
          </div>
        </div>
      </section>
    </div>
    <div v-else class="empty-state card">
      <p>Run the full analysis to generate Robert Greene framework insights.</p>
      <RouterLink :to="`/scenarios/${$route.params.id}/dashboard`" class="btn btn-primary">Go to Dashboard</RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { scenariosApi } from '../api/scenarios.js'
import StepProgress from '../components/StepProgress.vue'

const route = useRoute()
const loading = ref(true)
const data = ref(null)
const lawsTab = ref('recommended')

onMounted(async () => {
  try {
    const res = await scenariosApi.getAnalysis(route.params.id)
    const frameworks = res.data?.framework_summaries || []
    const greeneFa = frameworks.find(f => f.type === 'robert_greene')
    if (greeneFa?.raw_output) {
      data.value = typeof greeneFa.raw_output === 'string' ? JSON.parse(greeneFa.raw_output) : greeneFa.raw_output
    }
  } catch {} finally {
    loading.value = false
  }
})

const activeLaws = computed(() => data.value?.laws_of_power?.active_laws || [])
const opponentLaws = computed(() => data.value?.laws_of_power?.opponent_laws_being_used || [])
const recommendedLaws = computed(() => data.value?.laws_of_power?.recommended_laws_for_us || [])
const warStrategies = computed(() => data.value?.strategies_of_war || [])
const seduction = computed(() => data.value?.art_of_seduction || null)
const humanNature = computed(() => data.value?.laws_of_human_nature || [])
const mastery = computed(() => data.value?.mastery_assessment || null)
const law50 = computed(() => data.value?.fiftieth_law || null)
const dailyLaws = computed(() => data.value?.daily_laws || [])
const currentLaws = computed(() => ({ active: activeLaws.value, opponent: opponentLaws.value, recommended: recommendedLaws.value }[lawsTab.value] || []))
</script>

<style scoped>
.greene-view { padding: 32px 0; }
.greene-section { margin-bottom: 40px; }
.laws-tabs { display: flex; gap: 8px; margin-bottom: 20px; }
.laws-tabs button { background: var(--bg-secondary); border: 1px solid var(--border); color: var(--text-secondary); padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; }
.laws-tabs button.active { border-color: var(--accent-gold); color: var(--accent-gold); background: rgba(212,175,55,0.1); }
.laws-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.law-card { border-left: 3px solid var(--accent-gold); }
.law-number { font-size: 11px; color: var(--accent-gold); font-weight: 700; margin-bottom: 4px; }
.law-name { font-size: 14px; font-weight: 700; margin-bottom: 8px; }
.law-detail { font-size: 13px; color: var(--text-secondary); line-height: 1.5; }
.counter { color: var(--accent-green); font-size: 12px; }
.risk-text { color: var(--accent-red); font-size: 12px; }
.war-list { display: flex; flex-direction: column; gap: 12px; }
.war-item { }
.war-number { font-size: 11px; color: var(--accent-purple); font-weight: 700; }
.war-name { font-size: 15px; font-weight: 700; margin-bottom: 6px; }
.war-app { font-size: 13px; color: var(--text-secondary); margin-bottom: 6px; }
.war-tactic { font-size: 13px; color: var(--accent-blue); }
.seduction-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px; }
.sed-label { font-size: 11px; color: var(--text-secondary); margin-bottom: 4px; }
.sed-role { font-size: 18px; font-weight: 800; color: var(--accent-gold); margin-bottom: 8px; }
.sed-rationale, .sed-approach { font-size: 13px; color: var(--text-secondary); }
.sed-type { font-size: 12px; color: var(--accent-purple); margin-bottom: 4px; }
.warnings { background: rgba(239,68,68,0.05); border: 1px solid rgba(239,68,68,0.2); border-radius: 8px; padding: 14px; }
.warnings-title { font-size: 13px; font-weight: 600; color: var(--accent-red); margin-bottom: 8px; }
.warning-item { font-size: 12px; color: var(--text-secondary); margin-bottom: 4px; }
.nature-list { display: flex; flex-direction: column; gap: 12px; }
.nature-item { }
.nature-header { display: flex; gap: 10px; align-items: baseline; margin-bottom: 6px; }
.nature-number { font-size: 11px; color: var(--accent-gold); font-weight: 700; }
.nature-name { font-size: 14px; font-weight: 700; }
.nature-explains { font-size: 13px; color: var(--text-secondary); margin-bottom: 6px; }
.nature-counter { font-size: 13px; color: var(--accent-green); }
.mastery-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 40px; }
.mastery-phase { font-size: 24px; font-weight: 800; color: var(--accent-blue); margin-bottom: 12px; }
.phase-mastery { color: var(--accent-gold) !important; }
.phase-creative_active { color: var(--accent-purple) !important; }
.mastery-text, .mastery-rec { font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; }
.law50-fear { font-size: 13px; color: var(--accent-amber); margin-bottom: 12px; }
.moves-title { font-size: 12px; font-weight: 600; margin-bottom: 6px; }
.move-item { font-size: 13px; color: var(--text-secondary); margin-bottom: 4px; }
.law50-accept { font-size: 12px; color: var(--accent-purple); margin-top: 10px; font-style: italic; }
.daily-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.daily-card { border-top: 3px solid var(--accent-gold); }
.daily-ref { font-size: 12px; color: var(--accent-gold); font-weight: 700; margin-bottom: 8px; }
.daily-reminder { font-size: 14px; color: var(--text-primary); line-height: 1.6; }
.loading { color: var(--text-secondary); padding: 40px; text-align: center; }
.empty-state { text-align: center; padding: 60px 40px; }
</style>
