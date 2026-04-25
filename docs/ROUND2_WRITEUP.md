# Round 2 Writeup Draft

This file is our markdown writeup draft for tomorrow.

We can later:

- polish it into a Hugging Face blog-style post
- link it from the README
- reuse it for slides or a short pitch

---

# GEO Audit Environment: Training and Evaluating LLM Agents on a Professional GEO Workflow

## Problem

LLMs are increasingly used in content discovery, answer engines, and search-adjacent workflows, but they are not reliably trained to perform structured GEO webpage audits. Generic prompting can produce plausible advice, yet it often lacks consistency, measurability, and strong grounding in real audit behavior.

We wanted to turn GEO auditing into something an agent could actually be **evaluated and improved on**, not just something that “sounds helpful.”

## Environment

We built a **GEO Audit Environment** where each episode is a webpage audit task.

For each task:

- a webpage and target query are loaded
- the agent receives structured observations from the page
- the agent performs audit actions step by step
- the agent flags issues and positives
- the environment grades the final audit against benchmark truth

The environment follows an OpenEnv-style interaction loop with:

- `reset()`
- `step(action)`
- `state()`

and is exposed as a FastAPI application, containerized with Docker, and deployed on Hugging Face Spaces.

## Why this is interesting

Most existing GEO or SEO tools focus on directly helping a user audit a page.

Our project is different:

- it is an **environment for agent learning and evaluation**
- it turns a real professional workflow into a measurable task world
- it makes GEO auditing benchmarkable instead of purely subjective

This puts it closer to training infrastructure than a normal audit app.

## Agent Behavior

Inside the environment, the agent can:

- inspect page metadata and structure
- check schema and trust signals
- evaluate title, meta description, headers, and direct-answer quality
- flag issues
- mark positives
- decide when to submit a final report

This gives the environment a structured action space instead of a single free-form text answer.

## Reward and Evaluation

The environment uses a programmatic grader.

It compares:

- the issues the agent flagged
- the positives the agent marked

against benchmark truth for that task.

This creates a verifiable reward signal:

- correct findings increase reward
- false positives are penalized
- the workflow becomes measurable and reproducible

This is important because it reduces reliance on vague “looks good” judgments.

## Current Foundation

Before Round 2, we already built:

- the full environment server
- Docker packaging
- Hugging Face deployment
- synthetic benchmark pipeline
- a frozen real benchmark of `49` reviewed pages
- heuristic and learned baseline policies

That means Round 2 is not about proving that the environment exists.
It is about showing:

- why the environment matters
- why the reward is meaningful
- how training can improve agent behavior inside it

## Training Direction

Our training direction is:

1. start from a capable instruct model
2. give it the GEO task format and action structure
3. optionally use a small warm start
4. connect the model to the environment reward loop
5. compare baseline vs improved behavior

Tooling direction:

- OpenEnv for the environment
- Hugging Face TRL for RL training
- GRPO as the optimization method
- Unsloth for efficiency

## What we want to show

The most important evidence for judges is:

- a clean environment
- coherent reward logic
- a minimal training script
- before/after comparison
- measurable improvement

That could look like:

- baseline reward curve
- trained reward curve
- baseline audit example
- improved audit example

## Why this matters

This environment matters because it turns GEO auditing into a trainable and testable professional-task environment.

Instead of only asking whether an LLM can produce nice-sounding suggestions, we can ask:

- can the agent perform the audit workflow?
- can it improve under verifiable reward?
- can different agents be compared fairly on the same GEO tasks?

That is the deeper contribution of the project.

## Limitations

Our current reward is still a proxy for full GEO quality, not a perfect measure of real-world success.
The current benchmark is meaningful but still limited in diversity and realism compared with the full web.
These are exactly the kinds of issues we want to improve in Round 2 through stronger verifier reasoning, better reward defense, and clearer training evidence.

## Closing

Our project is best understood as a **professional-task environment for GEO auditing**, not just a webpage checker.

We built the environment layer where agents can be tested, compared, and improved on real GEO tasks using structured actions and verifiable rewards.
