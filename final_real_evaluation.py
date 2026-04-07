from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import DefaultDict, Dict, List

from inference import plan_actions
from server.environment import GeoAuditEnvironment
from train_q_policy import (
    Q_TABLE_PATH,
    build_action,
    load_q_table,
    set_page,
    state_key,
    valid_actions,
)


ARTIFACTS_DIR = Path("artifacts")
FINAL_REAL_DATASET_PATH = ARTIFACTS_DIR / "real_dataset_finalized_49.json"
FINAL_REAL_EVAL_REPORT_PATH = ARTIFACTS_DIR / "final_real_evaluation_report.json"


def run_heuristic_on_page(
    env: GeoAuditEnvironment, page: Dict, difficulty: str
) -> Dict[str, object]:
    observation = set_page(env, page, difficulty)

    for action in plan_actions(observation):
        observation = env.step(action)
        if observation.done:
            break

    return {
        "reward": float(observation.reward),
        "flagged_issue_types": sorted(
            issue["type"] for issue in observation.flagged_issues
        ),
    }


def run_learned_on_page(
    env: GeoAuditEnvironment,
    page: Dict,
    difficulty: str,
    q_table: DefaultDict,
) -> Dict[str, object]:
    observation = set_page(env, page, difficulty)

    while not observation.done:
        state = state_key(observation)
        actions = valid_actions(observation, env)
        if not actions:
            observation = env.step(build_action("submit_report", env))
            break

        action_id = max(actions, key=lambda action: q_table[state].get(action, 0.0))
        observation = env.step(build_action(action_id, env))

    return {
        "reward": float(observation.reward),
        "flagged_issue_types": sorted(
            issue["type"] for issue in observation.flagged_issues
        ),
    }


def summarize_policy(
    page_results: List[Dict[str, object]]
) -> Dict[str, object]:
    by_difficulty: DefaultDict[str, List[float]] = defaultdict(list)
    issue_hits: Counter[str] = Counter()

    for row in page_results:
        by_difficulty[row["difficulty"]].append(float(row["reward"]))
        issue_hits.update(row["flagged_issue_types"])

    difficulty_scores = {
        difficulty: round(sum(scores) / len(scores), 3)
        for difficulty, scores in sorted(by_difficulty.items())
    }
    all_scores = [float(row["reward"]) for row in page_results]

    return {
        "pages_evaluated": len(page_results),
        "average_reward_by_difficulty": difficulty_scores,
        "average_reward_overall": round(sum(all_scores) / len(all_scores), 3)
        if all_scores
        else 0.0,
        "top_flagged_issue_types": dict(issue_hits.most_common(10)),
    }


def load_finalized_dataset() -> List[Dict]:
    with FINAL_REAL_DATASET_PATH.open("r", encoding="utf-8") as handle:
        rows = json.load(handle)

    return [
        row
        for row in rows
        if row.get("final_status") in {"approved_clean", "approved_with_corrections"}
    ]


def main() -> None:
    if not FINAL_REAL_DATASET_PATH.exists():
        raise SystemExit(
            f"Missing finalized real dataset at {FINAL_REAL_DATASET_PATH}"
        )

    pages = load_finalized_dataset()
    env = GeoAuditEnvironment()

    heuristic_rows: List[Dict[str, object]] = []
    print("[FINAL REAL EVAL] heuristic policy")
    for page in pages:
        result = run_heuristic_on_page(env, page, page["difficulty"])
        heuristic_rows.append(
            {
                "page_id": page["page_id"],
                "difficulty": page["difficulty"],
                "url": page["url"],
                "reward": result["reward"],
                "flagged_issue_types": result["flagged_issue_types"],
                "ground_truth_issue_types": sorted(
                    issue["type"] for issue in page.get("issues", [])
                ),
            }
        )
        print(
            f"[HEURISTIC] {page['page_id']} difficulty={page['difficulty']} "
            f"reward={result['reward']:.3f}"
        )

    report: Dict[str, object] = {
        "dataset": {
            "source": str(FINAL_REAL_DATASET_PATH),
            "pages_evaluated": len(pages),
            "difficulty_counts": dict(Counter(page["difficulty"] for page in pages)),
        },
        "heuristic_policy": {
            "summary": summarize_policy(heuristic_rows),
            "page_results": heuristic_rows,
        },
    }

    if Q_TABLE_PATH.exists():
        learned_rows: List[Dict[str, object]] = []
        q_table = load_q_table()
        print("\n[FINAL REAL EVAL] learned policy")
        for page in pages:
            result = run_learned_on_page(env, page, page["difficulty"], q_table)
            learned_rows.append(
                {
                    "page_id": page["page_id"],
                    "difficulty": page["difficulty"],
                    "url": page["url"],
                    "reward": result["reward"],
                    "flagged_issue_types": result["flagged_issue_types"],
                    "ground_truth_issue_types": sorted(
                        issue["type"] for issue in page.get("issues", [])
                    ),
                }
            )
            print(
                f"[LEARNED] {page['page_id']} difficulty={page['difficulty']} "
                f"reward={result['reward']:.3f}"
            )

        report["learned_policy"] = {
            "summary": summarize_policy(learned_rows),
            "page_results": learned_rows,
        }

    ARTIFACTS_DIR.mkdir(exist_ok=True)
    with FINAL_REAL_EVAL_REPORT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)

    print(f"\n[SAVED] {FINAL_REAL_EVAL_REPORT_PATH}")


if __name__ == "__main__":
    main()
