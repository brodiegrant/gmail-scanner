from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


NodeType = Literal["classification", "sub_family", "specialism"]


@dataclass(frozen=True)
class ScoredNode:
    node_id: int
    node_type: NodeType
    name: str
    score: float
    matched_keywords: list[str]


@dataclass(frozen=True)
class CVClassificationResult:
    ruleset_version: str
    classification: ScoredNode | None
    sub_family: ScoredNode | None
    specialisms: list[ScoredNode]
    status: Literal["accepted", "flagged", "blocked"]
    reasons: list[str]


@dataclass(frozen=True)
class KeywordRule:
    phrase: str
    weight: float


@dataclass(frozen=True)
class NodeRule:
    node_id: int
    node_type: NodeType
    name: str
    min_score: float
    parent_node_id: int | None
    keywords: list[KeywordRule]


@dataclass(frozen=True)
class RuleSet:
    ruleset_id: int
    version: str
    classifications: list[NodeRule]
    sub_families: list[NodeRule]
    specialisms: list[NodeRule]
