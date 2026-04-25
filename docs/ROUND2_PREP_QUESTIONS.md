# Round 2 Preparation Questions

Use this file as a Round 2 cross-check list.

The goal is not just to explain what we built, but to defend:

- why the environment is meaningful
- where the reward is strong or weak
- how realistic the benchmark is
- where agents could exploit the setup
- what we would improve next

## Section 1: Core Round 2 Framing

1. What does our environment actually measure well?

2. What does our environment not measure well yet?

3. Why is GEO auditing a useful task for evaluating agents?

4. Why is our project more than “just another GEO auditing app”?

5. If an agent scores well in our environment, what does that mean in the real world?

6. If an agent scores well in our environment, what does it still NOT guarantee?

## Section 2: Reward Design

7. What is our reward function trying to encourage?

8. What kinds of bad behavior is our reward function trying to punish?

9. In what ways could the reward still be incomplete?

10. What would reward hacking look like in our GEO environment?

11. Could an agent over-flag issues just to chase reward?

12. Could an agent under-flag issues and still look good in some cases?

13. Why is reward design hard in environments like this?

14. Why is reward not the same thing as the real goal?

## Section 3: Verifier and Grader Quality

15. What makes our grader/verifier stronger than a vague human impression?

16. What makes our grader still weaker than the full real-world task?

17. What kinds of false positives could our grader allow?

18. What kinds of false negatives could our grader produce?

19. Why is “just use an LLM as judge” risky?

20. Why is our current grader more verifiable than a pure LLM judge?

21. If we wanted to make the verifier stronger, what would we improve first?

## Section 4: Environment Realism

22. In what sense is our environment realistic?

23. In what sense is our environment still a simplified abstraction?

24. What real-world GEO factors are missing from our current environment?

25. Does our environment capture messy real-world failure modes well enough?

26. What would make the environment feel less toy-like in Round 2?

27. If a judge says “this is too benchmark-like and not real enough,” how would we respond?

## Section 5: Task Diversity and Curriculum

28. Why did we create easy, medium, and hard tasks?

29. Is our easy/medium/hard structure closer to a benchmark split or true curriculum learning?

30. What is the difference between static task difficulty and adaptive task difficulty?

31. Is our current environment diverse enough?

32. Where might task diversity still be weak?

33. What kinds of additional GEO task types could strengthen the benchmark?

34. If an agent only performs well on our current 49 pages, what is the limitation of that?

## Section 6: Agents and Generalization

35. What does it mean that different agents can be tested in the same environment?

36. Why is that valuable?

37. What kinds of agents could be run on our environment?

38. Why is the environment separate from the agent?

39. How does our environment support evaluation better than a one-off script?

40. What is the difference between evaluating an agent and training an agent?

## Section 7: RL, RLHF, RLVR, and RLVE

41. How is our project related to RLHF?

42. How is our project related to RLVR?

43. How is our project related to RLVE?

44. Is our environment closer to RLVR or RLVE, and why?

45. How would TRL, GRPO, and Unsloth fit around our project if we trained more seriously?

46. Why would SFT or a warm start still matter before RL?

## Section 8: Weaknesses and Defensibility

47. What is the weakest part of our current environment design?

48. What is the weakest part of our benchmark?

49. What is the weakest part of our reward design?

50. What is the weakest part of our current submission story?

51. If a strong judge tries to poke holes in the project, what are the top 5 critiques they might raise?

52. Which of those critiques can we defend well?

53. Which of those critiques should we admit honestly?

54. How do we talk honestly about limitations without weakening the project too much?

## Section 9: Round 2 Improvement Thinking

55. If we had one extra day, what would be the highest-value improvement?

56. If we had one extra week, what would be the highest-value improvement?

57. Would it be better to improve reward quality, task diversity, or verifier realism first?

58. What changes would make our benchmark more generalizable?

59. What changes would make our environment harder to game?

60. What changes would make the project more valuable to a third-party user or company?

## Section 10: Final Defense Questions

61. What is the single strongest thing about our project?

62. What is the single biggest limitation of our project?

63. Why should anyone care about a GEO environment server?

64. Why is environment-building valuable even if it is not yet a full end-user product?

65. If you had to defend this project in one minute to a technical judge, what would you say?

66. If you had to defend this project in one minute to a non-technical founder, what would you say?

67. If you had to describe this project as infrastructure instead of an app, how would you say it?

68. What does success in Round 2 actually look like for us?

## Suggested Use

Best workflow:

1. Answer these gradually.
2. Mark the ones you can answer confidently.
3. Mark the ones that still feel vague.
4. Revisit weak ones after discussion.

You can add tags next to each:

- `strong`
- `partial`
- `weak`
- `needs follow-up`
