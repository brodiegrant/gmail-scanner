from __future__ import annotations

import sqlite3
from collections import defaultdict
from pathlib import Path

from .types import KeywordRule, NodeRule, RuleSet


class SQLiteRulesetRepository:
    """Loads versioned CV classification rules from a SQLite masterlist."""

    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)

    def load_active_ruleset(self) -> RuleSet:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            ruleset_row = conn.execute(
                """
                SELECT id, version
                FROM rulesets
                WHERE is_active = 1
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
            if ruleset_row is None:
                raise ValueError("No active ruleset found in rulesets table.")

            nodes = conn.execute(
                """
                SELECT id, node_type, name, min_score, parent_node_id
                FROM rule_nodes
                WHERE ruleset_id = ?
                """,
                (ruleset_row["id"],),
            ).fetchall()

            keywords = conn.execute(
                """
                SELECT node_id, keyword, weight
                FROM rule_keywords
                WHERE ruleset_id = ?
                """,
                (ruleset_row["id"],),
            ).fetchall()

        keyword_map: dict[int, list[KeywordRule]] = defaultdict(list)
        for row in keywords:
            keyword_map[row["node_id"]].append(
                KeywordRule(phrase=row["keyword"], weight=float(row["weight"]))
            )

        classification_nodes: list[NodeRule] = []
        sub_family_nodes: list[NodeRule] = []
        specialism_nodes: list[NodeRule] = []

        for row in nodes:
            node = NodeRule(
                node_id=int(row["id"]),
                node_type=row["node_type"],
                name=row["name"],
                min_score=float(row["min_score"]),
                parent_node_id=row["parent_node_id"],
                keywords=keyword_map.get(int(row["id"]), []),
            )
            if node.node_type == "classification":
                classification_nodes.append(node)
            elif node.node_type == "sub_family":
                sub_family_nodes.append(node)
            elif node.node_type == "specialism":
                specialism_nodes.append(node)
            else:
                raise ValueError(f"Unknown node_type: {node.node_type}")

        return RuleSet(
            ruleset_id=int(ruleset_row["id"]),
            version=ruleset_row["version"],
            classifications=classification_nodes,
            sub_families=sub_family_nodes,
            specialisms=specialism_nodes,
        )
