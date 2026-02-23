from __future__ import annotations

import re
from dataclasses import dataclass

from .repository import SQLiteRulesetRepository
from .types import CVClassificationResult, NodeRule, ScoredNode


@dataclass(frozen=True)
class EngineConfig:
    specialism_score_floor: float = 1.0


class CVClassificationEngine:
    """
    CV classifier driven by database-configured, versioned rulesets.

    Decision flow:
    1) score classification nodes
    2) score sub-families under winning classification (required gate)
    3) score all specialisms under winning sub-family and keep multi-match results
    4) return accepted / flagged / blocked with explicit evidence reasons
    """

    def __init__(
        self,
        ruleset_repository: SQLiteRulesetRepository,
        config: EngineConfig | None = None,
    ):
        self.ruleset_repository = ruleset_repository
        self.config = config or EngineConfig()

    def classify(self, cv_text: str) -> CVClassificationResult:
        normalized = self._normalize(cv_text)
        ruleset = self.ruleset_repository.load_active_ruleset()
        reasons: list[str] = []

        classification = self._best_match(ruleset.classifications, normalized)
        if classification is None:
            reasons.append("No classification met minimum evidence threshold.")
            return CVClassificationResult(ruleset.version, None, None, [], "blocked", reasons)

        candidate_sub_families = [n for n in ruleset.sub_families if n.parent_node_id == classification.node_id]
        sub_family = self._best_match(candidate_sub_families, normalized)
        if sub_family is None:
            reasons.append("Classification matched but no sub-family met minimum evidence (required gate failed).")
            return CVClassificationResult(ruleset.version, classification, None, [], "blocked", reasons)

        candidate_specialisms = [n for n in ruleset.specialisms if n.parent_node_id == sub_family.node_id]
        scored_specialisms = self._score_all(candidate_specialisms, normalized)
        matched_specialisms = [
            s for s in scored_specialisms
            if s.score >= max(self.config.specialism_score_floor, self._node_min_score(candidate_specialisms, s.node_id))
        ]

        status = "accepted"
        if not matched_specialisms:
            status = "flagged"
            reasons.append("Classification and sub-family passed but no specialism met threshold; manual review recommended.")

        return CVClassificationResult(
            ruleset.version,
            classification,
            sub_family,
            sorted(matched_specialisms, key=lambda n: n.score, reverse=True),
            status,
            reasons,
        )

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text.lower()).strip()

    @staticmethod
    def _node_min_score(nodes: list[NodeRule], node_id: int) -> float:
        for node in nodes:
            if node.node_id == node_id:
                return node.min_score
        return 0.0

    def _score_all(self, nodes: list[NodeRule], text: str) -> list[ScoredNode]:
        return [self._score_node(node, text) for node in nodes]

    def _best_match(self, nodes: list[NodeRule], text: str) -> ScoredNode | None:
        scored = [self._score_node(node, text) for node in nodes]
        eligible = [s for s in scored if s.score >= self._node_min_score(nodes, s.node_id)]
        if not eligible:
            return None
        return sorted(eligible, key=lambda n: n.score, reverse=True)[0]

    @staticmethod
    def _keyword_pattern(phrase: str) -> str:
        escaped = re.escape(phrase.lower())
        if " " not in phrase and phrase.isalpha():
            return rf"\b{escaped}s?\b"
        return rf"\b{escaped}\b"

    def _score_node(self, node: NodeRule, text: str) -> ScoredNode:
        total_score = 0.0
        matches: list[str] = []
        for kw in node.keywords:
            if re.search(self._keyword_pattern(kw.phrase), text):
                total_score += kw.weight
                matches.append(kw.phrase)

        return ScoredNode(node.node_id, node.node_type, node.name, round(total_score, 3), matches)
