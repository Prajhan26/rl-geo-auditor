# GEO Audit Environment - Quick Start Summary

## What We're Building

**An RL environment that trains AI to audit webpages for GEO (Generative Engine Optimization) issues.**

```
GEO = Making content get cited by AI (ChatGPT, Perplexity, Claude)
     Not just SEO (Google rankings)
```

---

## The Core Loop

```
1. reset() → Load a webpage
2. AI checks elements (title, meta, schema, etc.)
3. AI flags issues it finds
4. AI submits report
5. Compare to ground truth → Calculate reward
6. Repeat 1000x → AI learns to find real issues
```

---

## Files to Create

```
geo-audit-env/
├── server/
│   ├── __init__.py         # Exports
│   ├── app.py              # FastAPI server
│   ├── environment.py      # Main logic
│   ├── grader.py           # Reward calculation
│   └── models.py           # Pydantic models
├── data/
│   ├── task1_easy.json     # 20 pages with obvious issues
│   ├── task2_medium.json   # 20 pages with subtle issues
│   └── task3_hard.json     # 20 pages for competitive analysis
├── inference.py            # REQUIRED - runs AI against env
├── Dockerfile              # Container config
├── openenv.yaml            # Environment metadata
├── pyproject.toml          # Dependencies
└── README.md               # Documentation
```

---

## Available Actions

```python
ACTIONS = [
    "check_title_tag",
    "check_meta_description",
    "check_headers",
    "check_schema",
    "check_direct_answer",
    "check_content_structure",
    "check_word_count",
    "check_trust_signals",
    "flag_issue",
    "submit_report"
]
```

---

## Issue Types

```python
ISSUE_TYPES = [
    # Critical
    "missing_title_tag",
    "missing_meta_description",
    "no_direct_answer",
    
    # High
    "weak_title_tag",
    "weak_meta_description",
    "buried_answer",
    "missing_faq_schema",
    "missing_howto_schema",
    "no_headers",
    
    # Medium
    "missing_article_schema",
    "thin_content",
    "no_author",
    "no_date",
    
    # Low
    "no_sources",
    "poor_header_structure"
]
```

---

## Reward Formula

```python
# F1 Score with hallucination penalty
reward = F1_score - (hallucinations * 0.1)

# Where:
F1 = 2 * (precision * recall) / (precision + recall)
precision = true_positives / (true_positives + false_positives)
recall = true_positives / (true_positives + false_negatives)

# Examples:
# Found 4/5 real issues, 0 fake → ~0.88
# Found 3/5 real issues, 2 fake → ~0.50
# Found 0/5 real issues, 3 fake → 0.00
```

---

## Team Split

| Person | Responsibility | Hours |
|--------|---------------|-------|
| Hijak | Code, Docker, Deploy | 16 |
| Hari | Find 60 pages, Label issues | 12 |

---

## Key Commands

```bash
# Setup
pip install openenv-core
openenv init geo_audit

# Local test
uvicorn server.app:app --reload --port 8000

# Docker
docker build -t geo-audit-env .
docker run -p 8000:8000 geo-audit-env

# Deploy
openenv push --repo-id USERNAME/geo-audit-env

# Validate
openenv validate

# Run inference
python inference.py
```

---

## Submission Requirements

```
☐ HF Space works
☐ 3 tasks (easy/medium/hard)
☐ 20 pages per task
☐ Rewards 0.0-1.0
☐ inference.py runs
☐ Logs: [START], [STEP], [END]
☐ Runtime < 20 min
☐ README complete
```

---

## Documents in This Package

1. **01-HIJAK-TECHNICAL-GUIDE.md** - Full code and setup
2. **02-HARI-DATA-COLLECTION-GUIDE.md** - How to find and label pages
3. **03-DATA-FORMAT-SPEC.md** - JSON format for data
4. **04-TIMELINE-COORDINATION.md** - Hour-by-hour plan
5. **05-QUICK-START.md** - This summary

---

## Let's Go! 🚀
