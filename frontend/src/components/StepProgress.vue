<template>
  <div class="step-progress">
    <div
      v-for="(step, i) in steps"
      :key="step.key"
      class="step-item"
      :class="{ active: currentStep === step.key, done: isDone(step.key) }"
      @click="$emit('navigate', step.key)"
    >
      <div class="step-dot">{{ i + 1 }}</div>
      <span class="step-label">{{ step.label }}</span>
      <div v-if="i < steps.length - 1" class="step-connector" />
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const props = defineProps({ scenarioId: String, currentStep: String })
defineEmits(['navigate'])

const steps = [
  { key: 'analysis', label: 'Analysis' },
  { key: 'frameworks', label: 'Frameworks' },
  { key: 'personas', label: 'Personas' },
  { key: 'strategy', label: 'Strategy' },
  { key: 'pain-points', label: 'Pain Points' },
  { key: 'campaigns', label: 'Campaigns' },
  { key: 'roadmap', label: 'Roadmap' },
  { key: 'dashboard', label: 'Dashboard' },
]

const stepOrder = steps.map(s => s.key)
function isDone(key) {
  return stepOrder.indexOf(key) < stepOrder.indexOf(props.currentStep)
}
</script>

<style scoped>
.step-progress { display: flex; align-items: center; gap: 0; padding: 16px 0; overflow-x: auto; }
.step-item {
  display: flex; align-items: center; gap: 8px;
  cursor: pointer; opacity: 0.5; transition: opacity 0.2s; white-space: nowrap;
}
.step-item.active { opacity: 1; }
.step-item.done { opacity: 0.8; }
.step-dot {
  width: 28px; height: 28px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700;
  background: var(--border); color: var(--text-secondary);
  transition: all 0.2s;
}
.step-item.active .step-dot { background: var(--accent-blue); color: white; }
.step-item.done .step-dot { background: var(--accent-green); color: white; }
.step-label { font-size: 13px; font-weight: 600; }
.step-connector { width: 32px; height: 2px; background: var(--border); margin: 0 4px; }
</style>
