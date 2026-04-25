# Round 2 Training Target

This is a small internal reference note for our team.

Its purpose is to answer one question clearly before we spend compute:

> What exactly are we trying to improve, and how will we know if training helped?

---

## Training Target

- **Behavior to improve:** improve the agent’s ability to perform structured GEO audits by selecting relevant checks, identifying true issues, avoiding hallucinated issues, and producing stronger final submissions

- **Baseline:** the same instruct model before any Round 2 fine-tuning or RL, evaluated on the same held-out task slice

- **Main metric:** average final environment reward on held-out GEO tasks

- **One backup metric:** false positive rate on issue flags

- **Reward hacking risk:** the model may learn to over-report frequent issue types or exploit benchmark patterns to raise reward without improving real audit quality

---

## Why This File Exists

Without this note, training can become vague:

- we run a model
- we see some reward numbers
- we do not know what success means
- we do not know whether the improvement is real

This file prevents that.

It gives us:

- one clear behavior target
- one clear baseline
- one main metric
- one backup metric
- one known failure mode to watch

---

## Practical Meaning

This note should guide:

- notebook design
- baseline evaluation
- training analysis
- README result framing
- judge/demo explanation

---

## One-Line Version

> We want the model to get better at structured GEO auditing, and we will judge that mainly by average held-out environment reward, while watching false positives so benchmark score is not mistaken for real quality.
