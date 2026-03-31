# AI-Powered Configuration Navigator — GSoC 2026 PoC

> **Google Summer of Code 2026 Proof of Concept**
> 
> This is a Python prototype demonstrating the AI-powered configuration navigation concept proposed for Drupal core.
> 
> **Drupal.org Proposal:** [Issue #3569913](https://www.drupal.org/project/gsoc/issues/3569913)
> 
> **Mentor:** Aditya Bathani (adityabathani.4478@gmail.com)

---

## Overview

Drupal's extensive configuration system can be overwhelming for site builders. This project builds an AI assistant that helps users find the right configuration page using natural language queries.

**AI-powered natural-language assistant for finding Drupal admin configuration pages.** Built with **Reflex** (Python full-stack) + **Groq** (fast LLM inference) + **rapidfuzz** (hybrid retrieval).

---

## What this PoC does

You type a natural-language question like:

- *"How do I change the site logo?"*
- *"Where can I configure email settings?"*
- *"I need to add a new content type"*
- *"How do I put the site in maintenance mode?"*

The app:
1. Scores all **100 Drupal admin configuration pages** against your query using a **hybrid fuzzy + keyword retrieval pipeline**
2. Sends the top-ranked candidates to **Groq** for a short, actionable explanation
3. **Streams the response token-by-token** into the chat UI
4. Shows **clickable candidate cards** with the admin path for each relevant page

---

## Tech stack

| Layer | Technology | Why |
|---|---|---|
| Frontend + Backend | [Reflex](https://reflex.dev) | Pure Python full-stack — no JS needed |
| LLM endpoint | [Groq](https://console.groq.com) | Fast streamed inference, simple Python SDK |
| Fuzzy retrieval | [rapidfuzz](https://github.com/maxbachmann/RapidFuzz) | Handles typos and near-matches without embeddings |
| Config metadata | Local JSON (`assets/config_data.json`) | No Drupal instance required for the PoC |
| Env management | python-dotenv | Keeps API keys out of source code |

---

## Project structure

```
config_nav/                   ← project root
├── rxconfig.py               ← Reflex app configuration
├── requirements.txt          ← Python dependencies
├── .env.example              ← Environment variable template
├── scraper.py                ← Script to expand config pages from Drupal.org
├── README.md                 ← This file
└── config_nav/               ← Python package
    ├── __init__.py
    ├── config_nav.py         ← Page layout + app initialisation
    ├── state.py              ← Reflex state + streaming event handler
    ├── retrieval.py          ← Hybrid fuzzy/keyword retrieval service
    ├── groq_client.py        ← Groq SDK integration + prompt design
    ├── components/
    │   ├── __init__.py
    │   └── chat.py           ← All UI components (bubbles, cards, input)
    └── assets/
        ├── config_data.json       ← 100 Drupal admin page records
        └── config_data_backup.json ← Backup of original 35 entries
```

---

## Quick start

### Prerequisites

- Python **3.11+**
- Node.js **18+** (required by Reflex to compile the React frontend)
- A free **Groq API key** from [console.groq.com/keys](https://console.groq.com/keys)

### 1. Clone / navigate to the project

```bash
cd GSOC/poc/config_nav
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

```bash
cp .env.example .env
```

Open `.env` and replace `your_groq_api_key_here` with your actual key:

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
```

### 5. Initialise Reflex (first run only)

```bash
reflex init
```

When prompted to select a template, choose **0** (blank).

### 6. Run the app

```bash
reflex run
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Environment variables

All variables have sensible defaults — only `GROQ_API_KEY` is required.

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | *(required)* | Your Groq API key |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | Groq model for explanations |
| `GROQ_MAX_TOKENS` | `1500` | Max tokens per response |
| `GROQ_TEMPERATURE` | `0.5` | Lower = more deterministic, higher = more conversational |
| `GROQ_REASONING_EFFORT` | `medium` | Groq reasoning depth |
| `RETRIEVAL_MIN_SCORE` | `15` | Minimum fuzzy score to include a result (0–100) |
| `RETRIEVAL_TOP_K` | `5` | Max candidates passed to Groq |

---

## How retrieval works

The retrieval layer scores every config page record against your query using **four weighted signals**:

| Signal | Weight | Algorithm |
|---|---|---|
| Title match | 35% | `rapidfuzz.fuzz.token_set_ratio` |
| Description match | 25% | `rapidfuzz.fuzz.partial_ratio` |
| Keyword match | 25% | Best `partial_ratio` across keyword list |
| Synonym match | 15% | Best `partial_ratio` across synonym list |

Records scoring below `RETRIEVAL_MIN_SCORE` are discarded.
The top `RETRIEVAL_TOP_K` are passed to Groq as context.

### Debug retrieval scores

```bash
python -c "
from config_nav.retrieval import debug_scores
debug_scores('change logo')
"
```

---

## Sample queries to try

| Query | Expected top result |
|---|---|
| How do I change the site logo? | Appearance / Theme Settings |
| Where can I configure email? | Mail System / Email Settings |
| I need to add a content type | Content Types |
| How do I set permissions for editors? | Permissions |
| Where is the cache settings page? | Performance / Cache Settings |
| How do I put the site offline? | Maintenance Mode |
| Where do I manage navigation menus? | Menus |
| I want to create a taxonomy vocabulary | Taxonomy Vocabularies |
| How do I check the site status? | Status Report |
| Where can I configure URL aliases? | URL Aliases / Path Settings |

---

## Retrieval without Groq (offline mode)

If you want to test retrieval only, without calling the Groq API:

```python
from config_nav.retrieval import retrieve

results = retrieve("how do I change the logo?")
for r in results:
    print(f"{r['_score']:5.1f}  {r['title']:<40}  {r['path']}")
```

---

## Adding more config pages

### Option 1: Run the scraper script

A scraper script is included to expand config pages from Drupal documentation:

```bash
python scraper.py
```

This will:
- Load existing `config_data.json`
- Add predefined Drupal admin pages
- Create `config_data_new.json` with expanded entries
- Automatically handle keywords and synonyms

### Option 2: Manual editing

Edit `config_nav/assets/config_data.json`.
Each record must have:

```json
{
  "title": "Human-readable page title",
  "path": "/admin/path/to/page",
  "module": "module_name",
  "description": "What this page controls in plain English.",
  "keywords": ["keyword1", "keyword2", "..."],
  "synonyms": ["alternative phrase 1", "alternative phrase 2"],
  "permissions": ["required_drupal_permission"]
}
```

The metadata file is loaded once at startup via an `lru_cache`.
Restart `reflex run` after editing it, or call `reload_metadata()` in a shell.

---

## Relationship to the final GSoC implementation

This PoC intentionally uses a **lightweight Python stack** to validate the interaction model quickly. The production implementation for GSoC will be **Drupal-native**:

| PoC layer | Final Drupal implementation |
|---|---|
| `config_data.json` | Drupal route / menu / permission metadata indexer |
| `retrieval.py` (rapidfuzz) | Drupal AI Search + vector DB (SQLite VDB / pgvector) |
| `groq_client.py` | Drupal AI module provider abstraction |
| Reflex chat UI | Drupal AI Chatbot / DeepChat block |
| Python state | Drupal AI Assistant API |
| Local JSON records | Drupal plugin API for contrib metadata registration |

The PoC answers the following questions before committing to the full Drupal build:
- Does hybrid fuzzy + keyword retrieval give good results for config page queries?
- Is the Groq explanation format (bold title + path + one-line reason) clear enough?
- Do users understand the candidate cards?
- Is streaming important for perceived responsiveness at this response length?
- Which query phrasings are hardest to handle?

---

## Deploy to Reflex Cloud (optional)

To share a live demo link with your GSoC mentor:

```bash
reflex deploy
```

Follow the prompts to authenticate and deploy.
You will get a public URL you can include in your proposal.

---

## License

MIT — this is an open-source proof of concept for GSoC 2026.