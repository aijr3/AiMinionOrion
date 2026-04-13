<template>
  <Teleport to="body">
    <div class="modal-backdrop" @click.self="$emit('close')">
      <div class="modal-box">
        <div class="modal-header">
          <div class="modal-title">
            <span class="modal-icon">⚙</span>
            API Settings
          </div>
          <button class="close-btn" @click="$emit('close')">✕</button>
        </div>

        <div class="modal-body">
          <!-- Status banner -->
          <div class="status-banner" :class="keySet ? 'banner-ok' : 'banner-warn'">
            <span class="status-dot" :class="keySet ? 'dot-green' : 'dot-amber'" />
            <span v-if="keySet">OpenAI API key configured — {{ maskedKey }}</span>
            <span v-else>No API key set. The app cannot run analysis without a key.</span>
          </div>

          <div class="field-group">
            <label>OpenAI API Key</label>
            <div class="input-row">
              <input
                :type="showKey ? 'text' : 'password'"
                v-model="form.apiKey"
                placeholder="sk-..."
                autocomplete="off"
                class="key-input"
              />
              <button class="toggle-btn" @click="showKey = !showKey" type="button">
                {{ showKey ? '🙈' : '👁' }}
              </button>
            </div>
            <div class="field-hint">
              Your key is stored server-side in <code>uploads/app_settings.json</code> and never sent to the browser after saving.
            </div>
          </div>

          <div class="field-group">
            <label>Base URL <span class="optional">(OpenAI-compatible, optional)</span></label>
            <input
              type="text"
              v-model="form.baseUrl"
              placeholder="https://api.openai.com/v1"
            />
            <div class="field-hint">Change only if using a proxy or alternative provider (e.g., Azure, Groq, Ollama).</div>
          </div>

          <div class="field-group">
            <label>Model Name</label>
            <div class="model-row">
              <select v-model="form.modelName">
                <option value="gpt-4o">gpt-4o</option>
                <option value="gpt-4o-mini">gpt-4o-mini</option>
                <option value="gpt-4-turbo">gpt-4-turbo</option>
                <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
                <option value="o1">o1</option>
                <option value="o1-mini">o1-mini</option>
                <option value="custom">Custom…</option>
              </select>
              <input
                v-if="form.modelName === 'custom'"
                type="text"
                v-model="form.customModel"
                placeholder="e.g. claude-3-5-sonnet"
                class="custom-model-input"
              />
            </div>
          </div>

          <!-- Test result -->
          <div v-if="testResult" class="test-result" :class="testResult.success ? 'test-ok' : 'test-fail'">
            <span v-if="testResult.success">✓ Connection successful</span>
            <span v-else>✗ {{ testResult.error }}</span>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="testConnection" :disabled="saving || testing">
            {{ testing ? 'Testing…' : '🔌 Test Connection' }}
          </button>
          <div class="footer-right">
            <button class="btn btn-secondary" @click="$emit('close')" :disabled="saving">Cancel</button>
            <button class="btn btn-primary" @click="save" :disabled="saving || testing">
              {{ saving ? 'Saving…' : 'Save Settings' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import api from '../api/index.js'

const emit = defineEmits(['close', 'saved'])

const showKey = ref(false)
const saving = ref(false)
const testing = ref(false)
const testResult = ref(null)

const maskedKey = ref('')
const keySet = ref(false)

const form = reactive({
  apiKey: '',
  baseUrl: '',
  modelName: 'gpt-4o',
  customModel: '',
})

onMounted(async () => {
  try {
    const res = await api.get('/settings')
    const d = res.data || res
    maskedKey.value = d.llm_api_key_masked || ''
    keySet.value = d.llm_api_key_set || false
    form.baseUrl = d.llm_base_url || 'https://api.openai.com/v1'
    const knownModels = ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo', 'o1', 'o1-mini']
    if (knownModels.includes(d.llm_model_name)) {
      form.modelName = d.llm_model_name
    } else if (d.llm_model_name) {
      form.modelName = 'custom'
      form.customModel = d.llm_model_name
    }
  } catch {}
})

async function save() {
  saving.value = true
  testResult.value = null
  try {
    const effectiveModel = form.modelName === 'custom' ? form.customModel : form.modelName
    const payload = {
      llm_base_url: form.baseUrl || null,
      llm_model_name: effectiveModel || null,
    }
    if (form.apiKey.trim()) payload.llm_api_key = form.apiKey.trim()

    const res = await api.put('/settings', payload)
    const d = res.data || res
    maskedKey.value = d.llm_api_key_masked || ''
    keySet.value = d.llm_api_key_set || false
    form.apiKey = ''  // clear plaintext from field after save
    emit('saved', { keySet: keySet.value })
  } catch (e) {
    testResult.value = { success: false, error: e.message || 'Save failed' }
  } finally {
    saving.value = false
  }
}

async function testConnection() {
  testing.value = true
  testResult.value = null
  try {
    // Save first if a new key was entered
    if (form.apiKey.trim()) await save()
    const res = await api.post('/settings/test')
    testResult.value = res.success !== undefined ? res : { success: true }
  } catch (e) {
    testResult.value = { success: false, error: e.message || 'Test failed' }
  } finally {
    testing.value = false
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed; inset: 0; z-index: 1000;
  background: rgba(0,0,0,0.7);
  display: flex; align-items: center; justify-content: center;
  backdrop-filter: blur(4px);
}

.modal-box {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  width: 520px;
  max-width: calc(100vw - 32px);
  box-shadow: 0 24px 64px rgba(0,0,0,0.5);
  display: flex; flex-direction: column;
}

.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 24px 16px;
  border-bottom: 1px solid var(--border);
}
.modal-title { display: flex; align-items: center; gap: 10px; font-size: 18px; font-weight: 700; }
.modal-icon { font-size: 20px; }
.close-btn {
  background: none; border: none; color: var(--text-secondary);
  font-size: 18px; cursor: pointer; padding: 4px 8px; border-radius: 6px;
  transition: color 0.2s;
}
.close-btn:hover { color: var(--text-primary); }

.modal-body { padding: 24px; display: flex; flex-direction: column; gap: 20px; }

.status-banner {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 16px; border-radius: 8px;
  font-size: 13px; font-weight: 500;
}
.banner-ok { background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.25); color: var(--accent-green); }
.banner-warn { background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.25); color: var(--accent-amber); }

.status-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot-green { background: var(--accent-green); box-shadow: 0 0 6px var(--accent-green); }
.dot-amber { background: var(--accent-amber); box-shadow: 0 0 6px var(--accent-amber); }

.field-group { display: flex; flex-direction: column; gap: 6px; }
.field-group label { font-size: 13px; font-weight: 600; color: var(--text-secondary); }
.optional { font-weight: 400; opacity: 0.7; }
.field-hint { font-size: 12px; color: var(--text-secondary); opacity: 0.7; line-height: 1.5; }
.field-hint code { background: var(--bg-secondary); padding: 1px 5px; border-radius: 3px; font-size: 11px; }

.input-row { display: flex; gap: 8px; }
.key-input { flex: 1; font-family: monospace; letter-spacing: 0.05em; }
.toggle-btn {
  background: var(--bg-secondary); border: 1px solid var(--border);
  border-radius: 8px; padding: 0 12px; cursor: pointer;
  font-size: 16px; transition: border-color 0.2s; flex-shrink: 0;
}
.toggle-btn:hover { border-color: var(--accent-blue); }

.model-row { display: flex; gap: 8px; }
.model-row select { flex: 1; }
.custom-model-input { flex: 1; }

.test-result {
  padding: 10px 14px; border-radius: 8px; font-size: 13px; font-weight: 500;
}
.test-ok { background: rgba(16,185,129,0.1); color: var(--accent-green); border: 1px solid rgba(16,185,129,0.2); }
.test-fail { background: rgba(239,68,68,0.1); color: var(--accent-red); border: 1px solid rgba(239,68,68,0.2); }

.modal-footer {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 24px; border-top: 1px solid var(--border); gap: 12px;
}
.footer-right { display: flex; gap: 8px; }
</style>
