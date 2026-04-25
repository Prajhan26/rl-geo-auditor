# Round 2 Problem Statement

This file defines our Round 2 direction clearly so we do not drift tomorrow.

---

## 1. Selected Theme

Our primary theme is:

**Theme #3.1 Professional Tasks**

Why this is the best fit:

- GEO auditing is a real professional workflow
- the agent is expected to inspect structured signals and do real audit work
- the environment is not a toy game or casual chat task
- the workflow can be benchmarked, rewarded, and improved

Secondary overlap:

- limited overlap with **Theme #2 Long-Horizon Planning**
- only because a GEO audit can be multi-step and require staged inspection
- but our main identity is still a professional-task environment

---

## 2. Core Problem Statement

LLMs are increasingly used in content discovery, answer engines, and search-adjacent workflows, but they are not reliably trained to perform structured GEO webpage audits. Generic prompting can produce plausible advice, but not consistently accurate, measurable, or benchmarkable audit behavior.

We propose a **GEO Audit Environment** where an agent inspects a webpage and target query, performs structured audit actions, submits issue and positive findings, and receives a verifiable reward based on benchmark truth.

The purpose of this environment is not just to produce one-off suggestions. The purpose is to create a **training and evaluation environment** for improving and comparing agent behavior on GEO auditing tasks.

---

## 3. Why This Problem Matters

This problem matters because:

- GEO and answer-engine discoverability are emerging real-world needs
- teams increasingly want AI systems to evaluate content quality for LLM-mediated discovery
- most current tools focus on direct user suggestions, not on training or evaluating agents
- there are far fewer RL/LLM environments for GEO auditing than for games, coding, or math

This gives us a fresh angle:

> turn GEO auditing from a vague content-review task into a measurable environment for agent learning and evaluation

---

## 4. The Environment

The environment is a GEO auditing world where each episode represents one webpage audit task.

Each task includes:

- a page URL
- a target query
- structured webpage signals
- hidden benchmark truth used for grading

The agent does not directly see the grading labels.
It sees the observation and must act inside the environment.

The environment exposes:

- `reset()`
- `step(action)`
- `state()`

and is served through FastAPI / OpenEnv-style APIs.

---

## 5. Agent Capabilities

Inside this environment, the agent should be able to:

- inspect webpage metadata and structure
- reason over title, meta description, headers, schema, and trust signals
- identify likely GEO issues
- identify positive GEO signals
- choose which audit actions to take next
- decide when it has enough evidence
- submit a final audit report

This makes the agent more than a text generator.
It becomes a policy operating inside a structured task world.

---

## 6. Task Structure

Our current task structure uses:

- easy tasks
- medium tasks
- hard tasks

These differ in how obvious or nuanced the GEO issues are.

Examples of what difficulty can mean:

- **easy**: missing schema, missing meta description, missing author
- **medium**: content structure weaknesses, weak title quality, weak answer formatting
- **hard**: nuanced direct-answer quality, subtle trust/authority issues, non-obvious discoverability tradeoffs

This gives us a natural curriculum structure if we train later.

---

## 7. Reward Model / Evaluation Logic

The reward is programmatic.

The environment compares:

- issues flagged by the agent
- positives marked by the agent

against:

- benchmark issue labels
- benchmark positive labels

The current reward logic:

- rewards correct findings
- penalizes false positives
- supports structured, reproducible evaluation

Important Round 2 framing:

This reward is a **proxy for GEO audit quality**, not the full reality of GEO.
That is why verifier realism and reward hacking analysis matter in Round 2.

---

## 8. Post-Training / Improvement Strategy

Our practical Round 2 strategy is:

1. start from a capable instruct model
2. give the model clear task formatting and action structure
3. optionally use a light warm start or small SFT-style behavioral seed
4. train or refine behavior using environment rewards
5. compare baseline vs improved behavior on held-out GEO tasks

Important clarification:

- we do **not** train the environment
- we train the **agent/model against the environment**

Possible tooling:

- OpenEnv for environment interaction
- Hugging Face TRL for RL training
- GRPO as the RL optimization method
- Unsloth as the efficiency layer

---

## 9. What Is Already Built

We are not starting this from zero.

Already built:

- working environment server
- FastAPI/OpenEnv-style interface
- Docker packaging
- Hugging Face Space deployment
- benchmark pipeline
- frozen real benchmark at `49` pages
- programmatic grader
- heuristic baseline
- learned policy baseline

This means Round 2 is about:

- stronger positioning
- stronger verifier defense
- stronger training story
- stronger evidence of improvement

---

## 10. What We Need To Show In Round 2

To be competitive, we should show:

- a clear problem statement
- a clear environment description
- a coherent reward model
- a minimal training script using TRL or Unsloth
- evidence of before/after improvement
- readable plots or metrics
- a clean explanation of why this is a meaningful professional-task environment

---

## 11. One-Sentence Version

> We built a GEO auditing environment for training and evaluating LLM agents on a real professional workflow, where agents inspect webpage signals, submit audit findings, and receive verifiable rewards against benchmark truth.

---

## 12. Slightly Longer Pitch Version

> Our Round 2 project is a professional-task LLM environment for GEO webpage auditing. Each episode gives an agent a webpage and target query, the agent inspects structured page signals step by step, flags issues and positives, and is scored against benchmark truth. The environment is deployable, verifiable, and suitable for training or evaluating agent behavior rather than just generating one-off content suggestions.
