from typing import Dict, List


def calculate_reward(flagged: List[Dict], ground_truth: List[Dict]) -> float:
    """
    Score the final report using F1, then penalize hallucinated issues.

    This teaches the agent two things:
    1. Find real GEO issues.
    2. Avoid inventing issues that are not actually there.
    """

    flagged_types = {issue["type"] for issue in flagged}
    truth_types = {issue["type"] for issue in ground_truth}

    # A clean page that receives an empty report should count as a perfect audit.
    if not truth_types and not flagged_types:
        return 1.0

    true_positives = len(flagged_types & truth_types)
    false_positives = len(flagged_types - truth_types)
    false_negatives = len(truth_types - flagged_types)

    precision = (
        true_positives / (true_positives + false_positives)
        if true_positives + false_positives
        else 0.0
    )
    recall = (
        true_positives / (true_positives + false_negatives)
        if true_positives + false_negatives
        else 0.0
    )

    if precision + recall == 0:
        f1_score = 0.0
    else:
        f1_score = 2 * (precision * recall) / (precision + recall)

    reward = f1_score - (false_positives * 0.1)
    return max(0.0, min(1.0, reward))
