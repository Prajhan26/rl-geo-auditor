# Round 2 Execution Spec

This file is our working spec for the next 36 hours.

The goal is simple:

- know exactly what we are building
- know what is mandatory
- know who should do what
- know what success looks like at each step
- avoid vague busywork and random RL exploration

---

## 1. Mission

Our Round 2 mission is:

> turn our existing GEO audit environment into a training-ready, judge-friendly Round 2 submission with a minimal real training loop, measurable before/after evidence, and a clear professional-task story.

We are **not** starting from zero.
We already have:

- a deployable environment
- OpenEnv-style API
- Docker packaging
- Hugging Face Space
- benchmark pipeline
- reward/grader
- baseline policies

So our real job now is:

- tighten the environment for Round 2
- add a minimal training path
- capture evidence of improvement
- package the story clearly

---

## 2. Must-Haves

These are the non-negotiables for our Round 2 submission.

### Environment / infra

- working OpenEnv-compliant environment
- Hugging Face Space still working
- README updated for Round 2

### Training

- minimal training script or notebook using TRL or Unsloth
- runnable notebook or Colab link
- baseline vs trained comparison

### Evidence

- reward or metric plot
- one or two before/after examples
- metrics table or concise summary

### Story

- clear problem statement
- clear theme alignment
- clear explanation of reward logic
- clear explanation of what improved

### Submission support material

- writeup markdown in repo
- notebook linked from README
- optional mini video or slide deck if time allows

---

## 3. What We Do NOT Need

To stay focused, we explicitly avoid these traps:

- redesigning the full environment from scratch
- chasing multiple themes at once
- training a large model from scratch
- reading every tutorial and paper before starting
- adding lots of reward complexity before the first end-to-end run works
- polishing visuals before we have training evidence

---

## 4. Team Collaboration Model

We should split the work so neither person blocks on the other for basic progress.

### Person A: Environment / reward / product story owner

Responsible for:

- environment sanity
- reward sanity
- benchmark/eval sanity
- README and writeup correctness
- final story and positioning

### Person B: Training / notebook owner

Responsible for:

- notebook or Colab setup
- model selection
- TRL / Unsloth / GRPO wiring
- baseline run
- training run
- plots and saved outputs

### Shared ownership

Both people should jointly decide:

- exact training target
- what metric proves improvement
- what final demo example to show

---

## 5. Collaboration Rules

These rules are here so your friend does not have to rely on me every 15 minutes just to know if the work is valid.

### Rule 1

Before starting any task, write down:

- what the output should be
- what “done” means
- what file(s) will change

### Rule 2

Each work item must end with one of:

- `done`
- `blocked`
- `needs review`

No vague “almost finished”.

### Rule 3

If a task cannot be explained in 2-3 sentences, it is too fuzzy and needs to be broken down.

### Rule 4

Do not make silent design changes.
If one person changes:

- reward logic
- benchmark split
- training target
- theme framing

the other person should know immediately.

### Rule 5

Use artifacts, not memory.
Save:

- plots
- metrics
- notes
- notebook outputs

Do not rely on “we saw something earlier”.

### Rule 6

If a training run fails, debug in this order:

1. environment
2. reward / verifier
3. baseline inference
4. notebook wiring
5. trainer config

Do not blame the optimizer first.

### Rule 7

Do not scale until the smallest run works end to end.

---

## 6. Current Work Inventory

This is what we already have right now.

### Already built

- environment server
- FastAPI layer
- OpenEnv-style routes
- Dockerfile
- Hugging Face deployment
- real benchmark at `49` pages
- grader
- heuristic baseline
- learned policy
- Round 2 docs

### Missing / to build now

- minimal Round 2 training notebook
- actual before/after training evidence
- reward plot(s)
- README Round 2 packaging
- writeup final polish
- optional video/slides

---

## 7. What I Need From You

These are the things I need from your side so I can help effectively:

### From you

- keep the direction locked: Theme #3.1
- keep the problem statement locked
- tell me who is doing what
- send me exact outputs/errors when something fails
- avoid making silent random changes

### From your friend

- own a concrete workstream
- report results in artifacts, not vague status
- say clearly if blocked
- avoid changing core logic without alignment

### From both of you

- treat this like execution, not exploration
- optimize for evidence of improvement
- use the docs as the source of truth

---

## 8. What We Need To Tighten Before Moving Forward

Before serious training, these need to be tight:

### A. Problem statement

Needs to be fixed and stable.

Success looks like:

- one primary theme
- one clean one-sentence project description
- one clean one-minute explanation

### B. Reward understanding

Needs to be explicit.

Success looks like:

- we can explain what reward measures
- we can explain what reward misses
- we can name 3 reward hacking risks

### C. Training target

Needs to be specific.

Success looks like:

- we know what “improvement” means
- we know which metrics we will compare
- we know what baseline is being beaten

### D. Notebook scope

Needs to be narrow.

Success looks like:

- one small runnable baseline
- one small training loop
- one post-training eval

### E. README / writeup structure

Needs to be planned early.

Success looks like:

- placeholders known
- proof artifacts known
- nothing important forgotten at the end

---

## 9. 36-Hour Plan

### Phase 1: Lock direction

Goal:

- no more ambiguity

Success looks like:

- theme locked
- training target locked
- roles locked

### Phase 2: Tighten environment + reward

Goal:

- training-ready environment

Success looks like:

- reward understood
- reward limitations written down
- no unknown blocker in env loop

### Phase 3: Build minimal notebook

Goal:

- first real end-to-end run

Success looks like:

- baseline run works
- training run works
- post-training eval works

### Phase 4: Capture evidence

Goal:

- proof, not just code

Success looks like:

- one plot
- one comparison table
- one before example
- one after example

### Phase 5: Package

Goal:

- judges can understand it fast

Success looks like:

- README updated
- writeup linked
- notebook linked
- HF Space linked
- story is coherent

---

## 10. Success Criteria By Workstream

This section is the most important one.
It answers: “what does success look like at each step?”

### Workstream A: Theme + problem statement

Success looks like:

- we can state the theme in one line
- we can explain why it fits in three bullets
- we do not keep reinterpreting the project

Failure looks like:

- “maybe we are also theme 1/2/4”
- unclear identity
- changing framing every hour

### Workstream B: Reward / verifier

Success looks like:

- reward is understood
- reward weaknesses are known
- reward hacking risks are listed

Failure looks like:

- “score went up, so it must be good”
- no idea what the reward is actually teaching

### Workstream C: Training notebook

Success looks like:

- runs from setup to evaluation
- baseline and trained outputs can both be shown
- metrics are saved

Failure looks like:

- notebook exists but was never run end to end
- no saved outputs
- only code, no evidence

### Workstream D: Proof of learning

Success looks like:

- baseline vs trained comparison is visible
- at least one metric moved in the right direction
- examples show the difference

Failure looks like:

- “we think it improved”
- no chart
- no example

### Workstream E: Storytelling

Success looks like:

- non-technical person can follow the story
- technical person can trust the setup
- README answers problem / environment / reward / training / results

Failure looks like:

- only API docs
- only code dumps
- no clear why-this-matters explanation

---

## 11. What We Should Ask Before Every Major Step

Before any major step, ask:

1. what exactly are we producing?
2. how will we know this worked?
3. what artifact proves it?
4. does this improve the final submission, or is it just busywork?

If we cannot answer these, we should pause before continuing.

---

## 12. Spec Files To Use Together

Use these docs together:

- `docs/ROUND2_PROBLEM_STATEMENT.md`
- `docs/ROUND2_WRITEUP.md`
- `docs/ROUND2_TRAINING_NOTEBOOK_PLAN.md`
- `docs/ROUND2_CHECKLIST_AND_RULES.md`
- `docs/ROUND2_EXECUTION_SPEC.md`

This file is the operating spec.
The others give the detailed content.
