import { reactive } from 'vue'

export const scenarioStore = reactive({
  current: null,
  list: [],
  loading: false,
  error: null,

  setCurrent(scenario) {
    this.current = scenario
  },

  setList(scenarios) {
    this.list = scenarios
  },

  setLoading(val) {
    this.loading = val
  },

  setError(msg) {
    this.error = msg
  },

  clear() {
    this.current = null
    this.error = null
  },
})

export const analysisStore = reactive({
  competitors: [],
  personas: [],
  strategies: [],
  painPoints: [],
  roadmap: { win_path: [], graceful_forward_path: [] },
  frameworks: [],
  metrics: null,
  simulationResults: null,
  activeTask: null,

  reset() {
    this.competitors = []
    this.personas = []
    this.strategies = []
    this.painPoints = []
    this.roadmap = { win_path: [], graceful_forward_path: [] }
    this.frameworks = []
    this.metrics = null
    this.simulationResults = null
    this.activeTask = null
  },
})
