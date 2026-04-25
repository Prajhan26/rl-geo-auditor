# Round 2 Training Notebook Plan

This file is our plan for tomorrow's Colab / notebook work.

The goal is not to improvise training under time pressure.
The goal is to know exactly what we want to run, what evidence we want to collect, and what outputs we need for judging.

---

## 1. Notebook Goal

The notebook should prove three things:

1. the environment is usable from training code
2. a model or agent can be run against it
3. we can show measurable before/after improvement or at least meaningful reward change

This is more important than making the notebook fancy.

---

## 2. Preferred Notebook Story

The notebook should tell this story:

1. load the environment
2. show a baseline agent/model run
3. run a small training loop
4. evaluate again
5. compare before vs after
6. save plots and example outputs

That gives judges a clean narrative.

---

## 3. Minimal Notebook Sections

### Section A: Setup

Include:

- install dependencies
- import required libraries
- load environment client / local environment
- confirm environment connectivity

Good output:

- environment responds
- task loads
- one sample observation is visible

### Section B: Baseline Run

Run:

- a baseline model or baseline policy
- on a small set of tasks

Capture:

- average reward
- example outputs
- task success indicators

Good output:

- clear baseline score
- one example of baseline behavior

### Section C: Training Configuration

Show:

- model being used
- why that model was chosen
- training approach:
  - warm start only
  - RL only
  - light warm start + RL
- reward source
- optimizer/trainer choice

For example:

- TRL
- GRPO
- Unsloth for efficiency

### Section D: Small Training Run

Run:

- a short but real training loop
- enough steps for visible movement

Track:

- average reward over time
- component reward behavior if available
- failure / timeout behavior

Important:

- keep first run small
- do not start with full-scale training

### Section E: Post-Training Evaluation

Run:

- the trained model on the same or held-out task slice

Compare:

- baseline reward vs trained reward
- baseline behavior vs trained behavior
- failure examples vs improved examples

### Section F: Save Evidence

Save:

- plots as `.png`
- key metrics in a small table
- one or two example task transcripts

These assets should later be linked in the README.

---

## 4. Metrics To Capture

At minimum, capture:

- average reward
- task-level score
- false positive count or rate
- missed issue count or rate
- formatting / action validity

If possible, also capture:

- rollout length
- proportion of successful submissions
- component reward breakdown

---

## 5. Before / After Evidence We Need

Judges will care more about visible improvement than about fancy terminology.

So we should capture:

### Before

- one baseline metric block
- one example baseline audit

### After

- one post-training metric block
- one improved audit example

### Comparison

- one simple table
- one simple reward plot

---

## 6. Practical Training Strategy For Our Project

For our GEO project, the safest strategy is:

1. start from a capable instruct model
2. use clear task formatting
3. optionally add light warm start behavior
4. train with environment reward
5. measure baseline vs trained performance

Important:

- do not try to train from scratch
- do not make the first run too large
- do not trust reward alone without checking actual examples

---

## 7. What To Watch During Training

We should not monitor only one scalar.

Watch:

- average reward
- whether outputs are still valid
- whether agent behavior becomes repetitive or suspicious
- whether score increase matches actual task quality improvement

If reward rises but quality looks weird, stop and inspect.

---

## 8. Risks To Watch For

Big risks:

- reward hacking
- over-flagging issues
- poor formatting
- unstable training
- environment loop bugs mistaken for model problems

If something looks off, debug in this order:

1. environment
2. verifier / reward
3. baseline inference
4. training loop

---

## 9. Deliverables We Want By End Of Training

By the end of tomorrow, the ideal output is:

- one runnable notebook
- one or more saved plots
- one baseline vs trained comparison
- one short explanation of what changed
- links ready for README

---

## 10. README Links We Should Prepare To Add

Later, the README should link to:

- Hugging Face Space
- Round 2 writeup markdown
- Colab notebook or `.ipynb`
- saved plots
- optional short video / slides

---

## 11. One-Sentence Notebook Goal

> Show that our GEO environment is not only deployable, but also usable as a real training loop where agent behavior measurably improves against structured environment rewards.
