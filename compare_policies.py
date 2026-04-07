from __future__ import annotations

import random
import json
from pathlib import Path
from typing import Dict

from inference import run_episode as run_heuristic_episode
from server.environment import GeoAuditEnvironment
from train_q_policy import (
    Q_TABLE_PATH,
    load_q_table,
    rollout_greedy,
    set_page,
    state_key,
    valid_actions,
    build_action,
)

MODEL_DIR = Path("artifacts")
COMPARISON_REPORT_PATH = MODEL_DIR / "comparison_report.json"


def main() -> None:
    random.seed(7)

    if not Q_TABLE_PATH.exists():
        raise SystemExit(
            f"Missing learned policy at {Q_TABLE_PATH}. Run `python3 train_q_policy.py` first."
        )

    q_table = load_q_table()

    heuristic_scores: Dict[str, float] = {}
    learned_scores: Dict[str, float] = {}

    print("[HEURISTIC POLICY]")
    for difficulty in ("easy", "medium", "hard"):
        heuristic_scores[difficulty] = run_heuristic_episode(task_difficulty=difficulty)
        print()

    print("[LEARNED POLICY]")
    for difficulty in ("easy", "medium", "hard"):
        learned_scores[difficulty] = rollout_greedy(q_table, difficulty)
        print()

    print("[COMPARISON]")
    for difficulty in ("easy", "medium", "hard"):
        print(
            f"{difficulty}: heuristic={heuristic_scores[difficulty]:.3f} "
            f"learned={learned_scores[difficulty]:.3f}"
        )

    print("\n[FULL DATASET AVERAGE]")
    dataset_scores = evaluate_full_dataset(q_table)
    for label, score in dataset_scores.items():
        print(f"{label}: {score:.3f}")

    save_comparison_report(heuristic_scores, learned_scores, dataset_scores)
    print(f"[SAVED] {COMPARISON_REPORT_PATH}")


def evaluate_full_dataset(q_table) -> Dict[str, float]:
    env = GeoAuditEnvironment()
    results: Dict[str, float] = {}

    for difficulty, pages in env._data.items():  # noqa: SLF001 - evaluation helper
        page_rewards = []
        for page in pages:
            observation = set_page(env, page, difficulty)
            while not observation.done:
                state = state_key(observation)
                actions = valid_actions(observation, env)
                if not actions:
                    observation = env.step(build_action("submit_report", env))
                    break

                action_id = max(actions, key=lambda action: q_table[state].get(action, 0.0))
                observation = env.step(build_action(action_id, env))

            page_rewards.append(observation.reward)

        results[difficulty] = sum(page_rewards) / len(page_rewards) if page_rewards else 0.0

    all_scores = list(results.values())
    results["overall"] = sum(all_scores) / len(all_scores) if all_scores else 0.0
    return results


def save_comparison_report(
    heuristic_scores: Dict[str, float],
    learned_scores: Dict[str, float],
    dataset_scores: Dict[str, float],
) -> None:
    MODEL_DIR.mkdir(exist_ok=True)
    payload = {
        "heuristic_random_eval": heuristic_scores,
        "learned_random_eval": learned_scores,
        "learned_full_dataset_average": dataset_scores,
    }
    with COMPARISON_REPORT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
