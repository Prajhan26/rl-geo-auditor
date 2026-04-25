# GEO Audit Environment Self-Assessment Quiz

Answer these in your own words.
Try to answer each one in 4-10 sentences.

## Part A: Foundations

1. What is the difference between a normal script and an environment server?
The difference between the normal script and the environmental script server is normal script just involves some Python files and which I just ran to run to to build an application, but environmental servers, I'm actually building the whole environment. For an example, normal script is I just want to build an app, okay? When it comes to environment server, I am building the core fundamentals, I'm building the whole f baseline that where which any script can come and work with me. So this is what this is the difference between a normal script and any and an environmental server.


2. Why is GEO webpage auditing a real-world task and not a toy problem?
So right now I've been in a marketing agency and I have seen like people are really concerned about their pages being not optimized for A search results like whenever people people people people people people people people people people people are heavily reliant on this chat GPT and publicity nowadays to find the best results. So rather than just Googling here, they really wanted the results to be popped up in all these A LLMs. So now all the people who are building a business, who overrunning anything, they really wanted their search results to be appeared in this LLM model. So I really feel that GO website auditing it's a real world task.
3. What does one “episode” mean in this project?
Okay, one episode means here is in order to validate a task, okay. Now we have given forty nine tasks. We have given a forty nine auditing pages. So here one episode means is the script runs. I mean the script, I mean the environment runs, the environment audits. The precise word is environment audits, and if I'm sorry, I'm not sure about what it is.

4. What are the three most important parts of the RL-style loop in this project?
Okay, the three important parts of this oral style loop in this project is the agent observes. Okay. The agent, the state option, I mean the agent. S sorry, I said that agent observes and the agent audits and the agent rewards. This are the three most important parts of the oral style loop in this project.

5. Why do we need `reset()`, `step()`, and `state()` separately?
We need them separately here because reset, step and state. it's a kind of reset for a f reset in the sense like suppose a task suppose the audit has been done and it needs to be reset again right for the next thing. So reset is done and the step is kind of auditing and the state is kind of observation and rewarding. So these things has to be done separately.

## Part B: Architecture

6. What is the responsibility of `server/models.py`?
?Okay, models.py responsibility of models.py is we should run a Python script which represent like what are the models like we are planning to train this environment. So it's a kind of a model definition we are planning to do here.


7. What is the responsibility of `server/environment.py`
Okay, right now we are we are doing this environment thing, not this not just a script. So the responsibility of the environment is to make sure that like we are training the environment properly, as per they have said. Like it is not a kind of script we are running. We are training the whole oral environment loop. So the responsibility is to ensure that everything lies best in the space, like everything has been followed correctly as per the environment rules.

8. What is the responsibility of `server/grader.py`?
Okay, so grader is the one which m which which which which which which which which which which rewards okay based on the zero one pattern grader is like a type of the Python script. Which we train and we set the parameters here. So the responsibility is to check whether these parameters have been followed or not.

9. What is the responsibility of `server/app.py`?

10. Why do we have `server/api_models.py` in addition to the dataclasses/models?

## Part C: Data and Tasks

11. Why did we create easy, medium, and hard tasks?
We created easy, medium and hard task to train to train our agent in a very specialized way. Okay, so we never know that when when when when when when when when when when when someone needs a Gvo auditing, they never know whether it falls under easy, medium or hard. So we are training an agent in all the three manners. Like our agent should be able to audit everything easy, medium and hard things.

12. What is the difference between the synthetic benchmark tasks and the real reviewed benchmark?
I am not sure about the synth syn synthetic benchmark task, but I can say that real review benchmarkers mean like here we have taken a real websites right. We have not taken anything that you have provided. We have taken real bench real websites URLs so that we can train because this is going to be real world issue issue, so that we can train our model in a very real time scenario scenario scenario scenario. So that's the thing.

13. Why was freezing the benchmark at 49 pages a reasonable decision?
Actually we ran out of time and I feel like Fortnite pages is most great rather than going with a synthetic benchmark task.

14. What kinds of page signals does the agent inspect during an audit?
the pace signals vary from everything like meta, meta description, schema, markup, w whether it answered correctly, FAQs, whether it has S F FAQs, whether the answer has been given in the first hundred characters itself. Everything it was. Sorry, hundred words.

## Part D: Policy and Evaluation

15. What is the heuristic policy, and how is it different from the learned policy?
Sorry, I'm not sure about what a heuristic policy here is. I'm not sure.

16. Why did the heuristic initially perform worse on the real benchmark than we wanted?

17. What specific heuristic mistakes did we correct?
the real benchmark was like zero to one, but our heurist policies was doing like zero point zero zero something, so it is just a range issue like we were facing.

18. What does a real-benchmark score like `0.988` actually mean?
So the benchmarks code like zero point zero point nine eight h is quite do an excellent thing. So it has has to be rewarded w in which in in which parts to be.

19. Why is it useful to have `compare_policies.py`, `analyze_policies.py`, and `final_real_evaluation.py`?

## Part E: Submission and Deployment

20. Why did we need both GitHub and Hugging Face?
Okay, so Hugging Face is a deployment here. in order to judge us to evaluate in order for our server to run everywhere, not in just our local environment. We really need a hugging face. And when it comes to GitHub, it has two types of GitHub like we use. One GitHub is for my submission, which I wanted to paste them. The other GitHub is like since you've been deploying in Hugging Face, this other GitHub is a GitHub. I mean a Git repo. Git sorry, I can say it as a Git repo that's associated with the Hugging Face. So that I need to push it to the Hugging Face so that it can deploy.


21. Why did Docker matter for this project?
we we deployed in Hugging Peace, but we really need a Docker for it to run anywhere. not just in our local environment environment environment. So we containerized it into Docker so that the judges can evaluate. But still I have a doubt with this hugging face and Docker okay.

22. Why did `openenv validate` matter so much?
Okay, so this is the environment. Like we didn't go with the actual application thing. So this is an environment and validation of this open environment is must. Because it it pulls out all the dependencies from open environment so that we are training an R style looping model.

23. Why did the Hugging Face homepage show `Not Found` at first, and how did we fix it?
Okay, that's because of a root issue. Like I was confused whether I I'm supposed to use this port number, but it was an original root issue and we fixed it.

24. Why did `inference.py` need to be rewritten near the end?
infrastructure we didn't follow as per they are said that we just made it in a very d l low phase of luristic policy. So it wasn't even matchable to what they did. So we made it it incompatible with the expecting.

25. What exact submission rule caused the Phase 2 score-range failure?
because of the inference issue and because of the heuristic policies, I mean that range from zero point zero zero something. it is supposed to be zero to one. Okay, so that was the exact error that caused the problem.

26. Why was clipping the submission score into `(0,1)` the right fix?
So because as per the policy we are supposed to maintain n odd numbers like zero to one, like we you know what supposed to go with all the decimals like zero point zero zero zero something. So we need to stick with this. So this was a thing, like why was the clipping the submission error into zero one? So this was as per the guidelines.

## Part F: Reflection

27. If a judge asks “What did you actually build?”, how would you answer?
Oh that's a good question. Like if Judges ask me like what did I actually build and I would I will answer that. I I have built a GEVO. And RL style. style environment for Givo auditing. Okay. so and so we have trained an agent. We have trained which it is not an application, we have trained an agent. So that and that agent, that we have trained a agent in very much manner that it has a memory that this whenever an auditing is done by anyone, like it guides them that this us and and it scores and rewards them that this is a good Gvo I mean this page has followed best Givo benchmarks and this page hasn't followed a good Givo benchmark. So this is what we have built.

28. If a judge asks “What is the output of your environment?”, how would you answer?
So you hear the output of the environment is like our G our R L Cell Gvo auditing environment has been rewarding in terms of the benchmarks like we have mentioned. if a pay if the audit is done for a page, I mean a website, and if all the benchmarks are properly perfectly followed, our our our our our our our our our our our environment is going to rate them with the reward system. So that's the thing.

29. If a judge asks “What is creative or useful about this project?”, how would you answer?
Like right now like everyone are confused about what Givo means what SU, what's the difference between ACU and G VU. Like they really want to do it manually and even the agent don't understand nowadays and some of the subscriptions are too costly. So what if we do now agent in this style so that we don't want to worry about this Givo thing and we can rank our pages immediately in LLM so that we get clients, we get close the leads as easy as possible.

30. What do you personally feel you understand well now, and what still feels weak?
 I personally understood that it is an environment to be honest. I really understand it 100%. I really what I understood is so we are creating an environment. We are creating a fundamentals of for me is A has a memory, but agent has doesn't have a memory. So we are training an agent to act independently, okay? So every time we can't push the agent because A hallucinate, because A AI thinks in its own way, AI can make mistakes. So we are training in the real world environment with kind of 49 pages, and just saying that. And we have categorized into easy, hard, and medium. So in this way we have categorized and we are saying that and we are testing. We are actually training this A model that if all benchmarks are covered, you are supposed to give it at a much positive grade, and if all benchmarks are not covered, you are supposed to reward them in a negative way. I mean in the lowest as possible. So in this way, we are actually training our agent thing.

## Scoring Yourself

Use this rough rubric:

- `0/2` = I cannot explain it yet
- `1/2` = I partly understand it
- `2/2` = I can explain it clearly in my own words

Suggested interpretation:

- `0-20` = surface familiarity
- `21-40` = partial understanding
- `41-50` = strong practical understanding
- `51-60` = you can confidently defend the project

## How To Use This Well

Best method:

1. Read `docs/PROJECT_LEARNING_GUIDE.md`
2. Answer all 30 questions without looking
3. Re-read the guide
4. Improve your answers
5. Explain the project out loud once

That process will make the project “yours” intellectually.
