import api from './index.js'

export const scenariosApi = {
  create: (data) => api.post('/scenarios', data),
  list: (skip = 0, limit = 50) => api.get('/scenarios', { params: { skip, limit } }),
  get: (id) => api.get(`/scenarios/${id}`),
  update: (id, data) => api.put(`/scenarios/${id}`, data),
  delete: (id) => api.delete(`/scenarios/${id}`),
  runAnalysis: (id) => api.post(`/scenarios/${id}/run-analysis`),
  getMetrics: (id) => api.get(`/scenarios/${id}/metrics`),
  exportJson: (id) => api.post(`/scenarios/${id}/export/json`, {}, { responseType: 'blob' }),
  exportPdf: (id) => api.post(`/scenarios/${id}/export/pdf`, {}, { responseType: 'blob' }),
  // Competitors
  addCompetitor: (id, data) => api.post(`/scenarios/${id}/competitors`, data),
  deleteCompetitor: (id, cid) => api.delete(`/scenarios/${id}/competitors/${cid}`),
  // Analysis
  runCompetitiveAnalysis: (id) => api.post(`/scenarios/${id}/analysis/run`),
  getAnalysis: (id) => api.get(`/scenarios/${id}/analysis`),
  // Personas
  buildPersonas: (id) => api.post(`/scenarios/${id}/personas/build`),
  listPersonas: (id) => api.get(`/scenarios/${id}/personas`),
  // Strategies
  generateStrategies: (id) => api.post(`/scenarios/${id}/strategies/generate`),
  listStrategies: (id) => api.get(`/scenarios/${id}/strategies`),
  getStrategyExplanation: (id, sid) => api.get(`/scenarios/${id}/strategies/${sid}/explanation`),
  // Pain Points
  extractPainPoints: (id) => api.post(`/scenarios/${id}/pain-points/extract`),
  listPainPoints: (id) => api.get(`/scenarios/${id}/pain-points`),
  // Roadmap
  buildRoadmap: (id) => api.post(`/scenarios/${id}/roadmap/build`),
  getRoadmap: (id) => api.get(`/scenarios/${id}/roadmap`),
  getWinProbability: (id) => api.get(`/scenarios/${id}/roadmap/probability`),
  // Simulation
  launchSimulation: (id) => api.post(`/scenarios/${id}/simulate`),
  getSimulationResults: (id) => api.get(`/scenarios/${id}/simulate/results`),
}

export const tasksApi = {
  get: (taskId) => api.get(`/tasks/${taskId}`),
}
