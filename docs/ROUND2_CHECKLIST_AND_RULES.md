# Round 2 Checklist and Rules

This file is our practical Round 2 operating guide.

It has four jobs:

1. show what is already strong in our project
2. show what still needs work for Round 2
3. give us a detailed working checklist
4. give us detailed rules so we do not optimize the wrong thing

---

## Part 1: What Is Already Strong

These are the areas where our project already has a strong foundation.

Use this status key:

- `[strong]` already in a good place
- `[partial]` working, but not yet defensible enough for deep review
- `[weak]` needs real improvement before we rely on it heavily

### Environment foundation

- `[strong]` `reset()`, `step()`, and `state()` exist
- `[strong]` the environment is exposed through FastAPI
- `[strong]` the environment can run locally
- `[strong]` the environment can run in Docker
- `[strong]` the environment is deployed on Hugging Face Spaces

### OpenEnv compliance

- `[strong]` `openenv.yaml` exists
- `[strong]` `openenv validate` passed
- `[strong]` the project passed Phase 1 automated validation
- `[strong]` `Dockerfile` is in the repo root
- `[strong]` `inference.py` is in the repo root

### Task design

- `[strong]` we have 3 core task levels:
  - easy
  - medium
  - hard
- `[strong]` the task is real-world enough:
  - GEO webpage auditing
- `[strong]` the environment includes a structured audit workflow

### Benchmarking

- `[strong]` we built a synthetic benchmark
- `[strong]` we built a real benchmark pipeline
- `[strong]` we froze the real benchmark at `49` reviewed pages
- `[strong]` we ran final real evaluation

### Reward and grading

- `[strong]` the grader is programmatic, not just vague human judgment
- `[strong]` false positives are penalized
- `[strong]` positives can also be marked
- `[partial]` the reward is structured and testable
- `[partial]` the verifier is useful, but not yet proven hard to game

### Submission and packaging

- `[strong]` Hugging Face Space deployment worked
- `[strong]` GitHub repo exists
- `[strong]` homepage `/` route was fixed
- `[strong]` submission-compatible `inference.py` was created
- `[strong]` the task score range issue was fixed for submission

### Policy and evaluation

- `[strong]` heuristic baseline exists
- `[strong]` learned policy exists
- `[strong]` policy comparison/evaluation scripts exist
- `[strong]` the heuristic became very strong on the frozen real benchmark

### Big Round 2 conclusion

> We are not starting Round 2 from zero.
> We already have a functioning environment, benchmark, reward system, deployment, and baseline.

That is a very strong position.

---

## Part 2: Main Round 2 Objectives

Round 2 is no longer about “does the environment exist?”

Round 2 is about:

- how good the environment really is
- how realistic the reward is
- how hard the verifier is to exploit
- how much the benchmark reflects real work
- how defensible the project is technically

These are the main Round 2 objectives:

### Objective 1: Strengthen verifier realism

We should ask:

- what does the grader verify well?
- what does it miss?
- where could it allow false positives?
- where could it reject good behavior unfairly?

### Objective 2: Analyze reward hacking risk

We should ask:

- how could an agent get a high score without doing a truly good GEO audit?
- where are the loopholes?
- what shortcuts are possible?

### Objective 3: Improve task realism and diversity

We should ask:

- are the tasks too narrow?
- what GEO behaviors are not represented yet?
- what real-world failure modes are missing?

### Objective 4: Clarify transfer to real-world usefulness

We should ask:

- if an agent performs well here, what does that prove?
- what does it not prove?
- how useful is this as evaluation infrastructure for real AI systems?

### Objective 5: Prepare a stronger technical defense

We should be able to clearly explain:

- why this is an environment and not just an app
- why the reward is meaningful
- why the benchmark is useful
- what limitations we know
- what we would improve next

### Objective 6: Be ready for training-side questions

We should be able to explain:

- where OpenEnv fits
- where FastAPI fits
- where TRL, GRPO, and Unsloth fit
- why the environment is not what gets trained
- what a real training loop would look like if we add one

---

## Part 3: Detailed Round 2 Checklist

Use this section as the actual operating checklist.

### A. Verifier / Grader Review

- [ ] Re-read `server/grader.py`
- [ ] List exactly what the reward currently measures
- [ ] List what the reward does **not** measure
- [ ] Identify possible false positive scenarios
- [ ] Identify possible false negative scenarios
- [ ] Check whether the reward can be inflated by shallow pattern matching
- [ ] Check whether benchmark label agreement is being confused with full GEO quality
- [ ] Write down the current reward limitations in plain English
- [ ] Write down what makes our verifier strong today
- [ ] Write down what would make our verifier stronger in Round 2

### B. Reward Hacking Review

- [ ] Brainstorm how an agent could game the reward
- [ ] Check whether over-flagging can still produce good scores
- [ ] Check whether under-flagging can still look acceptable in some cases
- [ ] Check whether early submission could be exploited
- [ ] Check whether repeated shallow patterns can score well
- [ ] Write at least 3 specific “reward hacking” examples for our GEO environment
- [ ] Decide what current guardrails already exist
- [ ] Decide what future anti-cheat constraints should be added
- [ ] Separate “real GEO quality” from “current benchmark score” in our notes

### C. Task Realism Review

- [ ] Review what our easy tasks represent
- [ ] Review what our medium tasks represent
- [ ] Review what our hard tasks represent
- [ ] Check whether the benchmark over-represents one kind of GEO issue
- [ ] Check whether real-world messy edge cases are missing
- [ ] Check whether realistic failure modes are represented
- [ ] List which parts of GEO auditing are still outside the current environment
- [ ] List which parts of the environment are realistic enough already
- [ ] List which parts are still benchmark simplifications

### D. Diversity Review

- [ ] Check whether the 49-page benchmark is diverse enough
- [ ] Check whether websites/sources are too repetitive
- [ ] Check whether issue types are too repetitive
- [ ] Check whether query types are too repetitive
- [ ] Decide what 3-5 extra GEO task types would improve diversity
- [ ] Separate “nice-to-have diversity” from “must-have diversity”

### E. Transfer / Real-World Value Review

- [ ] Define what a high score in our environment actually means
- [ ] Define what a high score does **not** guarantee
- [ ] Explain how a third-party AI company might use this environment
- [ ] Explain how an SEO/GEO SaaS company might use this environment
- [ ] Explain what product could be built on top of this environment
- [ ] Explain what this environment cannot prove yet

### F. Agent / Training Review

- [ ] Be able to explain the difference between:
  - environment
  - agent
  - task
  - benchmark
  - reward
- [ ] Be able to explain heuristic vs learned policy
- [ ] Be able to explain what “different agents on the same environment” means
- [ ] Be able to explain where TRL, GRPO, and Unsloth fit
- [ ] Be able to explain why the environment is not what gets trained
- [ ] Be able to explain RLVR vs RLVE in our GEO context
- [ ] Be able to explain why SFT usually comes before RL

### G. Round 2 Positioning Review

- [ ] Prepare a one-sentence project description
- [ ] Prepare a one-minute technical explanation
- [ ] Prepare a one-minute non-technical explanation
- [ ] Prepare a “why this is not just another GEO app” answer
- [ ] Prepare a “what is creative/useful here?” answer
- [ ] Prepare a “what are the limitations?” answer
- [ ] Prepare a “how could this be trained with TRL later?” answer

### H. Demo and Story Review

- [ ] Prepare one clean walkthrough of a single GEO audit episode
- [ ] Prepare one benchmark summary with the `49`-page real benchmark
- [ ] Prepare one explanation of why the heuristic is strong
- [ ] Prepare one explanation of why benchmark success is not the whole real world
- [ ] Prepare one simple analogy:
  - exam system / student
  - driving test track / driver

---

## Part 4: Detailed Round 2 Rules

These are the rules we should follow in Round 2.

### Rule 1: Do not confuse the reward with the real goal

The reward is a proxy.

Always ask:

- does a higher reward truly mean better GEO auditing?
- or could the agent just be gaming the benchmark?

### Rule 2: Do not assume the current verifier is perfect

Even if the grader works, it can still be incomplete.

Always ask:

- what kinds of good behavior does it miss?
- what kinds of bad behavior does it accidentally allow?

### Rule 3: Do not optimize before trying to break the reward

Before improving training:

- try to break the reward yourself
- imagine how an agent would cheat
- look for loopholes

### Rule 4: Prefer strong hard checks over vague “looks good” judgment

When possible:

- use explicit checks
- use labeled truth
- use concrete validation

Avoid leaning too heavily on “this sounds right.”

### Rule 4A: Do not rely on one weak verifier if we can combine checks

When possible:

- combine hard checks
- combine benchmark truth
- combine anti-cheat rules
- combine final outcome with small process checks

The more independent the checks are, the harder the reward is to game.

### Rule 5: Keep the environment realistic enough to matter

The environment should not be a toy.

Always ask:

- what real-world GEO constraints are represented?
- what real-world messiness is still missing?

### Rule 6: Keep the task distribution useful

If tasks are too easy:

- they stop teaching anything useful

If tasks are too hard:

- they stop providing learning signal

So difficulty should stay meaningful.

### Rule 6A: Start simple, then scale

For any new Round 2 idea:

1. prove it in the smallest useful version
2. verify the reward
3. verify the environment
4. only then add more difficulty or diversity

### Rule 7: Diversity matters

A narrow benchmark creates narrow competence.

Always ask:

- are we training/evaluating on enough kinds of GEO problems?

### Rule 8: Explain limitations honestly

A strong Round 2 defense is not pretending the environment is perfect.

A strong defense is:

- explaining where it is strong
- explaining where it is limited
- explaining what the next improvement would be

### Rule 9: Separate infrastructure from product

Remember:

- our current project is mainly environment/evaluation infrastructure
- not yet a full user-facing GEO app

This is important for clean explanation.

### Rule 10: Always ask “what does success really prove?”

If an agent gets a high score here, what does that tell us?

And what does it not tell us?

This question is one of the most important Round 2 questions.

### Rule 11: Do not train against a reward we have not tried to break ourselves

Before any future training effort:

- brainstorm exploits
- test shallow shortcuts
- inspect suspicious high-scoring behavior
- check whether high score still means good real behavior

### Rule 12: If we add training, monitor more than one metric

Track at least:

- average reward
- component reward behavior
- false positives
- missed issues
- suspicious output patterns
- formatting compliance
- whether real task quality is rising along with reward

---

## Part 5: Strong Talking Points For Round 2

Use these to stay grounded.

### Strong point 1

We already built a valid and deployable environment server.

### Strong point 2

We already have programmatic grading and a frozen real benchmark.

### Strong point 3

We are not starting from “idea stage.”
We are now improving verifier quality, reward realism, and benchmark defensibility.

### Strong point 4

This project is useful because it turns GEO auditing into a measurable environment for agent evaluation, not just a vague content-review tool.

### Strong point 5

We already have the environment side working, so Round 2 can focus on verifier quality, reward realism, and training-readiness instead of basic setup.

---

## Part 6: Cross-Check Status Template

We can use tags like:

- `strong`
- `partial`
- `weak`
- `needs follow-up`

Example:

- verifier realism: `partial`
- reward hacking analysis: `weak`
- task diversity reasoning: `partial`
- product/use-case explanation: `strong`

This lets us track where we are actually ready and where we are not.

Suggested current starting point:

- environment infrastructure: `strong`
- OpenEnv compliance: `strong`
- deployment readiness: `strong`
- reward realism: `partial`
- verifier robustness: `partial`
- reward hacking analysis: `weak`
- task diversity defense: `partial`
- training-stack explanation: `partial`
- real-world transfer explanation: `partial`
- Round 2 storytelling: `partial`
