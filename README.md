# Miro Strategy App

A universal strategic advisor that transforms raw research into actionable strategies for **any scenario** — business competition, market entry, negotiations, political campaigns, product launches, and more.

## What It Does

Input your scenario context. The app runs it through a multi-framework analysis engine and produces:

- **Competitive Analysis** — Key player profiling with Porter's Five Forces, positioning matrix, threat scoring
- **MBTI-Typed Personas** — Psychological profiles for customers, opponents, and allies with decision-style and intent modeling
- **Multi-Path Strategy** — Win, pivot, and graceful exit strategies with Bayesian win probabilities
- **Tactical Playbook** — Tactics sourced from war strategy (Sun Tzu, OODA), marketing (AIDA, Google Ads), and Robert Greene's frameworks
- **Robert Greene Power Analysis** — 48 Laws of Power in play, 33 Strategies mapped, seduction type profiling, Laws of Human Nature diagnosis
- **Campaign Planning** — Google Ads-compatible AIDA campaigns with timelines, KPIs, and budgets
- **Victory Roadmap** — Step-by-step milestones with Monte Carlo probability scoring
- **Metrics Dashboard** — Live KPI tracking, win probability trends, framework coverage
- **MiroFish Simulation** — Optional multi-agent simulation enrichment via [MiroFish](https://github.com/666ghj/MiroFish)

## Framework Stack

| Framework | Source |
|---|---|
| War Strategy | Sun Tzu Art of War, Clausewitz, OODA loop |
| Marketing | AIDA funnel, Google Ads, content marketing |
| Target Research | Porter's Five Forces, TAM/SAM/SOM, Jobs-To-Be-Done |
| Psychology | MBTI (all 16 types), behavioral intent modeling |
| Power & Strategy | Robert Greene — 48 Laws, 33 Strategies, Art of Seduction, Laws of Human Nature, Mastery, 50th Law |
| Statistics | Bayesian probability, Monte Carlo simulation |
| AI Simulation | MiroFish multi-agent prediction engine |

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) (`pip install uv`)
- LLM API key (OpenAI-compatible)

### Setup

```bash
# Clone and enter the repo
git clone <repo-url>
cd miro-strategy-app

# Copy env config
cp .env.example .env
# Edit .env with your LLM_API_KEY and other settings

# Install all dependencies (backend + frontend + MiroFish submodule)
npm run setup:all

# Run database migrations
npm run db:migrate

# (Optional) Seed with a demo scenario
npm run db:seed

# Start development servers
npm run dev
```

- Backend API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- Frontend: http://localhost:3001

### Docker

```bash
cp .env.example .env
# Edit .env
docker-compose up --build
```

## Project Structure

```
miro-strategy-app/
├── mirofish/              # MiroFish submodule (AI simulation engine)
├── backend/               # FastAPI + SQLAlchemy backend
│   └── app/
│       ├── api/           # Route handlers
│       ├── models/        # SQLAlchemy ORM models
│       ├── services/      # Business logic + LLM pipelines
│       ├── utils/         # Shared utilities
│       └── prompts/       # LLM prompt templates
└── frontend/              # Vue 3 + Vite frontend
    └── src/
        ├── views/         # Page-level views
        ├── components/    # Reusable UI components
        ├── api/           # API client modules
        └── store/         # Reactive state stores
```

## Environment Variables

See `.env.example` for all configuration options.

## License

MIT
