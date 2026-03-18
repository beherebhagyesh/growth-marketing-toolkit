# Growth Marketing Toolkit 🦾

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.104+-009974?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge">
  <img src="https://img.shields.io/badge/Claude-Code🦾-purple?style=for-the-badge">
</p>

<p align="center">
  <strong>Turn Claude Code into your personal data analyst</strong><br>
  Analytics • SEO • Indexing • Pagespeed — All in one toolkit
</p>

---

## ✨ What Can You Do?

### 📊 Analytics — Your Data Analyst on Autopilot

```python
# Track events to PostHog, Google Analytics & Mixpanel
track_event("button_clicked", {"page": "/home", "user": "premium"})

# Check if your events are firing correctly
check_events(["signup", "purchase", "cancel"])

# Get natural language reports
report("show me conversion trends this week")
```

### 🔍 SEO — Programmatic Keyword Research

```python
# Build a keyword universe from seed keywords
universe = create_keyword_universe(["ai marketing", "growth hacking"])

# Optimize existing pages
optimize_existing_page(
    "https://example.com/ai-tools",
    ["best ai tools", "ai software 2024"]
)

# Generate new page content
content = create_new_page(
    "best project management software",
    ["https://competitor.com/tools", "https://another.com"]
)
```

### 🗺️ Indexing — Fix Your Google Index Issues

```python
# Analyze sitemap + GSC data
report = analyze_indexing(
    sitemap="sitemap.xml",
    gsc="gsc_export.csv"
)

# Get fix recommendations
fixes = fix_indexing(sitemap, gsc)
```

### ⚡ Pagespeed — Hit 90+ Scores

```python
# Run Lighthouse analysis
scores = run_pagespeed("https://example.com")

# Get optimization plan to reach 90+
plan = optimize_to_90("https://example.com")
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/beherebhagyesh/growth-marketing-toolkit.git
cd growth-marketing-toolkit
pip install -r requirements.txt
npm install -g lighthouse  # For pagespeed
```

### 2. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

| Service | Environment Variable | Get Key From |
|---------|---------------------|--------------|
| PostHog | `POSTHOG_API_KEY` | [post hog.app](https://app.posthog.com) |
| Google Analytics | `GOOGLE_ANALYTICS_MEASUREMENT_ID` | GA4 Console |
| Mixpanel | `MIXPANEL_API_KEY` | [mixpanel.com](https://mixpanel.com) |
| DataForSEO | `DATAFORSEO_LOGIN` | [dataforseo.com](https://dataforseo.com) ($10 min) |

### 3. Run the Web UI

```bash
python server.py
# Open http://localhost:8080
```

### 4. Or Use the CLI

```bash
# Analytics
python -m cli.main analytics track "signup" '{"plan": "pro"}'
python -m cli.main analytics check signup purchase

# SEO
python -m cli.main seo universe ai marketing growth
python -m cli.main seo optimize https://example.com ai tools

# Indexing
python -m cli.main indexing --sitemap sitemap.xml --gsc gsc.csv

# Pagespeed
python -m cli.main pagespeed https://example.com --optimize
```

---

## 🎯 Features

### Analytics Module
- ✅ Multi-provider tracking (PostHog, GA4, Mixpanel)
- ✅ Event validation & debugging
- ✅ Natural language metric queries
- ✅ Dashboard creation

### SEO Module
- ✅ Keyword universe generation
- ✅ Competitor analysis
- ✅ Page optimization recommendations
- ✅ Content generation templates
- ✅ SERP data extraction

### Indexing Module
- ✅ Sitemap parsing (XML)
- ✅ GSC export analysis
- ✅ Index status comparison
- ✅ Issue detection & recommendations
- ✅ Fix suggestions with code snippets

### Pagespeed Module
- ✅ Lighthouse integration
- ✅ Performance, Accessibility, SEO, Best Practices scores
- ✅ Optimization opportunities
- ✅ Code fix recommendations
- ✅ Batch URL auditing

---

## 📸 Web UI Preview

```
┌─────────────────────────────────────────────────────────────┐
│  🦾 Growth Marketing Toolkit                                │
│     Claude Code as your data analyst                        │
├─────────────────────────────────────────────────────────────┤
│  [📊 Analytics] [🔍 SEO] [🗺️ Indexing] [⚡ Pagespeed]    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Track Event                                        │   │
│  │  Event Name: [button_clicked________________]        │   │
│  │  Properties: [{"page": "/home"}________________]    │   │
│  │  [Track Event]                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Results                                            │   │
│  │  { "posthog": { "status": 200 },                   │   │
│  │    "ga": { "status": 200 } }                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architecture

```
growth-marketing-toolkit/
├── analytics/          # PostHog/GA/Mixpanel integration
├── seo/                # DataForSEO integration
├── indexing/           # Sitemap/GSC analysis
├── pagespeed/          # Lighthouse automation
├── cli/                # Command-line interface
├── frontend/           # Web UI
│   ├── templates/      # HTML templates
│   └── static/        # CSS & JS
├── server.py           # FastAPI server
└── .env.example        # Environment config
```

---

## 🔧 Requirements

- Python 3.8+
- Node.js (for Lighthouse CLI)
- API keys (see `.env.example`)

### Optional Services

| Service | Use Case | Cost |
|---------|----------|------|
| PostHog | Event tracking & analytics | Free tier available |
| DataForSEO | Keyword research | ~$10/month |
| Lighthouse | Pagespeed testing | Free |

---

## 🤖 Use with Claude Code

This toolkit is designed to work seamlessly with Claude Code. Once configured:

1. **Ask naturally**: "Hey Claude, what's our conversion rate this week?"
2. **Get insights**: "Create a keyword universe for AI marketing tools"
3. **Fix issues**: "Run pagespeed on our landing page and fix anything below 90"

Claude Code can read your analytics, analyze your SEO, fix indexing issues, and optimize performance — all through natural conversation.

---

## 📝 License

MIT License — feel free to use, modify, and distribute.

---

## 🔗 Links

- **Repository**: https://github.com/beherebhagyesh/growth-marketing-toolkit
- **Issues**: https://github.com/beherebhagyesh/growth-marketing-toolkit/issues

---

<p align="center">
  Made with ❤️ using Claude Code
</p>
