---
title: GEO Audit Environment
emoji: "🔎"
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
short_description: Reinforcement-learning-style GEO webpage audit environment with FastAPI endpoints.
---

# GEO Audit Environment

A reinforcement-learning-style GEO auditing environment for hackathon use.

## What This Project Does

This project simulates a reinforcement-learning-style audit workflow for
webpages. An agent:

1. receives a page and target query
2. inspects page signals such as title tags, schema, headers, trust signals,
   and sources
3. flags GEO issues
4. submits a report
5. receives reward based on agreement with labeled ground truth

The repo now contains both:

- a heuristic baseline policy in `inference.py`
- a learned Q-policy in `train_q_policy.py`

## Project Structure

```text
server/
  app.py             FastAPI app
  api_models.py      Typed API request/response schemas
  environment.py     Audit environment logic
  grader.py          Reward calculation
  models.py          Action/observation/state models
data/
  task1_easy.json    Easy task pages
  task2_medium.json  Medium task pages
  task3_hard.json    Hard task pages
artifacts/           Saved policy and evaluation reports
inference.py         Heuristic baseline policy
train_q_policy.py    Learned Q-policy training loop
compare_policies.py  Heuristic vs learned evaluation
analyze_policies.py  Per-page error analysis
openenv.yaml         Environment metadata
Dockerfile           Container setup
```

## Core Concepts

- Environment: the world and rules the agent interacts with
- Observation: the page signals the agent can see
- Action: one audit step such as `check_schema` or `flag_issue`
- Reward: how well the final audit report matches the labeled truth

## Reward Design

The environment uses an F1-style reward with a hallucination penalty.

- True positives improve reward
- Missed issues reduce recall
- Invented issues reduce precision and also incur a penalty

This encourages the agent to find real issues without over-flagging.

Special case:

- a clean page with no issues gets reward `1.0` when the agent correctly flags nothing

## Local Setup

### Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Run the baseline audit

```bash
python3 inference.py
```

### Train the learned Q-policy

```bash
python3 train_q_policy.py
```

### Compare heuristic vs learned policy

```bash
python3 compare_policies.py
```

### Analyze page-by-page misses

```bash
python3 analyze_policies.py
```

### Run the local smoke test

```bash
./venv/bin/python scripts/smoke_server.py
```

### Start the API locally

```bash
./venv/bin/python scripts/run_server.py
```

Or with Uvicorn directly:

```bash
./venv/bin/uvicorn server.app:app --host 127.0.0.1 --port 8000
```

## API Endpoints

### `GET /health`

Returns a simple status payload.

### `GET /metadata`

Returns environment metadata and supported actions.

### `POST /reset`

Starts a new audit episode.

Example body:

```json
{
  "task_difficulty": "easy"
}
```

### `POST /step`

Applies one action to the current episode.

Example body:

```json
{
  "action_type": "flag_issue",
  "issue_type": "missing_meta_description",
  "severity": "critical",
  "details": "Meta description is missing."
}
```

## Docker

### Build

```bash
docker build -t geo-audit-env .
```

### Run

```bash
docker run -p 8000:8000 geo-audit-env
```

Then open:

```text
http://localhost:8000/health
```

Or browse the API docs:

```text
http://localhost:8000/docs
```

## OpenEnv Validation

Run:

```bash
./venv/bin/openenv validate .
```

Current status: passing.

## Current Benchmark

Latest full-dataset comparison:

- easy: `1.000`
- medium: `1.000`
- hard: `1.000`
- overall: `1.000`

See:

- `artifacts/comparison_report.json`
- `artifacts/policy_analysis.json`
- `artifacts/training_report.json`

## Current Status

- Environment working locally
- Heuristic baseline working
- Learned Q-policy working
- FastAPI server working
- Typed Swagger docs working
- OpenEnv validation passing
- Dockerfile present
- Reporting artifacts generated

## Next Steps

- Expand the dataset from the current 15 pages to the full 60-page target
- Update `openenv.yaml` if the submission format requires explicit task definitions
- Verify Docker build end to end
- Deploy the API to Hugging Face Spaces
- Verify live `/reset` and `/step` responses on the deployed Space
