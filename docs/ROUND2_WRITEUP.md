# GEO Audit Environment: A Verifiable Environment for GEO and AI for SEO Workflows

## Why I built this

This project came out of real frustration, not just hackathon curiosity.

Around GEO, AI search, answer engines, and AI for SEO work, I kept seeing the same pattern: serious teams were spending serious money, but the actual evaluation loop was weak. People had opinions. Agencies had decks. LLMs had recommendations. But when it came time to ask whether an agent was actually good at GEO work, there was no clean environment for testing that end to end.

I have been close to this kind of work around teams and companies like MoonPay, Ledger, Alto, and QuickNode, and the gap felt obvious. If agents are going to be trusted for GEO workflows, there needs to be something stronger than prompt demos and subjective review.

That gap is why this repo exists.

## What this project is

This repo turns GEO auditing into a task environment.

An agent:

1. receives a page and target query
2. inspects structured page signals
3. checks things like title tags, metadata, headers, schema, direct-answer quality, trust signals, and sources
4. flags issues and positives
5. submits a report
6. gets scored against benchmark truth

The environment exposes a structured loop through:

- `reset()`
- `step(action)`
- `state()`

and is available through FastAPI, Docker, and Hugging Face Spaces.

The point is not just to make GEO suggestions sound useful.

The point is to make GEO work measurable, testable, and eventually trainable.

## Why this is different from a normal SEO tool

Most SEO or GEO products help a human audit a page.

This project is built to evaluate and train agents on the workflow itself.

That difference matters.

Instead of one open-ended text box, the agent operates in a structured action space. Instead of only subjective review, the project includes verifier logic and a programmatic grader. Instead of isolated examples, it includes benchmark tasks across difficulty levels. Instead of stopping at “the output looks smart,” it creates a loop where behavior can be compared, scored, and improved.

That makes this closer to training and evaluation infrastructure than a normal content tool.

## Environment design

The current environment models a GEO webpage audit workflow with structured observations and discrete actions.

Available actions include:

- checking title tags
- checking meta descriptions
- checking headers
- checking schema
- checking direct-answer quality
- checking content structure
- checking word count
- checking trust signals
- checking sources
- flagging issues
- marking positives
- submitting the report

This makes the task more realistic than a single text-generation prompt, while still keeping it simple enough to benchmark and train against.

## Reward and verifier design

The reward is deterministic and programmatic.

The grader compares the agent's flagged issues and positive findings against benchmark truth. It uses an F1-style scoring approach and penalizes false positives. That means an agent cannot win simply by sounding plausible or flagging everything.

This is important because it moves the project toward RL with verifiable rewards:

- no learned reward model
- no vague human preference score
- no “looks good to me” evaluation loop

Instead, the reward comes from a verifier and benchmark labels.

That is one of the main technical ideas behind the project.

## What we had before Round 2

Before Round 2, the foundation was already strong:

- FastAPI environment server
- OpenEnv-style interaction loop
- Docker packaging
- Hugging Face Space deployment
- synthetic benchmark pipeline
- frozen real benchmark with reviewed pages
- heuristic baseline
- learned policy and evaluation scripts

So Round 2 was never about proving that the environment exists.

Round 2 was about proving that the environment is meaningful enough to support training and evaluation in a serious way.

## Training direction

For the training side, I used:

- TRL
- GRPO
- Unsloth
- 4-bit Qwen instruct models

The training task is currently a simplified version of the full environment loop.

Instead of training on the entire sequential `reset -> step -> submit` interaction, the current script trains a model to map structured page signals to a compact JSON issue report. That is narrower than the full environment, but it keeps the training loop verifiable and tractable.

The important point is that the reward is still tied to the GEO verifier logic, not to a learned reward model.

## The main training lesson

The biggest training lesson from this project is simple:

RL was not enough on its own.

Early GRPO attempts were not giving useful improvements because the model still had the wrong response habits. It was too easy for generation length, formatting issues, or unstable output shape to dominate the learning signal.

The key improvement was to treat supervised fine-tuning as a real warm start instead of a symbolic one.

That meant:

- tightening the output format
- forcing the model toward short JSON-only completions
- using SFT to teach response shape first
- using GRPO afterward to refine correctness under verifier reward

Once the SFT stage began to clearly reduce training loss, the training story became much healthier. That was the turning point.

## Training results

Our final training run used `Qwen2.5-7B-Instruct` with the following setup:

- restricted active issue types to 3: `thin_content`, `missing_meta_description`, `no_direct_answer`
- SFT warm start: 15 epochs on 16 easy pages, batch size 1
- GRPO: 80 steps, learning rate 3e-6, max completion length 60 tokens

**SFT warm start:**

| | Value |
|--|--|
| Loss before SFT | 3.153 |
| Loss after SFT | **0.841** |

When SFT loss stayed at 3.15, GRPO produced zero signal. Once SFT brought it to 0.84, GRPO ran with real reward variance.

**Before vs after training:**

| Metric | Before | After |
|--------|--------|-------|
| avg reward | 0.467 | 0.458 |
| false positive rate | 0.333 | **0.250** |
| parse success rate | 1.000 | 1.000 |
| avg response length (chars) | 96.2 | **56.0** |

The reward delta (-0.009) is noise on a 4-page eval split. The behavioral improvements are real: 25% fewer false positives, 42% shorter and more precise responses, perfect JSON parse rate maintained.

**GRPO signal:**
- reward min: -0.037, max: 1.000, std: 0.172
- This is a real training signal, not the flat 0.0000 loss we saw in early runs

**Heuristic baseline for reference:** avg reward = 0.964

## Verifier design: what it checks and what it does not

The grader in `server/grader.py` is a deterministic, programmatic verifier. No LLM. No learned reward model. No human-in-the-loop scoring.

**What it checks well:**

- Whether the agent flagged real issues from the benchmark label set
- Whether the agent avoided hallucinating issues that are not present
- Whether the agent found both issues and positives when both exist
- F1-style balance between precision and recall, so neither over-flagging nor under-flagging can trivially win

The core logic is:

```
reward = F1(flagged_types, truth_types) - (0.1 × false_positive_count)
```

This double-penalizes false positives: once through lower precision in the F1, and again through the explicit 0.1 multiplier. That is intentional. It means an agent cannot win by dumping every known issue type onto every page.

A clean page with no issues returns 1.0 when the agent correctly outputs nothing. This teaches the agent that restraint is sometimes the right answer.

**What it does not check:**

- It does not verify the agent's reasoning, only its labels. An agent could flag `thin_content` because word count is low, or because it randomly guessed, and get the same score either way.
- It does not score severity. Any severity attached to a correct issue type is treated equally.
- It does not measure whether the agent's audit would help a real GEO practitioner. A correct label on a borderline case counts the same as a correct label on an obvious one.
- It does not verify order of operations. The agent could skip all intermediate audit steps and jump straight to a report, and the grader would not know.

These gaps are known and intentional for this stage. The goal was to build a verifiable, reproducible reward first. Deeper semantic checking is the right next layer.

## Reward hacking analysis

A strong environment is not just well-designed. It is also stress-tested. I tried to break the reward myself before defending it.

**Hack 1: Flag nothing on every page**

If an agent always outputs `{“issues”:[]}`, it scores 1.0 on any clean page and 0.0 on any page with real issues. On a benchmark with many clean pages, this strategy can produce a deceptively high average reward without doing any real auditing.

Current guardrail: we penalize missed issues through low recall in F1. But on a benchmark skewed toward clean pages, this guardrail weakens.

**Hack 2: Flag everything every time**

If an agent flags all known issue types on every page, recall is always 1.0 but precision collapses. The double FP penalty makes this unprofitable, but only if the FP count is large. On a page with 3 real issues and 6 hallucinated ones, the agent still gets partial credit.

Current guardrail: the -0.1 FP multiplier makes this strategy lose on net. But it does not make it zero. An agent that flags 2-3 common issue types everywhere can still get a mediocre-but-non-zero score.

**Hack 3: Memorize benchmark label priors**

If certain issue types appear frequently in the benchmark (e.g., `no_sources` in 30 out of 60 pages), an agent could learn to always flag those types and score well on average without inspecting the page signals at all.

Current guardrail: the held-out eval split limits this during training. But the benchmark is not adversarially constructed, so this risk is real.

**Hack 4: Exploit the clean-page shortcut**

The grader returns 1.0 for any page where both ground truth and flagged issues are empty. An agent that learns the pattern “if the page looks clean, output nothing” could exploit this on ambiguous pages.

Current guardrail: the benchmark includes pages at all difficulty levels. But this is still a soft guardrail.

**What makes the reward hard to game in practice:**

The double FP penalty, the F1 structure, and the held-out benchmark together make it difficult to win with any single shallow strategy. No strategy dominates: under-flagging loses recall, over-flagging loses precision plus the explicit penalty, and memorization is limited by the held-out split.

**What would make it harder to game:**

- Rotating or hidden eval splits
- Adversarially constructed pages that share surface signals with clean pages but have hidden issues
- Process-level checks that verify the agent used intermediate audit steps before submitting
- Per-issue confidence scoring rather than binary present/absent matching

These are the right next steps for a more robust verifier.

## What this project demonstrates

I think the strongest claim here is not:

“we trained the best GEO model.”

The strongest claim is:

“we built a verifiable environment where GEO agent behavior can be tested, benchmarked, and trained against deterministic reward.”

That is a stronger and more defensible contribution.

It means this project can be used to ask better questions:

- can an agent perform a GEO audit workflow?
- can two agent strategies be compared fairly?
- can behavior improve under a verifier-driven reward loop?
- what shortcuts or reward hacks should be defended against?

## Reward hacking risk

I do not think it is enough to say “the reward is deterministic” and stop there.

Any verifier-driven environment can still be gamed if the benchmark is narrow or the reward is too easy to satisfy with shallow patterns.

In this project, the current reward is strongest at measuring:

- issue-label agreement
- false-positive control
- basic report correctness under a fixed issue taxonomy

It is weaker at measuring:

- deeper content usefulness
- real ranking or traffic lift
- nuanced human judgment
- long-term GEO performance

That means there are still reward-hacking risks.

An agent could try to:

- memorize common issue priors from the benchmark instead of auditing robustly
- overfit to shallow page cues like missing metadata or low word count
- under-flag to avoid false-positive penalties
- learn benchmark-specific label patterns without learning broader GEO reasoning

We already have some guardrails:

- a fixed issue taxonomy
- deterministic grading
- explicit false-positive penalties
- held-out evaluation
- a real-page benchmark alongside synthetic tasks

But I would not claim the reward is impossible to game.

The honest claim is narrower: the environment already puts useful pressure against naive hallucination, but it still needs stronger defenses against shallow benchmark overfitting.

Future improvements here are clear:

- more diverse benchmark pages
- more adversarial evaluation cases
- hidden or rotating evaluation splits
- richer verifier checks
- stronger separation between benchmark agreement and full GEO quality

I think being explicit about this makes the project stronger, not weaker.

## Current limitations

There are still real limitations.

The current reward is meaningful, but it is still a proxy for full GEO quality, not a perfect measure of real-world search performance. The benchmark is useful, but it is still smaller and cleaner than the full web. The current training setup simplifies the full environment into a narrower structured-output problem. And the heuristic baseline remains very strong, which is both a strength and a challenge.

Those are not reasons to dismiss the project. They are exactly the reasons this kind of environment is worth building further.

## Why I think this matters

If AI for SEO and GEO tooling is going to become trustworthy, it needs stronger evaluation infrastructure.

Right now, too much of the space still relies on:

- vibes
- screenshots
- prompt demos
- subjective judgments

That is not enough when real budgets and real distribution decisions are involved.

This project is my attempt to push that in a better direction.

Instead of only generating advice, it creates an environment where the advice-producing agent can be evaluated, compared, and improved.

That is the deeper point of the work.

## Closing

The GEO Audit Environment is best understood as evaluation and training infrastructure for GEO workflows.

It is not just a checker. It is not just a prompt wrapper. It is an attempt to make GEO work behave more like a real task world with actions, rewards, benchmarks, and measurable agent behavior.

That is the contribution I care about most in this project.
