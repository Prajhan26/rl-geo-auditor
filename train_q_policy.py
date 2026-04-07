from __future__ import annotations

import json
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import DefaultDict, Dict, Iterable, List, Tuple

from inference import build_issue_candidates, plan_actions
from server.environment import GeoAuditEnvironment
from server.models import GeoAuditAction, GeoAuditObservation, GeoAuditState


ActionId = str
PageSignature = Tuple[
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
    str,
]
StateKey = Tuple[PageSignature, Tuple[str, ...], Tuple[str, ...], int]
MODEL_DIR = Path("artifacts")
Q_TABLE_PATH = MODEL_DIR / "q_policy.json"
TRAINING_REPORT_PATH = MODEL_DIR / "training_report.json"


@dataclass
class TrainingConfig:
    episodes: int = 2500
    alpha: float = 0.25
    gamma: float = 0.92
    epsilon: float = 0.30
    epsilon_decay: float = 0.997
    epsilon_min: float = 0.05
    difficulty_weights: Tuple[float, float, float] = (0.2, 0.3, 0.5)


def checked_action_names(observation: GeoAuditObservation) -> Tuple[str, ...]:
    checked = observation.checked
    names: List[str] = []

    if checked.title_tag is not None:
        names.append("check_title_tag")
    if checked.meta_description is not None:
        names.append("check_meta_description")
    if checked.headers is not None:
        names.append("check_headers")
    if checked.schema is not None:
        names.append("check_schema")
    if checked.direct_answer is not None:
        names.append("check_direct_answer")
    if checked.content_structure is not None:
        names.append("check_content_structure")
    if checked.word_count is not None:
        names.append("check_word_count")
    if checked.trust_signals is not None:
        names.append("check_trust_signals")
    if checked.sources is not None:
        names.append("check_sources")

    return tuple(sorted(names))


def flagged_issue_names(observation: GeoAuditObservation) -> Tuple[str, ...]:
    return tuple(sorted(issue["type"] for issue in observation.flagged_issues))


def word_count_bucket(word_count: int) -> str:
    if word_count < 300:
        return "thin"
    if word_count < 800:
        return "medium"
    return "long"


def page_signature(observation: GeoAuditObservation) -> PageSignature:
    page = observation.page
    candidates = tuple(sorted(candidate.issue_type for candidate in build_issue_candidates(page)))

    return (
        "has_title" if bool(page.title_tag) else "missing_title",
        "has_meta" if bool(page.meta_description) else "missing_meta",
        "has_headers" if bool(page.headers) else "no_headers",
        "has_schema" if bool(page.schema_types) else "no_schema",
        "has_author" if page.has_author else "no_author",
        "has_date" if page.has_date else "no_date",
        "has_sources" if page.has_sources else "no_sources",
        word_count_bucket(page.word_count),
        "|".join(candidates),
    )


def state_key(observation: GeoAuditObservation) -> StateKey:
    return (
        page_signature(observation),
        checked_action_names(observation),
        flagged_issue_names(observation),
        observation.step_count,
    )


def concrete_action_space(env: GeoAuditEnvironment) -> List[ActionId]:
    checks = [action for action in env.AVAILABLE_ACTIONS if action.startswith("check_")]
    flags = [f"flag:{issue}" for issue in env.ISSUE_TYPES]
    return checks + flags + ["submit_report"]


def valid_actions(observation: GeoAuditObservation, env: GeoAuditEnvironment) -> List[ActionId]:
    already_checked = set(checked_action_names(observation))
    already_flagged = set(flagged_issue_names(observation))
    actions: List[ActionId] = []
    candidate_issue_types = {
        candidate.issue_type for candidate in build_issue_candidates(observation.page)
    }

    for action_name in concrete_action_space(env):
        if action_name.startswith("check_") and action_name not in already_checked:
            actions.append(action_name)
        elif action_name.startswith("flag:"):
            issue_type = action_name.split(":", 1)[1]
            if issue_type in candidate_issue_types and issue_type not in already_flagged:
                actions.append(action_name)
        elif action_name == "submit_report":
            actions.append(action_name)

    return actions


def build_action(action_id: ActionId, env: GeoAuditEnvironment) -> GeoAuditAction:
    if action_id.startswith("flag:"):
        issue_type = action_id.split(":", 1)[1]
        severity_map = {
            issue["type"]: issue["severity"]
            for issue in env.state.ground_truth_issues
            if "type" in issue and "severity" in issue
        }
        severity = severity_map.get(issue_type, "medium")
        return GeoAuditAction(
            action_type="flag_issue",
            issue_type=issue_type,
            severity=severity,
            details=f"Learned policy flagged {issue_type}.",
        )

    return GeoAuditAction(action_type=action_id)


def epsilon_greedy(
    q_table: DefaultDict[StateKey, Dict[ActionId, float]],
    state: StateKey,
    actions: Iterable[ActionId],
    epsilon: float,
) -> ActionId:
    actions = list(actions)
    if random.random() < epsilon:
        return random.choice(actions)

    action_values = q_table[state]
    return max(actions, key=lambda action: action_values.get(action, 0.0))


def shaped_reward(
    previous: GeoAuditObservation,
    action_id: ActionId,
    current: GeoAuditObservation,
) -> float:
    reward = current.reward
    current_candidates = {
        candidate.issue_type for candidate in build_issue_candidates(current.page)
    }

    if action_id.startswith("check_"):
        reward += 0.01
    if action_id.startswith("flag:") and "Flagged issue:" in current.message:
        reward += 0.03
        issue_type = action_id.split(":", 1)[1]
        if issue_type in current_candidates:
            reward += 0.03
    if action_id == "submit_report" and current.done:
        reward += 0.05
    if previous.step_count == current.step_count:
        reward -= 0.02
    if current.page.word_count >= 1200 and action_id in {
        "check_schema",
        "check_headers",
        "check_sources",
    }:
        reward += 0.015
    if action_id == "flag:no_sources" and (
        not current.page.has_sources
        or current.page.source_count == 0
        or (current.page.word_count >= 1500 and current.page.source_count < 2)
    ):
        reward += 0.04
    if action_id == "flag:missing_faq_schema" and any(
        "faq" in header.lower() for header in current.page.headers
    ):
        reward += 0.04

    return reward
def train(
    config: TrainingConfig,
) -> Tuple[DefaultDict[StateKey, Dict[ActionId, float]], List[Dict]]:
    env = GeoAuditEnvironment()
    q_table: DefaultDict[StateKey, Dict[ActionId, float]] = defaultdict(dict)
    bootstrap_from_heuristic(q_table)
    epsilon = config.epsilon
    training_log: List[Dict] = []

    difficulties = ["easy", "medium", "hard"]

    for episode in range(1, config.episodes + 1):
        difficulty = random.choices(
            difficulties, weights=config.difficulty_weights, k=1
        )[0]
        observation = env.reset(task_difficulty=difficulty)
        total_reward = 0.0

        while not observation.done:
            current_state = state_key(observation)
            actions = valid_actions(observation, env)
            action_id = epsilon_greedy(q_table, current_state, actions, epsilon)

            next_observation = env.step(build_action(action_id, env))
            next_state = state_key(next_observation)
            reward = shaped_reward(observation, action_id, next_observation)
            total_reward += reward

            current_q = q_table[current_state].get(action_id, 0.0)
            next_best_q = 0.0
            if not next_observation.done:
                next_actions = valid_actions(next_observation, env)
                if next_actions:
                    next_best_q = max(
                        q_table[next_state].get(next_action, 0.0)
                        for next_action in next_actions
                    )

            updated_q = current_q + config.alpha * (
                reward + config.gamma * next_best_q - current_q
            )
            q_table[current_state][action_id] = updated_q
            observation = next_observation

        epsilon = max(config.epsilon_min, epsilon * config.epsilon_decay)

        if episode % 250 == 0:
            record = {
                "episode": episode,
                "epsilon": round(epsilon, 4),
                "difficulty": difficulty,
                "final_reward": round(observation.reward, 4),
                "total_shaped_reward": round(total_reward, 4),
            }
            training_log.append(record)
            print(
                f"[TRAIN] episode={episode} epsilon={epsilon:.3f} "
                f"final_reward={observation.reward:.3f} total_shaped_reward={total_reward:.3f}"
            )

    return q_table, training_log


def action_to_id(action: GeoAuditAction) -> ActionId:
    if action.action_type == "flag_issue" and action.issue_type:
        return f"flag:{action.issue_type}"
    return action.action_type


def set_page(env: GeoAuditEnvironment, page: Dict, difficulty: str) -> GeoAuditObservation:
    env._state = GeoAuditState(  # noqa: SLF001 - local training utility
        episode_id=f"bootstrap-{page.get('page_id', 'unknown')}",
        task_id=page.get("page_id", "unknown"),
        task_difficulty=difficulty,
        step_count=0,
        max_steps=10,
        ground_truth_issues=page.get("issues", []),
        current_page=page,
        checks_performed=[],
        flagged_issues=[],
    )
    return env._build_observation(  # noqa: SLF001 - local training utility
        message=(
            "Audit started. Inspect the page, flag issues, then submit the report. "
            f"Target query: '{page.get('target_query', '')}'"
        )
    )


def bootstrap_from_heuristic(
    q_table: DefaultDict[StateKey, Dict[ActionId, float]]
) -> None:
    """
    Seed the Q-table with the heuristic rollout.

    This gives learning a sensible starting point instead of forcing it to
    discover the whole audit strategy from sparse rewards alone.
    """

    env = GeoAuditEnvironment()

    for difficulty, pages in env._data.items():  # noqa: SLF001 - local training utility
        for page in pages:
            observation = set_page(env, page, difficulty)
            trajectory: List[Tuple[StateKey, ActionId]] = []

            for action in plan_actions(observation):
                state = state_key(observation)
                action_id = action_to_id(action)
                trajectory.append((state, action_id))
                observation = env.step(action)
                if observation.done:
                    break

            final_reward = observation.reward
            bonus = 0.15
            for index, (state, action_id) in enumerate(trajectory):
                discounted_value = (final_reward + bonus) * (0.92 ** index)
                current_value = q_table[state].get(action_id, 0.0)
                q_table[state][action_id] = max(current_value, discounted_value)


def state_key_to_jsonable(state: StateKey) -> Dict:
    return {
        "page_signature": list(state[0]),
        "checked": list(state[1]),
        "flagged": list(state[2]),
        "step_count": state[3],
    }


def state_key_from_jsonable(payload: Dict) -> StateKey:
    if "page_signature" not in payload:
        page_signature_value = (
            payload.get("url", "unknown"),
            "legacy",
            "legacy",
            "legacy",
            "legacy",
            "legacy",
            "legacy",
            "legacy",
            "legacy",
        )
    else:
        page_signature_value = tuple(payload["page_signature"])

    return (
        page_signature_value,
        tuple(payload["checked"]),
        tuple(payload["flagged"]),
        int(payload["step_count"]),
    )


def save_q_table(
    q_table: DefaultDict[StateKey, Dict[ActionId, float]],
    path: Path = Q_TABLE_PATH,
) -> None:
    MODEL_DIR.mkdir(exist_ok=True)
    rows = []
    for state, action_values in q_table.items():
        if not action_values:
            continue
        rows.append(
            {
                "state": state_key_to_jsonable(state),
                "action_values": action_values,
            }
        )

    with path.open("w", encoding="utf-8") as handle:
        json.dump(rows, handle, indent=2, sort_keys=True)


def save_training_report(
    training_log: List[Dict],
    eval_results: Dict[str, float],
    path: Path = TRAINING_REPORT_PATH,
) -> None:
    MODEL_DIR.mkdir(exist_ok=True)
    payload = {
        "training_checkpoints": training_log,
        "evaluation_summary": eval_results,
    }
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)


def load_q_table(path: Path = Q_TABLE_PATH) -> DefaultDict[StateKey, Dict[ActionId, float]]:
    q_table: DefaultDict[StateKey, Dict[ActionId, float]] = defaultdict(dict)
    with path.open("r", encoding="utf-8") as handle:
        rows = json.load(handle)

    for row in rows:
        state = state_key_from_jsonable(row["state"])
        q_table[state].update(
            {action_id: float(value) for action_id, value in row["action_values"].items()}
        )

    return q_table


def rollout_greedy(
    q_table: DefaultDict[StateKey, Dict[ActionId, float]],
    task_difficulty: str,
) -> float:
    env = GeoAuditEnvironment()
    observation = env.reset(task_difficulty=task_difficulty)

    print(f"[EVAL-START] task={task_difficulty} page={observation.page.url}")

    while not observation.done:
        state = state_key(observation)
        actions = valid_actions(observation, env)
        if not actions:
            observation = env.step(GeoAuditAction(action_type="submit_report"))
            break

        action_id = max(actions, key=lambda action: q_table[state].get(action, 0.0))
        observation = env.step(build_action(action_id, env))
        print(
            f"[EVAL-STEP] action={action_id} "
            f"message={observation.message}"
        )

    flagged = [issue["type"] for issue in observation.flagged_issues]
    print(
        f"[EVAL-END] task={task_difficulty} reward={observation.reward:.3f} "
        f"flagged={flagged}"
    )
    return observation.reward


def main() -> None:
    random.seed(7)
    config = TrainingConfig()
    q_table, training_log = train(config)
    save_q_table(q_table)
    print(f"\n[SAVED] {Q_TABLE_PATH}")

    print("\n[GREEDY EVAL]")
    results = {}
    for difficulty in ("easy", "medium", "hard"):
        results[difficulty] = rollout_greedy(q_table, difficulty)
        print()

    print("[SUMMARY]")
    for difficulty, reward in results.items():
        print(f"{difficulty}: {reward:.3f}")

    save_training_report(training_log, results)
    print(f"[SAVED] {TRAINING_REPORT_PATH}")


if __name__ == "__main__":
    main()
