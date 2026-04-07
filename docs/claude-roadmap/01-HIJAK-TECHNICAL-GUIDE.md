# GEO Audit Environment - Technical Guide for Hijak

## What We're Building

An OpenEnv RL environment that trains AI to audit webpages for GEO (Generative Engine Optimization) issues.

```
INPUT:  Webpage + Target Query
OUTPUT: AI learns to find REAL issues that hurt AI Search visibility
REWARD: Based on accuracy (found real issues, didn't hallucinate)
```

---

## Tech Stack

- **Python 3.11+**
- **OpenEnv Core** (Meta's RL framework)
- **FastAPI** (server)
- **Docker** (containerization)
- **Hugging Face Spaces** (deployment)

---

## Project Structure

```
geo-audit-env/
├── server/
│   ├── __init__.py
│   ├── app.py              # FastAPI server
│   ├── environment.py      # Main RL logic
│   ├── grader.py           # Reward calculation
│   └── models.py           # Pydantic models
├── data/
│   ├── task1_easy.json     # 20 obvious-issue pages
│   ├── task2_medium.json   # 20 subtle-issue pages
│   └── task3_hard.json     # 20 competitive pages
├── inference.py            # REQUIRED - runs AI against env
├── Dockerfile              # Container config
├── openenv.yaml            # Environment metadata
├── pyproject.toml          # Dependencies
└── README.md               # Documentation
```

---

## Step 1: Project Setup

```bash
# Create project folder
cd ~
mkdir geo-audit-env
cd geo-audit-env

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install OpenEnv
pip install openenv-core

# Initialize (creates scaffolding)
openenv init geo_audit

# Create additional folders
mkdir -p data
mkdir -p server
```

---

## Step 2: models.py

Create `server/models.py`:

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from openenv.core.env_server import Action, Observation, State


@dataclass
class GeoAuditAction(Action):
    """Actions the AI can take."""
    action_type: str  # "check_*", "flag_issue", "submit_report"
    
    # For check actions
    target: Optional[str] = None
    
    # For flag_issue action
    issue_type: Optional[str] = None
    severity: Optional[str] = None  # critical, high, medium, low
    details: Optional[str] = None


@dataclass
class PageData:
    """Raw page data."""
    url: str = ""
    target_query: str = ""
    title_tag: str = ""
    meta_description: str = ""
    h1: str = ""
    first_paragraph: str = ""
    word_count: int = 0
    headers: List[str] = field(default_factory=list)
    schema_types: List[str] = field(default_factory=list)
    has_author: bool = False
    has_date: bool = False


@dataclass
class CheckResults:
    """Results of AI's checks."""
    title_tag: Optional[Dict] = None
    meta_description: Optional[Dict] = None
    headers: Optional[Dict] = None
    schema: Optional[Dict] = None
    direct_answer: Optional[Dict] = None
    content_structure: Optional[Dict] = None
    word_count: Optional[Dict] = None
    trust_signals: Optional[Dict] = None


@dataclass
class GeoAuditObservation(Observation):
    """What AI sees after each action."""
    # Page info
    page: PageData = field(default_factory=PageData)
    
    # Analysis results (fills in as AI checks)
    checked: CheckResults = field(default_factory=CheckResults)
    
    # AI's findings
    flagged_issues: List[Dict] = field(default_factory=list)
    
    # Episode state
    step_count: int = 0
    max_steps: int = 10
    available_actions: List[str] = field(default_factory=list)
    
    # Feedback
    message: str = ""
    done: bool = False
    reward: float = 0.0


@dataclass
class GeoAuditState(State):
    """Internal state (hidden from AI)."""
    episode_id: str = ""
    task_id: str = ""
    task_difficulty: str = ""
    step_count: int = 0
    max_steps: int = 10
    
    # Ground truth
    ground_truth_issues: List[Dict] = field(default_factory=list)
    
    # Current page data
    current_page: Dict = field(default_factory=dict)
    
    # What AI has done
    checks_performed: List[str] = field(default_factory=list)
    flagged_issues: List[Dict] = field(default_factory=list)
```

---

## Step 3: environment.py

Create `server/environment.py`:

```python
import uuid
import json
import random
from pathlib import Path
from openenv.core.env_server import Environment
from .models import (
    GeoAuditAction, 
    GeoAuditObservation, 
    GeoAuditState,
    PageData,
    CheckResults
)
from .grader import calculate_reward


class GeoAuditEnvironment(Environment):
    
    AVAILABLE_ACTIONS = [
        "check_title_tag",
        "check_meta_description",
        "check_headers",
        "check_schema",
        "check_direct_answer",
        "check_content_structure",
        "check_word_count",
        "check_trust_signals",
        "flag_issue",
        "submit_report"
    ]
    
    ISSUE_TYPES = [
        "missing_title_tag",
        "weak_title_tag",
        "missing_meta_description",
        "weak_meta_description",
        "no_direct_answer",
        "buried_answer",
        "missing_faq_schema",
        "missing_howto_schema",
        "missing_article_schema",
        "no_headers",
        "poor_header_structure",
        "thin_content",
        "no_author",
        "no_date",
        "no_sources"
    ]
    
    def __init__(self):
        super().__init__()
        self._state = GeoAuditState()
        self._data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load task datasets."""
        data_dir = Path(__file__).parent.parent / "data"
        return {
            "easy": self._load_json(data_dir / "task1_easy.json"),
            "medium": self._load_json(data_dir / "task2_medium.json"),
            "hard": self._load_json(data_dir / "task3_hard.json"),
        }
    
    def _load_json(self, path: Path) -> List:
        """Load JSON file safely."""
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return []
    
    def reset(self, task_difficulty: str = "easy") -> GeoAuditObservation:
        """Start new audit episode."""
        
        # Get pages for this difficulty
        pages = self._data.get(task_difficulty, [])
        
        # Use dummy if no data
        if not pages:
            page = self._get_dummy_page()
        else:
            page = random.choice(pages)
        
        # Initialize state
        self._state = GeoAuditState(
            episode_id=str(uuid.uuid4()),
            task_id=page.get("page_id", "unknown"),
            task_difficulty=task_difficulty,
            step_count=0,
            max_steps=10,
            ground_truth_issues=page.get("issues", []),
            current_page=page,
            checks_performed=[],
            flagged_issues=[],
        )
        
        return self._build_observation(
            message=f"Audit started. Analyze this page for GEO issues. "
                    f"Target query: '{page.get('target_query', '')}'"
        )
    
    def step(self, action: GeoAuditAction) -> GeoAuditObservation:
        """Process one action."""
        self._state.step_count += 1
        
        # Check max steps
        if self._state.step_count >= self._state.max_steps:
            return self._finalize("Max steps reached. Auto-submitting.")
        
        # Route action
        if action.action_type.startswith("check_"):
            return self._handle_check(action)
        elif action.action_type == "flag_issue":
            return self._handle_flag(action)
        elif action.action_type == "submit_report":
            return self._finalize("Report submitted.")
        else:
            return self._build_observation(
                message=f"Unknown action: {action.action_type}"
            )
    
    def _handle_check(self, action: GeoAuditAction) -> GeoAuditObservation:
        """Handle check_* actions."""
        check_type = action.action_type.replace("check_", "")
        
        if action.action_type in self._state.checks_performed:
            return self._build_observation(
                message=f"Already checked: {check_type}"
            )
        
        self._state.checks_performed.append(action.action_type)
        
        # Get analysis result
        result = self._analyze(check_type)
        
        return self._build_observation(
            message=f"Checked {check_type}: {result}"
        )
    
    def _analyze(self, check_type: str) -> str:
        """Analyze a page element."""
        page = self._state.current_page
        
        if check_type == "title_tag":
            title = page.get("title_tag", "")
            if not title:
                return "NO TITLE TAG FOUND"
            return f"Title: '{title}' ({len(title)} chars)"
        
        elif check_type == "meta_description":
            meta = page.get("meta_description", "")
            if not meta:
                return "NO META DESCRIPTION FOUND"
            return f"Meta: '{meta[:100]}...' ({len(meta)} chars)"
        
        elif check_type == "headers":
            headers = page.get("headers", [])
            h1 = page.get("h1", "")
            return f"H1: '{h1}', Other headers: {headers}"
        
        elif check_type == "schema":
            schemas = page.get("schema_types", [])
            if not schemas:
                return "NO SCHEMA MARKUP FOUND"
            return f"Schema types: {schemas}"
        
        elif check_type == "direct_answer":
            first_p = page.get("first_paragraph", "")
            query = page.get("target_query", "")
            return f"First paragraph: '{first_p[:150]}...' Query: '{query}'"
        
        elif check_type == "content_structure":
            headers = page.get("headers", [])
            word_count = page.get("word_count", 0)
            return f"Headers: {len(headers)}, Words: {word_count}"
        
        elif check_type == "word_count":
            count = page.get("word_count", 0)
            if count < 300:
                return f"THIN CONTENT: {count} words"
            elif count < 500:
                return f"Light content: {count} words"
            return f"Good length: {count} words"
        
        elif check_type == "trust_signals":
            author = page.get("has_author", False)
            date = page.get("has_date", False)
            return f"Author: {author}, Date: {date}"
        
        return "Unknown check type"
    
    def _handle_flag(self, action: GeoAuditAction) -> GeoAuditObservation:
        """Handle flag_issue action."""
        if not action.issue_type:
            return self._build_observation(
                message="flag_issue requires issue_type"
            )
        
        if action.issue_type not in self.ISSUE_TYPES:
            return self._build_observation(
                message=f"Unknown issue type: {action.issue_type}. "
                        f"Valid types: {self.ISSUE_TYPES}"
            )
        
        issue = {
            "type": action.issue_type,
            "severity": action.severity or "medium",
            "details": action.details or ""
        }
        
        self._state.flagged_issues.append(issue)
        
        return self._build_observation(
            message=f"Flagged: {action.issue_type} ({action.severity})"
        )
    
    def _finalize(self, message: str) -> GeoAuditObservation:
        """Calculate reward and end episode."""
        reward = calculate_reward(
            flagged=self._state.flagged_issues,
            ground_truth=self._state.ground_truth_issues
        )
        
        return self._build_observation(
            message=message,
            done=True,
            reward=reward
        )
    
    def _build_observation(
        self,
        message: str = "",
        done: bool = False,
        reward: float = 0.0
    ) -> GeoAuditObservation:
        """Build observation from state."""
        page = self._state.current_page
        
        return GeoAuditObservation(
            page=PageData(
                url=page.get("url", ""),
                target_query=page.get("target_query", ""),
                title_tag=page.get("title_tag", ""),
                meta_description=page.get("meta_description", ""),
                h1=page.get("h1", ""),
                first_paragraph=page.get("first_paragraph", ""),
                word_count=page.get("word_count", 0),
                headers=page.get("headers", []),
                schema_types=page.get("schema_types", []),
                has_author=page.get("has_author", False),
                has_date=page.get("has_date", False),
            ),
            checked=self._build_check_results(),
            flagged_issues=self._state.flagged_issues,
            step_count=self._state.step_count,
            max_steps=self._state.max_steps,
            available_actions=self.AVAILABLE_ACTIONS,
            message=message,
            done=done,
            reward=reward,
        )
    
    def _build_check_results(self) -> CheckResults:
        """Build check results from performed checks."""
        results = CheckResults()
        page = self._state.current_page
        
        for check in self._state.checks_performed:
            check_type = check.replace("check_", "")
            
            if check_type == "title_tag":
                results.title_tag = {
                    "present": bool(page.get("title_tag")),
                    "value": page.get("title_tag", ""),
                    "length": len(page.get("title_tag", ""))
                }
            elif check_type == "meta_description":
                results.meta_description = {
                    "present": bool(page.get("meta_description")),
                    "value": page.get("meta_description", ""),
                    "length": len(page.get("meta_description", ""))
                }
            # Add more as needed
        
        return results
    
    def _get_dummy_page(self) -> Dict:
        """Return dummy page for testing."""
        return {
            "page_id": "dummy_001",
            "url": "https://example.com/test-page",
            "target_query": "how to test something",
            "title_tag": "Test Page | Example",
            "meta_description": "",
            "h1": "Welcome to Our Site",
            "first_paragraph": "We are a company that does things. Our mission is to help people. Contact us for more information about our services.",
            "word_count": 280,
            "headers": ["H2: About Us", "H2: Contact"],
            "schema_types": [],
            "has_author": False,
            "has_date": False,
            "issues": [
                {"type": "missing_meta_description", "severity": "critical"},
                {"type": "no_direct_answer", "severity": "critical"},
                {"type": "thin_content", "severity": "medium"},
            ]
        }
    
    @property
    def state(self) -> GeoAuditState:
        return self._state
```

---

## Step 4: grader.py

Create `server/grader.py`:

```python
from typing import List, Dict


def calculate_reward(
    flagged: List[Dict],
    ground_truth: List[Dict]
) -> float:
    """
    Calculate reward based on audit accuracy.
    
    Uses F1 score with hallucination penalty.
    Returns value between 0.0 and 1.0.
    """
    
    # Extract issue types
    flagged_types = {issue["type"] for issue in flagged}
    truth_types = {issue["type"] for issue in ground_truth}
    
    # Calculate metrics
    true_positives = len(flagged_types & truth_types)
    false_positives = len(flagged_types - truth_types)  # Hallucinations
    false_negatives = len(truth_types - flagged_types)  # Missed
    
    # Precision: Of flagged issues, how many were real?
    if true_positives + false_positives > 0:
        precision = true_positives / (true_positives + false_positives)
    else:
        precision = 0.0
    
    # Recall: Of real issues, how many did AI find?
    if true_positives + false_negatives > 0:
        recall = true_positives / (true_positives + false_negatives)
    else:
        recall = 0.0
    
    # F1 Score
    if precision + recall > 0:
        f1 = 2 * (precision * recall) / (precision + recall)
    else:
        f1 = 0.0
    
    # Hallucination penalty (we really don't want fake issues)
    hallucination_penalty = false_positives * 0.1
    
    # Final reward
    reward = f1 - hallucination_penalty
    
    # Clamp to [0.0, 1.0]
    reward = max(0.0, min(1.0, reward))
    
    return round(reward, 3)
```

---

## Step 5: app.py

Create `server/app.py`:

```python
from openenv.core.env_server import create_fastapi_app
from .models import GeoAuditAction, GeoAuditObservation
from .environment import GeoAuditEnvironment

env = GeoAuditEnvironment()
app = create_fastapi_app(env, GeoAuditAction, GeoAuditObservation)
```

---

## Step 6: server/__init__.py

Create `server/__init__.py`:

```python
from .models import GeoAuditAction, GeoAuditObservation, GeoAuditState
from .environment import GeoAuditEnvironment
from .grader import calculate_reward

__all__ = [
    "GeoAuditAction",
    "GeoAuditObservation", 
    "GeoAuditState",
    "GeoAuditEnvironment",
    "calculate_reward"
]
```

---

## Step 7: inference.py

Create `inference.py` in root:

```python
#!/usr/bin/env python3
"""
GEO Audit Environment - Inference Script

This script runs an LLM agent against the GEO audit environment.
Required for hackathon evaluation.
"""

import os
import json
import asyncio
import httpx
from datetime import datetime
from openai import OpenAI

# Environment variables (REQUIRED)
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api-inference.huggingface.co/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
HF_TOKEN = os.environ.get("HF_TOKEN", "")
ENV_URL = os.environ.get("ENV_URL", "http://localhost:8000")

# Initialize OpenAI client with HF router
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN,
)


SYSTEM_PROMPT = """You are a GEO (Generative Engine Optimization) auditor.
Your job is to analyze webpages and find issues that hurt their visibility in AI search results.

## Available Actions

CHECK ACTIONS (analyze page elements):
- check_title_tag
- check_meta_description  
- check_headers
- check_schema
- check_direct_answer
- check_content_structure
- check_word_count
- check_trust_signals

FLAG ACTION (report an issue):
- flag_issue with issue_type, severity, details

SUBMIT ACTION (finish audit):
- submit_report

## Issue Types
- missing_title_tag, weak_title_tag
- missing_meta_description, weak_meta_description
- no_direct_answer, buried_answer
- missing_faq_schema, missing_howto_schema, missing_article_schema
- no_headers, poor_header_structure
- thin_content
- no_author, no_date, no_sources

## Severity Levels
- critical: Must fix immediately
- high: Should fix soon
- medium: Nice to fix
- low: Optional improvement

## Response Format
Respond with ONLY a JSON object:

For check actions:
{"action_type": "check_meta_description"}

For flag actions:
{"action_type": "flag_issue", "issue_type": "missing_meta_description", "severity": "critical", "details": "No meta description tag found"}

For submit:
{"action_type": "submit_report"}

IMPORTANT: 
- Check elements before flagging issues
- Only flag issues you have evidence for
- Don't hallucinate issues that don't exist
- Submit when you've found all issues
"""


def log_start(task_id: str, difficulty: str):
    """Log episode start in required format."""
    print(json.dumps({
        "type": "[START]",
        "timestamp": datetime.now().isoformat(),
        "task_id": task_id,
        "task_difficulty": difficulty,
    }))


def log_step(step: int, action: dict, reward: float, done: bool):
    """Log step in required format."""
    print(json.dumps({
        "type": "[STEP]",
        "timestamp": datetime.now().isoformat(),
        "step": step,
        "action": action,
        "reward": reward,
        "done": done,
    }))


def log_end(task_id: str, final_reward: float, total_steps: int):
    """Log episode end in required format."""
    print(json.dumps({
        "type": "[END]",
        "timestamp": datetime.now().isoformat(),
        "task_id": task_id,
        "final_reward": final_reward,
        "total_steps": total_steps,
    }))


def build_prompt(obs: dict) -> str:
    """Build prompt from observation."""
    page = obs.get("page", {})
    
    return f"""
Audit this webpage for GEO issues.

## Page Information
URL: {page.get('url', '')}
Target Query: "{page.get('target_query', '')}"

Title Tag: {page.get('title_tag', 'NOT FOUND') or 'EMPTY'}
Meta Description: {page.get('meta_description', 'NOT FOUND') or 'EMPTY'}
H1: {page.get('h1', '')}
First Paragraph: {page.get('first_paragraph', '')[:200]}...
Word Count: {page.get('word_count', 0)}
Headers: {page.get('headers', [])}
Schema Types: {page.get('schema_types', []) or 'NONE'}
Has Author: {page.get('has_author', False)}
Has Date: {page.get('has_date', False)}

## Your Progress
Step: {obs.get('step_count', 0)} / {obs.get('max_steps', 10)}
Issues Flagged: {obs.get('flagged_issues', [])}

## Last Message
{obs.get('message', '')}

What's your next action? Respond with JSON only.
"""


def parse_action(response: str) -> dict:
    """Parse action from LLM response."""
    import re
    
    try:
        # Find JSON in response
        json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except json.JSONDecodeError:
        pass
    
    # Default: submit if parsing fails
    return {"action_type": "submit_report"}


async def run_episode(difficulty: str) -> float:
    """Run one audit episode."""
    
    async with httpx.AsyncClient(base_url=ENV_URL, timeout=60) as http:
        # Reset environment
        reset_resp = await http.post(
            "/reset",
            json={"task_difficulty": difficulty}
        )
        obs = reset_resp.json()
        
        task_id = obs.get("task_id", f"{difficulty}_unknown")
        log_start(task_id, difficulty)
        
        step = 0
        done = False
        final_reward = 0.0
        
        while not done and step < 15:
            # Build prompt
            prompt = build_prompt(obs)
            
            # Get LLM response
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.3,
                )
                action = parse_action(response.choices[0].message.content)
            except Exception as e:
                print(f"LLM error: {e}")
                action = {"action_type": "submit_report"}
            
            # Take step
            step_resp = await http.post("/step", json={"action": action})
            obs = step_resp.json()
            
            step += 1
            done = obs.get("done", False)
            reward = obs.get("reward", 0.0)
            
            log_step(step, action, reward, done)
            
            if done:
                final_reward = reward
        
        log_end(task_id, final_reward, step)
        return final_reward


async def main():
    """Run inference on all tasks."""
    print("=" * 60)
    print("GEO AUDIT ENVIRONMENT - INFERENCE")
    print("=" * 60)
    
    results = {}
    
    for difficulty in ["easy", "medium", "hard"]:
        print(f"\n{'='*40}")
        print(f"TASK: {difficulty.upper()}")
        print("=" * 40)
        
        rewards = []
        for episode in range(3):  # 3 episodes per difficulty
            print(f"\nEpisode {episode + 1}/3")
            reward = await run_episode(difficulty)
            rewards.append(reward)
            print(f"Reward: {reward:.3f}")
        
        avg = sum(rewards) / len(rewards)
        results[difficulty] = avg
        print(f"\n{difficulty.upper()} Average: {avg:.3f}")
    
    # Final summary
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    for diff, reward in results.items():
        print(f"{diff}: {reward:.3f}")
    
    overall = sum(results.values()) / len(results)
    print(f"\nOVERALL AVERAGE: {overall:.3f}")


if __name__ == "__main__":
    asyncio.run(main())
```

---

## Step 8: Dockerfile

Create `Dockerfile` in root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir uv && \
    uv pip install --system .

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run server
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Step 9: pyproject.toml

Create `pyproject.toml`:

```toml
[project]
name = "geo-audit-env"
version = "1.0.0"
description = "GEO Audit Environment for OpenEnv Hackathon"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "openenv-core>=0.2.0",
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
    "pydantic>=2.0.0",
    "httpx>=0.24.0",
    "openai>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

---

## Step 10: openenv.yaml

Create `openenv.yaml`:

```yaml
name: geo-audit-env
version: 1.0.0
description: |
  GEO (Generative Engine Optimization) Audit Environment.
  Trains AI to find issues that hurt webpage visibility in AI search results
  like ChatGPT, Perplexity, and Google AI Overview.

author: Hijak & Hari
license: MIT

tasks:
  - id: easy
    name: Obvious Issues
    description: Pages with clear GEO problems (missing meta, no schema, etc.)
    difficulty: easy
    
  - id: medium  
    name: Subtle Issues
    description: Pages with harder-to-detect problems (weak descriptions, buried answers)
    difficulty: medium
    
  - id: hard
    name: Competitive Analysis
    description: Compare pages against competitors, find why they rank better
    difficulty: hard

endpoints:
  reset: /reset
  step: /step
  state: /state
  health: /health

action_space:
  - check_title_tag
  - check_meta_description
  - check_headers
  - check_schema
  - check_direct_answer
  - check_content_structure
  - check_word_count
  - check_trust_signals
  - flag_issue
  - submit_report

observation_space:
  - page_data
  - check_results
  - flagged_issues
  - step_count
  - message

reward_range: [0.0, 1.0]
```

---

## Step 11: README.md

Create `README.md`:

```markdown
# GEO Audit Environment

An OpenEnv environment for training AI agents to perform GEO (Generative Engine Optimization) audits.

## What is GEO?

GEO = Optimizing content to be cited by AI systems (ChatGPT, Perplexity, Google AI Overview).

Unlike SEO (ranking in search results), GEO focuses on being the **source** that AI pulls answers from.

## The Task

AI agents analyze webpages and identify issues that hurt visibility in AI-generated answers:

- Missing/weak meta descriptions
- No direct answer to target query  
- Missing structured data (FAQ, HowTo schema)
- Poor content structure
- Missing trust signals (author, date)

## Actions

| Action | Description |
|--------|-------------|
| `check_title_tag` | Analyze title tag |
| `check_meta_description` | Analyze meta description |
| `check_headers` | Analyze H1/H2/H3 structure |
| `check_schema` | Check for structured data |
| `check_direct_answer` | Check if query is answered directly |
| `check_content_structure` | Analyze overall structure |
| `check_word_count` | Check content depth |
| `check_trust_signals` | Check for author, date |
| `flag_issue` | Report a found issue |
| `submit_report` | Submit final audit |

## Tasks

1. **Easy**: Pages with obvious issues
2. **Medium**: Pages with subtle issues
3. **Hard**: Competitive analysis

## Rewards

- F1 score based on finding real issues
- Penalty for hallucinating fake issues
- Range: 0.0 to 1.0

## Installation

```bash
pip install git+https://huggingface.co/spaces/YOUR_USERNAME/geo-audit-env
```

## Usage

```python
from geo_audit_env import GeoAuditEnv, GeoAuditAction

env = GeoAuditEnv(base_url="https://YOUR_SPACE.hf.space")

# Start audit
obs = env.reset(task_difficulty="easy")

# Check elements
obs = env.step(GeoAuditAction(action_type="check_meta_description"))

# Flag issue
obs = env.step(GeoAuditAction(
    action_type="flag_issue",
    issue_type="missing_meta_description",
    severity="critical"
))

# Submit
obs = env.step(GeoAuditAction(action_type="submit_report"))
print(f"Reward: {obs.reward}")
```

## Authors

- **Hijak** (Prajhaan) - Environment design & coding
- **Hari** - Data collection & labeling

## License

MIT
```

---

## Local Testing Commands

```bash
# Activate environment
source venv/bin/activate

# Run server locally
uvicorn server.app:app --reload --port 8000

# In another terminal, test endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/reset -H "Content-Type: application/json" -d '{"task_difficulty": "easy"}'

# Build Docker
docker build -t geo-audit-env .
docker run -p 8000:8000 geo-audit-env

# Run inference (set env vars first)
export HF_TOKEN="your_token"
export ENV_URL="http://localhost:8000"
python inference.py

# Validate OpenEnv spec
openenv validate

# Push to Hugging Face
openenv push --repo-id YOUR_USERNAME/geo-audit-env
```

---

## Checklist Before Submit

```
☐ server/models.py created
☐ server/environment.py created  
☐ server/grader.py created
☐ server/app.py created
☐ server/__init__.py created
☐ inference.py created
☐ Dockerfile created (in root)
☐ pyproject.toml created
☐ openenv.yaml created
☐ README.md created
☐ data/task1_easy.json has 20 pages
☐ data/task2_medium.json has 20 pages
☐ data/task3_hard.json has 20 pages
☐ Local server runs without errors
☐ Docker builds successfully
☐ inference.py completes
☐ Deployed to Hugging Face
☐ HF Space responds to /health
☐ openenv validate passes
```
