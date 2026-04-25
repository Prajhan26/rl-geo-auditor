# Round 2 Default Decisions

This file exists to reduce unnecessary back-and-forth.

The rule is:

> Follow these defaults unless you are blocked, changing a core design decision, or the output is ambiguous.

If the next step follows these defaults, continue without asking.

---

## 1. Theme

- Primary theme = **Theme #3.1 Professional Tasks**
- Do not re-open theme selection unless there is a serious reason

---

## 2. Project Identity

- This is a **training/evaluation environment for GEO auditing**
- It is **not** just a normal GEO audit app
- It is **not** a toy environment

---

## 3. Training Architecture

- First training/debugging path should use the **environment locally**
- Do **not** use the live Hugging Face Space as the primary training dependency
- Hugging Face Space is mainly for **deployment/demo**

---

## 4. Baseline Rule

- Always run a **notebook/script-specific baseline first**
- Do not assume old benchmark numbers are enough for the new training setup
- Historical anchors are useful, but current training needs its own baseline

Historical anchors:

- heuristic real benchmark score: about `0.988`
- learned policy real benchmark score: about `0.865`

---

## 5. Warm Start Rule

- “Warm start” means:
  - prompt scaffolding
  - task formatting
  - maybe a few example trajectories
- It does **not** mean full heavy SFT by default
- Do not assume we are doing a large SFT pipeline unless explicitly decided

---

## 6. First Goal

The first goal is **not full training**.

The first goal is:

1. connect to the environment
2. load one task
3. run one baseline episode
4. print or save reward/output

Only after that should we expand.

---

## 7. First Training Rule

- Keep the first training run **small**
- Do not scale first
- Do not optimize first
- First prove the loop works end to end

---

## 8. Model Rule

- Use a capable instruct model
- Do **not** try to train from scratch
- Do **not** make the model choice overly fancy before the first working loop exists

---

## 9. Reward Rule

- Treat reward as a **proxy**, not the full real goal
- Do not assume “reward went up” automatically means “behavior improved”
- Save examples so we can inspect quality, not just metrics

---

## 10. Artifact Rule

Every meaningful step should leave an artifact:

- code file
- notebook cell output
- log
- screenshot
- metric table
- plot

Do not rely on memory alone.

---

## 11. Escalation Rule

Only escalate if one of these is true:

1. **Blocked technically**
2. **Changing a core design decision**
3. **Output is ambiguous and cannot be judged confidently**

If none of these is true, continue.

---

## 12. Check-In Rule

- Default check-in cadence = every **45 to 60 minutes**
- Check-ins should focus only on:
  - blockers
  - design changes
  - ambiguous results

Not every small step.

---

## 13. Update Format

When sending an update, use this format:

```text
Task:
Status: DONE / BLOCKED / NEEDS REVIEW
What I changed:
Proof:
Next move:
Blocker:
```

---

## 14. Immediate Current Defaults

Right now, the defaults are:

- use the repo as currently structured
- read only the core Round 2 docs first
- create `scripts/round2_train.py`
- run baseline before TRL/GRPO wiring
- keep the first workflow local and minimal

---

## 15. One-Line Operating Rule

> Continue by default. Stop only for blockers, design changes, or ambiguous results.
