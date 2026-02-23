from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from cv_classifier import CVClassificationEngine, SQLiteRulesetRepository


class ClassificationEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "rules.db"
        root = Path(__file__).resolve().parents[1]
        schema = (root / "db" / "schema.sql").read_text()
        seed = (root / "db" / "seed_v1.sql").read_text()
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema)
            conn.executescript(seed)

        self.engine = CVClassificationEngine(SQLiteRulesetRepository(self.db_path))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_accepts_when_classification_subfamily_and_specialism_match(self) -> None:
        text = "Software developer experienced in Python APIs, microservices, and Kubernetes."
        result = self.engine.classify(text)
        self.assertEqual(result.status, "accepted")
        self.assertEqual(result.classification.name, "Technology")
        self.assertEqual(result.sub_family.name, "Software Engineering")
        self.assertTrue(any(s.name == "Backend" for s in result.specialisms))

    def test_blocks_when_subfamily_gate_fails(self) -> None:
        text = "Software developer with product ownership and stakeholder management experience."
        result = self.engine.classify(text)
        self.assertEqual(result.status, "blocked")
        self.assertIsNotNone(result.classification)
        self.assertIsNone(result.sub_family)

    def test_flags_when_no_specialism(self) -> None:
        text = "Software engineering candidate with Java and Python API experience."
        result = self.engine.classify(text)
        self.assertEqual(result.status, "flagged")
        self.assertEqual(result.sub_family.name, "Software Engineering")
        self.assertEqual(result.specialisms, [])

    def test_keyword_changes_require_no_code_change(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO rule_keywords (ruleset_id, node_id, keyword, weight) VALUES (?, ?, ?, ?)",
                (1, 301, "typescript", 1.0),
            )
            conn.commit()

        result = self.engine.classify("Frontend software developer with TypeScript expertise and Python APIs")
        self.assertTrue(any(s.name == "Frontend" for s in result.specialisms))


if __name__ == "__main__":
    unittest.main()
