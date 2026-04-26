# I turned GEO auditing into an RL environment. Here is what actually happened.

The frustration came first.

I had been close to GEO work with companies like MoonPay, Ledger, Alto, and QuickNode. The pattern was always the same: real budget going out the door, real content being produced, real agency hours being billed. But when I asked how they knew whether the GEO work was actually helping, the answer was always some version of "it feels like it is."

That is not an answer. That is hope.

Gartner projects traditional search volume will drop 25% by 2026 as AI chatbots take over query traffic. The market for GEO services is growing from $886 million today to $7.3 billion by 2031. 94% of digital marketing leaders plan to increase GEO spend next year. The money is real. The measurement is not.

![GEO is real spend — with no standard way to measure results](../artifacts/geo_market_problem.png)
*GEO services market: $886M (2024) to $7.3B (2031) at 34% CAGR. Sources: Valuates Reports, eMarketer, Incremys, Gartner (2025).*

Most tools in this space let a human read AI output and decide what to do. That is not evaluation. That is a text box with extra steps.

So I built the environment instead.

## What the environment actually does

The GEO Audit Environment turns page auditing into a scored task. An agent gets a webpage and a target query. It inspects structured signals: meta description, headers, word count, sources, schema. It flags what it finds wrong. It submits a report. A deterministic verifier scores it against labeled ground truth.

No human judge. No "does this sound good?" The scoring is programmatic.

The rule: find real problems, get credit. Invent problems that are not there, lose credit twice over. A clean page that receives an empty report scores 1.0. Knowing when to say nothing is part of the task.

The environment is live. You can run a full audit episode right now:

```bash
# Start an episode — get a real page with structured signals
curl -X POST https://samunhashed-geo-audit-env.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task_difficulty": "easy"}'

# Flag an issue
curl -X POST https://samunhashed-geo-audit-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{"action_type": "flag_issue", "issue_type": "thin_content", "severity": "medium"}'

# Submit and receive your score
curl -X POST https://samunhashed-geo-audit-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{"action_type": "submit_report"}'
```

That loop, exposed as an API, is what makes this trainable. An agent that can be scored can be improved.

## The clearest way to see what training did

Take a page with two real issues: thin content and a missing meta description. Show the same model on the same page before and after training.

**Before training**, the untrained 7B model outputs:
```json
{"issues":[{"type":"thin_content"},{"type":"no_direct_answer"},{"type":"missing_schema"}]}
```
It found one real issue. It invented two that are not there. Reward: 0.133.

**After training**, the same model outputs:
```json
{"issues":[{"type":"thin_content"}]}
```
One issue. The one that is actually there. Nothing invented. Reward: 0.5.

The model did not get smarter about GEO. It got more honest about what it actually knows.

## The training story, including the part that went wrong

I ran supervised fine-tuning first, then GRPO (a reinforcement learning method) on Qwen2.5-7B-Instruct.

The thing I did not expect: reinforcement learning produces zero signal until supervised training teaches the output format first. When the model's supervised loss was still at 3.15, every single RL reward call came back 0.000. Not low. Zero. The model could not produce a readable output, so there was nothing for the reward function to score.

Once supervised training ran long enough to push loss down to 0.841, the RL phase started working. The model began producing real variance across its guesses. It was actually learning from the scores the environment was giving it.

After the full training run, the false positive rate fell from 0.333 to 0.250 (25% fewer invented issues). Average response length dropped from 96 characters to 56 (42% more concise). The reward delta across four eval pages was -0.009, which is statistical noise. What changed was behavior, not the headline number.

![Behavioral improvements after SFT + GRPO training](../artifacts/round2_behavioral.png)

## The honest numbers

The heuristic baseline scores 0.964 on synthetic tasks. The trained model scores 0.458. I am not going to pretend that gap is not there.

![Reward comparison: heuristic vs LLM before and after training](../artifacts/round2_comparison.png)

What I care about is that the environment made this outcome visible instead of hiding it. Most GEO tooling cannot tell you whether the model it is running is accurate or just confident-sounding. This one can.

On the real benchmark, which covers 49 pages collected from the live web and labeled by hand, the heuristic scores 0.571 and the learned model scores 0.460. The gap narrows on real pages because real pages are harder and noisier. That is what makes them a useful proof set: a benchmark that is too easy to pass is not a benchmark.

## What this actually changes

If you run a GEO tool today, you get a report. You read it. You decide whether the advice seems right. You act on it or you do not. At no point does the tool know whether it was correct.

This environment breaks that pattern. An agent that goes through this loop can be scored, compared against other agents, and trained to score better. The feedback is deterministic. The loop is open. Anyone can run it.

GEO work is guesswork until you can measure it.

**Live environment:** [samunhashed-geo-audit-env.hf.space](https://samunhashed-geo-audit-env.hf.space)  
**API docs:** [samunhashed-geo-audit-env.hf.space/docs](https://samunhashed-geo-audit-env.hf.space/docs)  
**Code and benchmark data:** [huggingface.co/spaces/Samunhashed/geo-audit-env](https://huggingface.co/spaces/Samunhashed/geo-audit-env)
