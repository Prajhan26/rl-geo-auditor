# RL Geo Auditor — Progress Log

## Project Goal

Building a reinforcement-learning-style **GEO audit environment** that trains
an agent to inspect webpages, identify GEO issues, and submit an audit report
based on signals such as metadata, structure, schema, trust signals, and
citations.

---

## What I Built First

### 1. RL Foundations

Learned and implemented the core RL loop manually:

* state
* action
* reward
* episode loop

Built Q-learning from scratch and understood:

* Q-table
* policy
* exploration vs exploitation
* reward shaping

### 2. Grid-World Prototype

Built a small navigation-based RL prototype before moving to the real audit
environment.

Implemented:

* 1D goal movement
* 2D grid movement
* obstacles
* reward-based pathfinding
* simple path visualization

This phase was useful because it made the RL mechanics clear before shifting to
the real GEO use case.

### 3. Fixed Prototype Execution Issues

Resolved the Python run issue in `scripts/openenv_geo/`.

Root cause:

* `run_env.py` and `models.py` had accidental leading spaces in their filenames

Fix applied:

* renamed both files correctly

Result:

```bash
python3 scripts/openenv_geo/run_env.py
```

now works.

---

## Project Pivot

After reviewing the roadmap files from Claude, the project direction changed
from a simple grid navigator into a **GEO webpage-auditing environment**.

That roadmap is now stored in:

* `docs/claude-roadmap/`

Important realization:

* the grid world was a learning prototype
* the actual hackathon project is a webpage audit environment

---

## Current GEO Audit System

### 1. Environment Scaffold

Created the main project structure for the real environment:

```text
server/
  app.py
  environment.py
  grader.py
  models.py
data/
  task1_easy.json
  task2_medium.json
  task3_hard.json
inference.py
openenv.yaml
pyproject.toml
Dockerfile
README.md
```

### 2. Models

Defined the main environment objects in `server/models.py`:

* `GeoAuditAction`
* `GeoAuditObservation`
* `GeoAuditState`
* `PageData`
* `CheckResults`

These define:

* what the agent can do
* what the agent can see
* what hidden state the environment tracks

### 3. Environment Logic

Implemented the main audit environment in `server/environment.py`.

Current environment supports:

* `reset()` to start a new audit episode
* `step()` to apply actions
* page inspection actions such as:
  * `check_title_tag`
  * `check_meta_description`
  * `check_headers`
  * `check_schema`
  * `check_direct_answer`
  * `check_word_count`
  * `check_trust_signals`
  * `check_sources`
* `flag_issue`
* `submit_report`

### 4. Reward System

Implemented grading logic in `server/grader.py`.

Current reward design:

* F1-style scoring
* hallucination penalty for false issue flags
* bounded final reward from `0.0` to `1.0`

This means the agent is rewarded for:

* finding real issues
* avoiding fake issues

### 5. Sample Task Data

Built sample labeled datasets in:

* `data/task1_easy.json`
* `data/task2_medium.json`
* `data/task3_hard.json`

Current task data includes:

* multiple sample pages per difficulty
* target query
* visible page signals
* ground-truth issue labels

Signals currently modeled include:

* title tag
* meta description
* headers
* schema types
* author/date
* sources/citations
* word count
* first paragraph

### 6. Baseline Inference Agent

Implemented a working baseline policy in `inference.py`.

It now:

* reads page features
* creates issue candidates
* ranks them by confidence and severity
* chooses actions under a step budget
* flags issues
* submits the final report

This gives a strong heuristic benchmark and also bootstraps the learned policy.

### 7. Local API

Implemented a FastAPI app in `server/app.py`.

Working endpoints:

* `GET /health`
* `GET /metadata`
* `POST /reset`
* `POST /step`

Added typed request/response schemas so `/docs` is clean and demo-friendly.

### 8. Smoke Testing

Added local smoke validation through:

* `scripts/smoke_server.py`

Verified:

```bash
./venv/bin/python scripts/smoke_server.py
```

passes successfully.

### 9. Packaging, Container Setup, and Validation

Added:

* `pyproject.toml`
* `Dockerfile`
* `.dockerignore`
* `scripts/run_server.py`
* `README.md`
* `openenv.yaml`
* `uv.lock`

This means the project is now:

* installable
* locally runnable
* documented
* container-ready
* OpenEnv validation-ready

Verified:

```bash
./venv/bin/openenv validate .
```

passes.

### 10. Learned Q-Policy

Implemented the first true learned RL-style policy in `train_q_policy.py`.

It now:

* trains a Q-table over audit actions
* uses feature-based state instead of memorizing URLs
* bootstraps from the heuristic baseline
* uses reward shaping for hard-page behaviors
* saves learned weights to `artifacts/q_policy.json`

### 11. Policy Comparison and Reporting

Added:

* `compare_policies.py`
* `analyze_policies.py`
* `artifacts/training_report.json`
* `artifacts/comparison_report.json`
* `artifacts/policy_analysis.json`

This gives:

* side-by-side heuristic vs learned evaluation
* full-dataset average scores
* per-page miss analysis
* reusable training artifacts

---

## What I Learned So Far

### RL Learning

* RL is not just pathfinding; it is a decision loop under reward
* an environment needs clear state, action, and reward definitions
* a baseline policy is useful before training a learned one

### GEO System Design

* GEO auditing can be modeled as an environment instead of a checklist
* the observation space matters a lot
* reward design matters because it controls whether the agent becomes useful or
  hallucinatory
* dataset quality is critical because the reward depends on labeled truth
* scoring logic must correctly handle both bad pages and good pages

### Engineering

* packaging and API structure matter for hackathon delivery
* container support makes the project reproducible
* smoke tests are valuable for validating end-to-end flows quickly
* typed API schemas make the environment easier to demo and understand
* artifact reports are important because they preserve progress beyond terminal output

---

## Current Status

Completed:

* RL fundamentals
* grid-world prototype
* GEO audit environment scaffold
* reward/grader system
* labeled sample task data
* baseline inference agent
* learned Q-policy
* local API endpoints
* smoke testing
* Docker and packaging setup
* OpenEnv validation
* policy reporting and comparison

In progress:

* expanding task realism beyond the current benchmark
* final hackathon explanation / demo polish

Not built yet:

* larger real-world dataset
* hosted deployment / public demo target

Current benchmark status on the existing dataset:

* heuristic policy: `1.000` average
* learned policy: `1.000` average

Latest full comparison report:

* `artifacts/comparison_report.json`

Latest per-page analysis:

* `artifacts/policy_analysis.json`

---

## Current Commands

Run baseline inference:

```bash
python3 inference.py
```

Run server smoke test:

```bash
./venv/bin/python scripts/smoke_server.py
```

Run local API:

```bash
./venv/bin/python scripts/run_server.py
```

Train learned policy:

```bash
python3 train_q_policy.py
```

Compare heuristic vs learned policy:

```bash
python3 compare_policies.py
```

Analyze page-by-page misses:

```bash
python3 analyze_policies.py
```

Build Docker image:

```bash
docker build -t geo-audit-env .
```

Run OpenEnv validation:

```bash
./venv/bin/openenv validate .
```

---

## Next Steps

### Immediate Next Build

1. Expand the dataset beyond the current small benchmark
2. Add more “good” and mixed-quality pages to test generalization
3. Decide whether to deploy a hosted demo endpoint
4. Polish the hackathon explanation and submission story

### Hackathon Goal

Be able to clearly explain:

* what the environment is
* what the agent sees
* what actions it can take
* how reward is calculated
* how the baseline agent works
* how the learned policy improves through reward and evaluation

---

## Summary

* RL basics learned
* prototype grid world built
* roadmap reviewed and imported
* project pivoted to GEO audit environment
* end-to-end baseline environment built
* API, smoke test, and typed docs working
* Docker, validation, and docs added
* learned Q-policy implemented
* reporting and analysis added
* current dataset benchmark reaches `1.000` average
* next phase is larger-scale realism and final submission polish
