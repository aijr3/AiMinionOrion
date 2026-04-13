<template>
  <div id="miro-app">
    <AppHeader />
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import AppHeader from './components/AppHeader.vue'
</script>

<style>
:root {
  --bg-primary: #0a0e1a;
  --bg-secondary: #111827;
  --bg-card: #1a2235;
  --border: #2d3748;
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;
  --accent-blue: #3b82f6;
  --accent-purple: #8b5cf6;
  --accent-green: #10b981;
  --accent-amber: #f59e0b;
  --accent-red: #ef4444;
  --accent-gold: #d4af37;
}

body { margin: 0; background: var(--bg-primary); color: var(--text-primary); }

#miro-app { min-height: 100vh; display: flex; flex-direction: column; }

.main-content { flex: 1; padding: 0 24px 40px; max-width: 1400px; margin: 0 auto; width: 100%; }

.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
}

.btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 10px 20px; border-radius: 8px; border: none;
  font-size: 14px; font-weight: 600; cursor: pointer;
  transition: all 0.2s;
}

.btn-primary { background: var(--accent-blue); color: white; }
.btn-primary:hover { background: #2563eb; }
.btn-secondary { background: transparent; border: 1px solid var(--border); color: var(--text-primary); }
.btn-secondary:hover { border-color: var(--accent-blue); color: var(--accent-blue); }
.btn-gold { background: var(--accent-gold); color: #0a0e1a; }

.badge {
  display: inline-block; padding: 2px 10px; border-radius: 20px;
  font-size: 12px; font-weight: 600;
}
.badge-critical { background: rgba(239,68,68,0.2); color: #ef4444; }
.badge-high { background: rgba(245,158,11,0.2); color: #f59e0b; }
.badge-medium { background: rgba(59,130,246,0.2); color: #3b82f6; }
.badge-low { background: rgba(16,185,129,0.2); color: #10b981; }
.badge-win { background: rgba(16,185,129,0.2); color: #10b981; }
.badge-exit { background: rgba(139,92,246,0.2); color: #8b5cf6; }
.badge-pivot { background: rgba(245,158,11,0.2); color: #f59e0b; }

.section-title { font-size: 22px; font-weight: 700; margin: 0 0 20px; }
.page-title { font-size: 32px; font-weight: 800; margin: 32px 0 8px; }
.page-subtitle { color: var(--text-secondary); margin: 0 0 32px; }

.prob-bar { height: 8px; background: var(--border); border-radius: 4px; overflow: hidden; }
.prob-fill { height: 100%; border-radius: 4px; transition: width 0.8s ease; }

input, textarea, select {
  background: var(--bg-secondary); border: 1px solid var(--border);
  color: var(--text-primary); border-radius: 8px; padding: 10px 14px;
  font-size: 14px; width: 100%; outline: none;
}
input:focus, textarea:focus, select:focus { border-color: var(--accent-blue); }
label { display: block; font-size: 13px; font-weight: 600; color: var(--text-secondary); margin-bottom: 6px; }
</style>
