from typing import Dict, List


def _f1_like_score(predicted_types: set[str], truth_types: set[str]) -> float:
    if not truth_types and not predicted_types:
        return 1.0

    true_positives = len(predicted_types & truth_types)
    false_positives = len(predicted_types - truth_types)
    false_negatives = len(truth_types - predicted_types)

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
        return 0.0
    return 2 * (precision * recall) / (precision + recall)


def calculate_reward(
    flagged: List[Dict],
    ground_truth: List[Dict],
    marked_positives: List[Dict] | None = None,
    ground_truth_positives: List[Dict] | None = None,
) -> float:
    """
    Score the final report using F1, then penalize hallucinated issues.

    This teaches the agent two things:
    1. Find real GEO issues.
    2. Avoid inventing issues that are not actually there.
    """

    flagged_types = {issue["type"] for issue in flagged}
    truth_types = {issue["type"] for issue in ground_truth}
    positive_types = {item["type"] for item in (marked_positives or [])}
    truth_positive_types = {item["type"] for item in (ground_truth_positives or [])}

    # A clean page that receives an empty report should count as a perfect audit.
    if not truth_types and not flagged_types:
        if not truth_positive_types and not positive_types:
            return 1.0

    false_positives = len(flagged_types - truth_types)
    issue_score = _f1_like_score(flagged_types, truth_types)
    reward = issue_score - (false_positives * 0.1)

    has_positive_eval = bool(truth_positive_types or positive_types)
    if has_positive_eval:
        positive_score = _f1_like_score(positive_types, truth_positive_types)
        reward = (0.85 * reward) + (0.15 * positive_score)

    return max(0.0, min(1.0, reward))
