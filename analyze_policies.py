from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

from inference import plan_actions
from server.environment import GeoAuditEnvironment
from server.models import GeoAuditAction, GeoAuditObservation
from train_q_policy import (
    Q_TABLE_PATH,
    build_action,
    load_q_table,
    set_page,
    state_key,
    valid_actions,
)


ARTIFACTS_DIR = Path("artifacts")
ANALYSIS_REPORT_PATH = ARTIFACTS_DIR / "policy_analysis.json"


def issue_types(items: List[Dict]) -> List[str]:
    return sorted(item["type"] for item in items)


def compare_flags(flagged: List[str], truth: List[str]) -> Dict[str, List[str]]:
    flagged_set = set(flagged)
    truth_set = set(truth)
    return {
        "correct": sorted(flagged_set & truth_set),
        "missed": sorted(truth_set - flagged_set),
        "extra": sorted(flagged_set - truth_set),
    }


def rollout_heuristic(env: GeoAuditEnvironment, observation: GeoAuditObservation) -> GeoAuditObservation:
    for action in plan_actions(observation):
        observation = env.step(action)
        if observation.done:
            break
    return observation


def rollout_learned(env: GeoAuditEnvironment, observation: GeoAuditObservation, q_table) -> GeoAuditObservation:
    while not observation.done:
        state = state_key(observation)
        actions = valid_actions(observation, env)
        if not actions:
            observation = env.step(GeoAuditAction(action_type="submit_report"))
            break

        action_id = max(actions, key=lambda action: q_table[state].get(action, 0.0))
        observation = env.step(build_action(action_id, env))
    return observation


def analyze() -> Dict:
    if not Q_TABLE_PATH.exists():
        raise SystemExit(
            f"Missing learned policy at {Q_TABLE_PATH}. Run `python3 train_q_policy.py` first."
        )

    q_table = load_q_table()
    env = GeoAuditEnvironment()
    report: Dict[str, List[Dict]] = {}

    for difficulty, pages in env._data.items():  # noqa: SLF001 - analysis helper
        page_reports: List[Dict] = []
        for page in pages:
            heuristic_obs = set_page(env, page, difficulty)
            heuristic_final = rollout_heuristic(env, heuristic_obs)

            learned_obs = set_page(env, page, difficulty)
            learned_final = rollout_learned(env, learned_obs, q_table)

            truth = issue_types(page.get("issues", []))
            heuristic_flags = issue_types(heuristic_final.flagged_issues)
            learned_flags = issue_types(learned_final.flagged_issues)

            page_reports.append(
                {
                    "page_id": page["page_id"],
                    "url": page["url"],
                    "truth": truth,
                    "heuristic": {
                        "reward": round(heuristic_final.reward, 4),
                        "flagged": heuristic_flags,
                        "comparison": compare_flags(heuristic_flags, truth),
                    },
                    "learned": {
                        "reward": round(learned_final.reward, 4),
                        "flagged": learned_flags,
                        "comparison": compare_flags(learned_flags, truth),
                    },
                }
            )

        report[difficulty] = page_reports

    return report


def save_report(report: Dict) -> None:
    ARTIFACTS_DIR.mkdir(exist_ok=True)
    with ANALYSIS_REPORT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)


def print_summary(report: Dict) -> None:
    for difficulty, rows in report.items():
        print(f"[{difficulty.upper()}]")
        for row in rows:
            learned = row["learned"]
            missed = learned["comparison"]["missed"]
            extra = learned["comparison"]["extra"]
            if missed or extra:
                print(
                    f"{row['page_id']}: reward={learned['reward']:.3f} "
                    f"missed={missed} extra={extra}"
                )


def main() -> None:
    report = analyze()
    save_report(report)
    print_summary(report)
    print(f"[SAVED] {ANALYSIS_REPORT_PATH}")


if __name__ == "__main__":
    main()
