# IT-News Relevance & Ranking Service
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](LICENSE)

A serverless pipeline that **crawls tech-news feeds, filters for enterprise-IT relevance, ranks incidents by urgency**, and exposes them through HTTP & scheduled Azure Functions.

---

## 📁 Project layout
```
.
├── api/                    # Azure Function endpoints (HTTP + timer)
│   ├── crawl.py            # Timer trigger → run crawler every 6 hours
│   ├── ingest.py           # Filters, scores and saves relevant articles to the DB
│   └── retrieve.py         # returns filtered & ranked articles
├── services/               # core logic
│   ├── crawler.py          # fetch RSS/Reddit sources
│   ├── embeddings.py       # MiniLM encoder wrapper
│   ├── filter.py           # Binary relevant article classifier + scoring functions
├── prompts/                # zero-shot prompt templates for generating training data
├── models/                 # .joblib weights for each binary classifier / filter
├── sql/                    # SQL to execute on supabase to create the database
├── db/                     # Database functions and models
│   ├── crud.py             # Helper functions to fetch sources and upsert article batches
│   ├── models.py           # Dataclass schemas (Source, Article) used throughout the app.
├── tests/                  # pytest unit tests for retrieve and ingest endpoints
├── scripts/                # Files used for preparing data and training models
│   ├── label_dataset.ipynb # Label, train and save models
│   ├── classifier.py       # Functions to label article using LLMs
├── function_app.py         # Azure Functions entry-point
└── host.json               # host configuration
```
---

## 🔍 Filtering
Large-language models are *excellent* at spotting whether a news item matters to an IT manager (they understand “zero-day”, “sev-1”, “S3 outage”, etc.).  
**Problem:** each call is nondeterministic and expensive, which is unacceptable for an always-on pipeline. So, I took another approach.

### 1 · Synthetic data
* I first generated a dataset of 200 articles for training and 50 articles for testing on chatGPT using o3.
### 2 · Labelling
* **Zero-shot prompt** (`prompts/classifier/v1.txt`) is sent to GPT-4o to label each headline + first paragraph (if any) with four Boolean flags:  
  `relevant`, `severe`, `wide_scope`, `high_impact`.  
* 1-shot+examples prompt ensures consistent labels → deterministic JSON.

### 3 · Embedding  
* **Sentence-Transformers `all-MiniLM-L6-v2`** (384-dim, frozen, L2-normalised).  
* Same vector is reused by *every* classifier → single forward pass per article.

### 4 · Filter
| Flag | Model | Class weight | Why logistic? |
|------|-------|--------------|---------------|
| `relevant` | Logistic R. (`lbfgs`, C chosen by 5-fold GridSearchCV) | `balanced` | High recall with linear decision surface, easy to threshold. |

Final values stored in `models/relevant_model.joblib`, ensuring deterministic predictions.

---

## 📈 Ranking
In the same lofic as filtering, I trained three tiny “weak learners”** – plain logistic-regression heads – on the frozen MiniLM embeddings.  
   *They’re “weak” in the boosting sense: individually simple, but in aggregate they capture enough signal.*

| Flag | Model | Class weight | Why logistic? |
|------|-------|--------------|---------------|
| `severe` | Logistic R. (`lbfgs`, C chosen by 5-fold GridSearchCV) | `balanced` | Separates “critical” vs “routine” with few features. |
| `wide_scope` | Logistic R. (`lbfgs`, C chosen by 5-fold GridSearchCV) | `balanced` | Captures vendor keywords + semantic distance. |
| `high_impact` | Logistic R. (`lbfgs`, C chosen by 5-fold GridSearchCV) | `balanced` | Learns phrases like “millions of records”. |

```text
importance_score =
    0.70 × ( 0.50·P(severe)
           + 0.30·P(wide_scope)
           + 0.20·P(high_impact) )
  + 0.30 × freshness
````
Elements are then ranked according to the importance_score

---

## 🚦 Pipeline

1. **Entry points (two ways in)**  
   * **Timer trigger `crawl_sources`**  
     * Fires every **6 h** (`0 0 */6 * * *`).  
     * Calls `crawl.crawl_and_process()` → pulls RSS feeds → returns an **array of dicts**.  
   * **HTTP route `POST /api/ingest`**  
     * Accepts a JSON **array** *or* **ND-JSON** stream pushed by clients.

2. **Shared ingest routine `ingest.ingest_articles()`**  
   1. **Hydrate** each raw dict into `models.Article`.  
   2. **Relevance filter**  
      * MiniLM embedding → `relevant_model.joblib`.  
      * Keep if `P(relevant) ≥ 0.55` (class-weight *balanced* → high recall).  
   3. **Importance scoring**  
      | Head (model) | Predicts | File | Default weight |
      |--------------|----------|------|----------------|
      | `severe_model` | zero-day / sev-1 / CVSS ≥ 9 | `models/severe_model.joblib` | **0.50** |
      | `wide_scope_model` | tier-1 vendor affected | `models/wide_scope_model.joblib` | **0.30** |
      | `high_impact_model` | millions of users / global outage | `models/high_impact_model.joblib` | **0.20** |
      * **Freshness** =`e^(−age / 72 h)` (weight **0.30**).  
      * All four scores are stored on the `Article` object.  
   4. **Compute total**  
      ```text
        importance_score =
            0.70 · ( 0.50 · P(severe)
                   + 0.30 · P(wide_scope)
                   + 0.20 · P(high_impact) )
          + 0.30 · freshness
      ```

3. **Persist – `crud.upload_articles()`**  
   * Batch **UPSERT** into Supabase `articles` table (idempotent on `id`).  
   * Columns include `severity_score`, `wide_scope_score`, `high_impact_score`, `importance_score`, `published_at`, etc.

4. **Retrieve – `GET /api/retrieve`**  
   * `retrieve.retrieve_events()` runs  
     ```sql
     SELECT * FROM articles
     ORDER BY importance_score DESC, published_at DESC
     LIMIT $n;
     ```  
   * Each element in the returned array is a **JSON object** enriched with scores
produced by the pipeline:

        ```jsonc
        {
        "id": "https://www.computerweekly.com/news/366627640/…",
        "title": "Luxury retailer LVMH says UK customer data was stolen in cyber attack",
        "body": "UK customers of luxury goods brand Louis Vuitton have been warned …",
        "published_at": "2025-07-14T10:45:00Z",
        "created_at": "2025-07-15T09:41:19.7979Z",
        "source": "computerweekly",

        // model-generated signals  (0 – 1 probabilities)
        "severity_score":     0.400745,
        "wide_scope_score":   0.585280,
        "high_impact_score":  0.859793,

        // final ranking value
        "score":   0.598855
        }

5. **Client usage**  
   * Dashboards, Slack bots, or SIEM webhooks hit **`/api/retrieve`** to obtain a ranked feed.  
   * All weights (`SEVERITY_WEIGHT`, `WIDE_SCOPE_WEIGHT`, `HIGH_IMPACT_WEIGHT`, `FRESHNESS_WEIGHT`) and the cron schedule are **overridable via environment variables**—no redeploy required.

---

## 📈 Pipeline diagram
```
┌─────────────────┐         internal call
│ crawl_sources   │       (timer function)
│  - crawler.py   │  <────────────────────────── Scheduler  (every 6 h)
└─────┬───────────┘
      │ raw dicts
      ▼
┌───────────────────────┐      
│ ingest_articles       │      HTTP POST /api/ingest
│  (http + shared code) │  <─────────────────────────── Client pushes new batches                     
└─────┬─────────────────┘                             
      │ Article dataclass objects               
      ▼                                         
┌───────────────────────────┐
│ filter.relevant_articles  │
│  • MiniLM embedding       │
│  • relevant_model         │
└─────┬─────────────────────┘
      │ labels + vectors
      ▼
 ─ keep only “True” ───────────────────────────────────────────
      ▼
┌─────────────────────┐
│ importance_score    │
│  • severe_model     │ 0.50 weight
│  • wide_scope_model │ 0.30 weight
│  • high_impact_model│ 0.20 weight
└─────┬───────────────┘
      │ scores injected into Article objects
      ▼
┌─────────────────────────┐
│ crud.upload_articles    │  ➜ Supabase `articles` table
└─────────────────────────┘





HTTP GET /api/retrieve
┌─────────────────┐
│  retrieve.py    │
└─────────────────┘
      │ ranking:
      │   ORDER BY importance_score DESC
      │   0.7*(0.5·severity + 0.3·scope + 0.2·impact) + 0.3·freshness
      ▼
┌─────────────────┐
│ JSON response   │
└─────────────────┘

```

## 🧰 Tech Stack Overview

| Layer | Choice | Why |
|-------|--------|-----|
| **Serverless runtime** | **Azure Functions** | Native timer & HTTP triggers, zero-ops scaling, easy CI/CD |
| **Scheduler** | Azure Timer Trigger (`crawl_sources`, 6-hour cron) | Keeps crawler code and API in the same deployment unit. |
| **Database** | **Supabase (PostgreSQL)** | Instant REST API, row-level security, “upsert” support, generous free tier for prototypes. Easy to set-up |
| **LLM providers** | OpenAI **GPT-4o** for one-off labelling · **o3** for synthetic headline generation | Best zero-shot quality (4o) and deterministic text generation (o3). |
| **ML library** | **scikit-learn** (LogisticRegression, GridSearchCV) | Fast, interpretable, deterministic. |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` | 384-dim, CPU-friendly, MIT license. Easy to set-up |
| **Frontend** | **Nuxt 3** SPA, deployed as static files to **AWS S3 + CloudFront** <br>*(separate repo: `https://github.com/you/it-news-frontend`)* | CDN-backed delivery, zero server maintenance. |
| **CI / CD** | GitHub Actions · pytest · coverage badge | Lints, unit-tests, and auto-deploys to Azure on push to `main`. |

---

### 🗄️  Supabase schema

#### `sources` table
| column | type | note |
|--------|------|------|
| `id` *(PK)* | `uuid` | auto-gen |
| `name` | `text` | “AWS status”, “Tom’s Hardware”… |
| `url`  | `text` | Feed endpoint |
| `type` | `text` | `rss` / `json` |

#### `articles` table
| column | type | note |
|--------|------|------|
| `id` *(PK)* | `text` | canonical URL or GUID |
| `title` | `text` | headline |
| `body` | `text` | first paragraphs |
| `published_at` | `timestamptz` |
| `source` | `text` |
| `severity_score` | `float4` |
| `wide_scope_score` | `float4` |
| `high_impact_score` | `float4` |
| `created_at` | `timestamptz` | *default now()* |

---

## 📈 Evaluating filtering & ranking
Done inside `scripts/label_dataset.ipynb` after training each model and ranking algorithms.

| Layer | Method | Metric |
|-------|--------|--------|
| **Filtering (relevant / irrelevant)** | • Use GPT-4o once as an “oracle” to relabel the test batch.<br>• Compare my model’s output → **Precision / Recall** (recall is the KPI). | Target: **R ≥ 0.80**, P ≥ 0.70 |
| **Ranking inside the relevant set** | • Three independent LLMs score `severe`, `scope`, `impact`. <br>• Average → ground-truth **importance_score**. <br>• Items above the median count as “positive”. | **Precision@5**, **nDCG@5**, MAP |

*This keeps evaluation deterministic, avoids manual labelling, and focuses on recall (don’t miss critical news) while still checking that top-ranked items match the LLM consensus.*

### 🔗  External repos

* **Backend (this repo):** serverless API, ML models, data pipeline  
* **Frontend:** [`it-news-frontend`](https://github.com/you/it-news-frontend) – Nuxt 3 SPA that consumes `/api/retrieve` and renders a real-time dashboard.

---

## 🚀 Quick-start (local)

```bash
# 1. Clone & install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Set env vars
cp env.example .env   # edit DB path, feed URLs, etc.

# 3. Run all functions locally
func start   # needs Azure Functions Core Tools ≥4

# 4. Trigger crawl manually
curl http://localhost:7071/api/crawl

Note: The timer trigger in function_app.py fires automatically every 6 h
(0 0 */6 * * *). Set run_on_startup=True while debugging.