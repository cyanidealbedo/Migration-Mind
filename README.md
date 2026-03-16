<div align="center">
  <img src="https://i.ibb.co/1fXV0vRc/image.png" alt="MigrationMind Banner" width="100%">
</div>

<div align="center">


### *Azure Migrate tells you what you have.*
### *MigrationMind tells you what to do with it.*
**In what order. At what cost. And exactly what will break along the way.**

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-mm--django--app.azurewebsites.net-0078D4?style=for-the-badge)](https://mm-django-app.azurewebsites.net)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Azure Functions](https://img.shields.io/badge/Azure_Functions-V2_Python-0062AD?style=for-the-badge&logo=microsoft-azure&logoColor=white)](https://azure.microsoft.com/products/functions)
[![GPT-4o](https://img.shields.io/badge/GPT--4o-Azure_OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)](https://azure.microsoft.com/products/ai-services/openai-service)
[![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

> *Built for the **Microsoft AI Dev Days Hackathon** — Challenge: Build AI Applications & Agents using Microsoft AI Platform and tools*

</div>

---

## 📋 Table of Contents

1. [The Problem](#-the-problem)
2. [Our Solution](#-our-solution)
3. [Key Features](#-key-features)
4. [System Architecture](#️-system-architecture)
5. [The Four Agents](#-the-four-agents)
6. [The Living Playbook](#-the-living-playbook)
7. [Technology Stack](#️-technology-stack)
8. [Azure Services Used](#-azure-services-used-10)
9. [Quick Start](#-quick-start)
10. [Data Models](#-data-models)
11. [Responsible AI](#-responsible-ai)
12. [Team](#-team)

---

## 🧠 The Problem

Every enterprise cloud migration starts the same way: a consultant charges $200,000, hands you a 400-page Word document, and leaves. Three months later, you start migrating — and discover the dependencies nobody mapped, the compliance risks nobody flagged, and the cost projections that assumed pricing from six months ago.

**Azure Migrate tells you your inventory. Nobody tells you what to do with it.**

There is no tool that takes a raw Azure Migrate export and answers the questions that actually matter:

- Which servers must move first, or everything breaks?
- What is the live cost delta, priced against **today's** Azure SKUs?
- What compliance and security risks will block this if we don't act?
- When Wave 1 completes, what does the updated plan look like?

**MigrationMind answers all of it — automatically, in minutes, powered by a 4-agent AI pipeline.**

---

## 💡 Our Solution

Upload an Azure Migrate assessment export (JSON or CSV). MigrationMind's agent pipeline takes it from there.

It achieves three goals:

- **Sequencing:** Topological dependency analysis that tells you the exact order to migrate, not just what you have.
- **Live Pricing:** Real cost projections from the Azure Retail Prices API — not stale estimates from a consultant's spreadsheet.
- **Governance:** Structured compliance risk evaluation with blocking flags and a human sign-off workflow, built for enterprise audit trails.

---

## ✨ Key Features

### 1. 🗺️ Surveyor — Dependency Mapper
Reads your Azure Migrate assessment via **Azure MCP** and builds a complete directed dependency graph covering every asset and every edge. In demo mode, uses a hardcoded 47-asset synthetic estate so you can explore the full experience without an Azure Migrate subscription.

### 2. 🏗️ Architect — Wave Sequencer
Takes the dependency graph and performs a **topological sort** to sequence assets into ordered migration waves. **GPT-4o** reasons about which assets must move first based on dependency depth, criticality, and blast radius — with all output validated through Pydantic and `json_schema` structured outputs. No hallucinations in structured data.

### 3. 💰 Accountant — Live Pricing Engine
Hits `https://prices.azure.com/api/retail/prices` — a public Microsoft API — and prices every VM SKU in every wave against **current Azure pricing**. Outputs per-wave savings, 3-Year NPV, and ROI breakeven month. Every figure is verifiable.

### 4. 🛡️ Risk Officer — Compliance Evaluator
**GPT-4o** evaluates each wave for compliance, security, and operational risks. Returns structured risk cards with remediation plans. **Blocking risks require human sign-off before a wave can proceed**, enforcing a governance gate baked into the pipeline.

### 5. 📋 Living Playbook — V2 Re-runs
The playbook is not static. Click **"Mark Wave 1 Complete"** and the entire 4-agent pipeline re-runs on your updated estate. Completed assets are removed from the graph, savings projections update, and a new versioned playbook is saved with a diff summary: *"3 assets removed · savings increased by $4,200/mo"*. Every version is preserved in a history timeline.

### 6. 🔍 Governance Dashboard
A dedicated approval queue for blocking risk cards. Enterprise compliance officers can approve or reject waves, with every decision logged in a full audit trail of `AgentRun` records — tokens, duration, model, and complete reasoning output per step.

---

## 🏛️ System Architecture


<div align="center">
  <img src="https://i.ibb.co/ycgynrWP/finalmon-migration-mind.jpg" alt="MigrationMind Architecture Diagram" width="800"/>
</div>


---

## 📸 Project Screenshots

### Main Dashboard

<div align="center">
  <img src="https://hackboxpmeproduction.blob.core.windows.net/proj-8bd6f1b0-67de-4193-8d40-3970593d58f8-1773629421558/733b7c8f-150d-41b4-a407-82bf680c2291_1773640312755?sv=2026-02-06&st=2026-03-16T05%3A57%3A59Z&se=2026-03-16T06%3A07%3A59Z&skoid=4fec1579-ad60-4829-98b1-c37115c9dd25&sktid=975f013f-7f24-47e8-a7d3-abc4752bf346&skt=2026-03-16T05%3A57%3A59Z&ske=2026-03-16T06%3A07%3A59Z&sks=b&skv=2026-02-06&sr=b&sp=r&sig=PWjT3zQm2Iog38KjAYIYijT%2BVzDJ951JHjwQifnnDZA%3D" alt="MigrationMind Main Dashboard" width="800"/>
</div>

### Feature Showcase

<table>
  <tr>
    <td width="50%">
      <img src="https://hackboxpmeproduction.blob.core.windows.net/proj-8bd6f1b0-67de-4193-8d40-3970593d58f8-1773629421558/eb50ec3c-9967-4f48-933c-1c665ce80e01_1773640172458?sv=2026-02-06&st=2026-03-16T05%3A57%3A59Z&se=2026-03-16T06%3A07%3A59Z&skoid=4fec1579-ad60-4829-98b1-c37115c9dd25&sktid=975f013f-7f24-47e8-a7d3-abc4752bf346&skt=2026-03-16T05%3A57%3A59Z&ske=2026-03-16T06%3A07%3A59Z&sks=b&skv=2026-02-06&sr=b&sp=r&sig=%2BYZzEX0ZdwT4b8TopAqcXpmn3lj%2BgGRryIHQXKdhGUo%3D" alt="Dependency Map" width="100%"/>
      <p align="center"><strong>Dependency Map (2D + 3D)</strong></p>
    </td>
    <td width="50%">
      <img src="https://hackboxpmeproduction.blob.core.windows.net/proj-8bd6f1b0-67de-4193-8d40-3970593d58f8-1773629421558/4f6221af-366e-4c8c-b782-73457ba30e26_1773640348831?sv=2026-02-06&st=2026-03-16T05%3A57%3A59Z&se=2026-03-16T06%3A07%3A59Z&skoid=4fec1579-ad60-4829-98b1-c37115c9dd25&sktid=975f013f-7f24-47e8-a7d3-abc4752bf346&skt=2026-03-16T05%3A57%3A59Z&ske=2026-03-16T06%3A07%3A59Z&sks=b&skv=2026-02-06&sr=b&sp=r&sig=kq5CFKG2K0bef2smc09lXUEvIDpvSTLlWTQk3XSXZFU%3D" alt="Migration Waves" width="100%"/>
      <p align="center"><strong>Migration Waves</strong></p>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <img src="https://hackboxpmeproduction.blob.core.windows.net/proj-8bd6f1b0-67de-4193-8d40-3970593d58f8-1773629421558/b2adda5d-b163-4fce-9754-ec29b983fb9f_1773641913104?sv=2026-02-06&st=2026-03-16T06%3A20%3A42Z&se=2026-03-16T06%3A30%3A42Z&skoid=4fec1579-ad60-4829-98b1-c37115c9dd25&sktid=975f013f-7f24-47e8-a7d3-abc4752bf346&skt=2026-03-16T06%3A20%3A42Z&ske=2026-03-16T06%3A30%3A42Z&sks=b&skv=2026-02-06&sr=b&sp=r&sig=UMTOAo%2FQUFQHCT3gAGPZ1CKBg2K9vLJL4A8zMUwZD7w%3D" alt="Business Case" width="100%"/>
      <p align="center"><strong>Business Case & Live Pricing</strong></p>
    </td>
    <td width="50%">
      <img src="https://hackboxpmeproduction.blob.core.windows.net/proj-8bd6f1b0-67de-4193-8d40-3970593d58f8-1773629421558/6eeddb24-d41b-4a0e-9c05-236cd531a761_1773641694369?sv=2026-02-06&st=2026-03-16T06%3A20%3A42Z&se=2026-03-16T06%3A30%3A42Z&skoid=4fec1579-ad60-4829-98b1-c37115c9dd25&sktid=975f013f-7f24-47e8-a7d3-abc4752bf346&skt=2026-03-16T06%3A20%3A42Z&ske=2026-03-16T06%3A30%3A42Z&sks=b&skv=2026-02-06&sr=b&sp=r&sig=0rLwLzG%2BqyYoIh7lWzb0ShhfaRLt7sw%2BdpCfQE7Qmbs%3D" alt="Agent Thought Streame" width="100%"/>
      <p align="center"><strong>Agent Thought Stream</strong></p>
    </td>
  </tr>
</table>

---

## 🤖 The Four Agents

### 🗺️ Surveyor — Dependency Mapper
Reads the Azure Migrate assessment via **Azure MCP** and builds a complete directed dependency graph. Every asset. Every edge. In demo mode, uses a hardcoded 47-asset synthetic estate.

**Output:** `{"Web-IIS-01": ["Prod-SQL-01", "Auth-Redis-01"], ...}`

---

### 🏗️ Architect — Wave Sequencer

Takes the dependency graph and performs a **topological sort** to sequence assets into migration waves. GPT-4o reasons about which assets must move first based on dependency depth, criticality, and blast radius.

| Agent Input | Agent Output |
|---|---|
| Dependency graph (47 assets) | 4 ordered migration waves |
| Completed waves list | Critical path (ordered asset IDs) |
| Asset metadata | Total estimated days: 90 |

**All output is Pydantic-validated.** `response_format: json_schema` on every GPT-4o call — no hallucinations in structured data.

---

### 💰 Accountant — Live Pricing Engine

Hits `https://prices.azure.com/api/retail/prices` — a **public Microsoft API, no auth required** — and prices every VM SKU in every wave against current Azure pricing.

| Output | Value |
|---|---|
| Per-wave monthly savings | Real figures, not estimates |
| 3-Year NPV | Computed from live price delta |
| ROI breakeven month | Dynamic per your estate |
| Pricing source | `azure_retail_prices_api` — verifiable |

---

### 🛡️ Risk Officer — Compliance Evaluator

GPT-4o evaluates each wave for compliance, security, and operational risks. Returns structured risk cards with remediation plans. **Blocking risks require human sign-off before a wave can proceed.**

| Risk Type | Blocking? |
|---|---|
| `compliance_gdpr` | ✅ Yes — production SQL with PII |
| `network_dependency` | ⚠️ Sometimes |
| `data_sovereignty` | ✅ Yes — cross-region replication |

---

## 📋 The Living Playbook

The playbook is the output — a **5-tab interactive document** that updates itself every time you complete a migration wave.

| Tab | Contents |
|---|---|
| **Dependency Map** | vis.js force-directed graph + Three.js 3D view. Nodes coloured by type: blue=app, coral=DB, amber=shared service |
| **Migration Waves** | GPT-4o wave cards with assets, reasoning, duration. Wave 1 has a "Mark Complete" button that re-runs the entire pipeline |
| **Business Case** | Live NPV, breakeven month, per-wave cost table priced from Azure Retail Prices API |
| **Risk & Compliance** | Animated compliance score bar. Risk cards with per-card Acknowledge workflow |
| **Agent Log** | Dark terminal thought stream — every AgentRun record with tokens, duration, model, and full reasoning output |

### V2 Living Playbook

When you click **"Mark Wave 1 Completed":**

1. Django PATCHes the wave status and re-enqueues a Service Bus message
2. The Azure Function detects `version_count > 0`, removes completed assets from the graph
3. All 4 agents re-run on the updated estate
4. A new `PlaybookVersion` is saved with a diff summary: *"3 assets removed · savings increased by $4,200/mo"*
5. The UI shows a **v2 banner** on reload

Every version is preserved in the history timeline.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Web Framework** | Django 5.2 + Django REST Framework |
| **Agent Runtime** | Python 3.10 · Azure Functions V2 |
| **AI Model** | Azure OpenAI GPT-4o (structured outputs via `json_schema`) |
| **Data Validation** | Pydantic — all agent I/O contracts |
| **Database** | Azure MySQL Flexible Server · Django ORM + raw pymysql |
| **Async Messaging** | Azure Service Bus |
| **Observability** | OpenTelemetry · azure-monitor-opentelemetry · Application Insights |
| **Static Files** | WhiteNoise (production, no nginx) |
| **WSGI** | gunicorn (4 workers, 600s timeout) |
| **Dependency Graph** | vis-network (2D) · Three.js r128 (3D) |
| **Frontend** | Bootstrap 5 · Phosphor Icons v2.1.1 · Epilogue + Plus Jakarta Sans + Space Mono |
| **CI/CD** | GitHub Actions → Azure App Service + Azure Functions |
| **Pricing Data** | Azure Retail Prices API (public, `prices.azure.com`) |
| **Secrets** | Azure Key Vault (production) · python-dotenv (dev) |

---

## ☁️ Azure Services Used (10)

| # | Service | What It Does |
|---|---|---|
| 1 | **Azure App Service** | Hosts the Django 5.2 web app (B1 Linux, Python 3.10) |
| 2 | **Azure Functions V2** | Serverless Python host for all 4 agents |
| 3 | **Azure Service Bus** | Async job queue decoupling Django from agent pipeline |
| 4 | **Azure OpenAI (GPT-4o)** | Powers Architect and Risk Officer agents — structured JSON output |
| 5 | **Azure Database for MySQL Flexible Server** | All persistent data — assessments, playbooks, agent runs |
| 6 | **Azure AI Content Safety** | Moderates every user upload before processing begins |
| 7 | **Azure Key Vault** | Secret injection at Django boot time (production only) |
| 8 | **Azure Application Insights** | Full OTel tracing — HTTP, DB, Service Bus, per-agent spans |
| 9 | **Azure AI Foundry** | GPT-4o model deployment and lifecycle management |
| 10 | **Azure MCP (Model Context Protocol)** | Surveyor agent fetches real Azure Migrate assessment data |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- An Azure subscription
- Azure Functions Core Tools v4

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/your-org/MigrationMind.git
    cd MigrationMind
    ```

2. **Set up the Django app:**
    ```bash
    cd django_app
    python -m venv antenv
    source antenv/bin/activate
    pip install -r requirements.txt
    ```

3. **Configure environment:**
    ```bash
    cp .env.example .env
    # Edit .env with your values (SQLite works for local dev)
    ```

4. **Run migrations and start:**
    ```bash
    python manage.py migrate
    python manage.py runserver
    ```

5. **Start the agent runtime (separate terminal):**
    ```bash
    cd agent_runtime
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    cp local.settings.json.example local.settings.json
    # Edit with your Azure OpenAI + Service Bus credentials
    func start
    ```

6. **Access:** Navigate to `http://localhost:8000`

### Environment Variables

**Django App (`.env`):**
```env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3

SERVICE_BUS_CONNECTION_STRING=Endpoint=sb://...
SERVICE_BUS_QUEUE_NAME=assessment-jobs

CONTENT_SAFETY_ENDPOINT=https://....cognitiveservices.azure.com/
CONTENT_SAFETY_KEY=...

APPLICATIONINSIGHTS_CONNECTION_STRING=InstrumentationKey=...

# Production only
KEY_VAULT_URL=https://....vault.azure.net/
```

**Agent Runtime (`local.settings.json`):**
```env
AZURE_OPENAI_ENDPOINT=https://...openai.azure.com/
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
DATABASE_URL=mysql://USER:PASS@HOST:3306/migrationmind
SERVICE_BUS_CONNECTION_STRING=...
APPLICATIONINSIGHTS_CONNECTION_STRING=...
```

---

## 📁 Project Structure

```
MigrationMind/
├── django_app/
│   ├── manage.py
│   ├── requirements.txt
│   ├── migrationmind/
│   │   ├── settings.py          # Key Vault boot injection + App Insights OTel
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── apps/core/
│       ├── models.py            # 8 Django models
│       ├── urls.py              # 5 pages + 11 API endpoints
│       ├── views/
│       │   ├── api.py           # 6 DRF API view classes
│       │   └── pages.py         # 5 Django template view functions
│       ├── services/
│       │   ├── enqueue.py       # Azure Service Bus publisher
│       │   └── contentsafety.py # Azure Content Safety wrapper
│       └── templates/core/
│           ├── home_upload.html
│           ├── assessments_list.html
│           ├── playbook_detail.html  # 5-tab living playbook
│           ├── playbook_history.html
│           └── governance.html
│
├── agent_runtime/
│   ├── function_app.py          # Azure Functions entrypoint + pipeline orchestrator
│   ├── requirements.txt
│   └── src/migrationmind_agents/
│       ├── contracts.py         # Pydantic I/O contracts for all agents
│       ├── agents/
│       │   ├── architect.py     # GPT-4o wave sequencer
│       │   ├── accountant.py    # Azure Retail Prices API
│       │   └── risk_officer.py  # GPT-4o compliance evaluator
│       └── persistence/
│           └── mysql_repo.py    # Raw pymysql (no Django ORM in Functions)
│
└── .github/workflows/
    ├── deploy-django.yml        # CI/CD → Azure App Service
    └── deploy-functions.yml     # CI/CD → Azure Functions
```

---

## 📊 Data Models

| Model | Purpose |
|---|---|
| `Assessment` | Upload metadata + pipeline state machine (`uploaded → processing → playbook_ready / failed`) |
| `Asset` | Normalized VMs, databases, applications from Azure Migrate |
| `Dependency` | Directed dependency edges between assets |
| `MigrationWave` | Ordered wave groups with M2M asset relationships |
| `CostModel` | Per-wave financial data from Azure Retail Prices API |
| `RiskCard` | Compliance flags with blocking status and sign-off tracking |
| `PlaybookVersion` | Full JSON playbook snapshots with diff summaries |
| `AgentRun` | Complete audit trail — tokens, duration, model, logs per agent step |

---

## 🔐 Responsible AI

MigrationMind is built with enterprise trust as a first-class concern:

- **Content Moderation:** Every user upload is passed through **Azure AI Content Safety** (hate, violence, sexual, self-harm — severity threshold 4) before any processing begins. Blocked submissions return HTTP 400 with the reason flagged.
- **Grounding:** Architect and Risk Officer agents use `response_format: json_schema` with Pydantic-validated outputs — eliminating hallucinations in structured migration data. Pricing figures are sourced directly from the Azure Retail Prices API, not model-generated estimates.
- **Governance Gate:** Blocking compliance risks (`compliance_gdpr`, `data_sovereignty`) require a named human sign-off before a wave can proceed. The approval workflow is built into the platform, not bolted on.
- **Audit Trail:** Every agent step produces an `AgentRun` record with token counts, duration, model version, and full reasoning output — giving compliance teams complete visibility into every AI-generated decision.
- **Secrets Management:** All production secrets are stored in **Azure Key Vault** and injected at Django boot time. They never exist in environment variables or source control in production.

---

## 🏆 Hackathon Alignment

| Judging Criterion | Our Implementation |
|---|---|
| **Technological Implementation** | Service Bus async decoupling · OTel spans on every agent step · `json_schema` structured GPT-4o outputs · Live Azure Retail Prices API · Content Safety on every upload · Key Vault secret injection |
| **Agentic Design & Innovation** | 4 specialized sequential agents · Pydantic contracts for deterministic parsing · Anti-hallucination via rule-based compliance detection · Living playbook V2 re-run on wave completion |
| **Real-World Impact** | Replaces a $200K+ consulting engagement · Verifiable live pricing, not estimates · Full governance audit trail for enterprise compliance |
| **UX & Presentation** | 5-tab living playbook · V2 diff banner · Animated compliance score bar · Agent thought stream · Version history timeline · 3D dependency graph |
| **Microsoft Platform Adherence** | Azure AI Foundry · Agent Framework pattern · Azure MCP · App Insights (OTel) · Key Vault · Content Safety · Service Bus · Azure OpenAI GPT-4o |

---

## 🚢 Deployment

Fully automated CI/CD via GitHub Actions. Push to `main` and it deploys.

```bash
# Django app — triggers on changes to django_app/**
git push origin main

# Agent runtime — triggers on changes to agent_runtime/**
git push origin main

# Manual trigger
gh workflow run deploy-django.yml
gh workflow run deploy-functions.yml
```

Post-deploy migrations run automatically via the Kudu API after each deployment.

---

## 👥 Team

| Member | GitHub |
|---|---|
| **Gary Bryan** | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat-square&logo=github&logoColor=white)](https://github.com/SlugVortex) |
| **Adrian Tennant** | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat-square&logo=github&logoColor=white)](https://github.com/10ANT) |
| **Malik Christopher** | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat-square&logo=github&logoColor=white)](https://github.com/Mal-chris) |
| **Humani Fagan** | [![GitHub](https://img.shields.io/badge/GitHub-100000?style=flat-square&logo=github&logoColor=white)](https://github.com/cyanidealbedo) |

---

<div align="center">

**Built with ❤️ for the Microsoft AI Dev Days Hackathon**

*Powered by Azure OpenAI · Azure Functions · Django · Azure Service Bus*

[![Azure](https://img.shields.io/badge/Microsoft_Azure-0078D4?style=flat-square&logo=microsoft-azure&logoColor=white)](https://azure.microsoft.com)
[![Django](https://img.shields.io/badge/Django-092E20?style=flat-square&logo=django&logoColor=white)](https://djangoproject.com)
[![OpenAI](https://img.shields.io/badge/Azure_OpenAI-412991?style=flat-square&logo=openai&logoColor=white)](https://azure.microsoft.com/products/ai-services/openai-service)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white)](https://github.com/features/actions)

</div>
