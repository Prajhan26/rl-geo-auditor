from dataclasses import dataclass
from typing import Tuple

@dataclass
class State:
    position: Tuple[int, int]

@dataclass
class Action:
    move: str  # "up", "down", "left", "right"

@dataclass
class Observation:
    position: Tuple[int, int]