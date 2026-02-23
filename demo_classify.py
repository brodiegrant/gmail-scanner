from __future__ import annotations

from cv_classifier import CVClassificationEngine, SQLiteRulesetRepository


CV_TEXT = """
Senior software developer with 8 years of experience building Python APIs and microservices.
Hands-on with Kubernetes and Terraform. Built REST services for high-scale platforms.
"""


def main() -> None:
    repository = SQLiteRulesetRepository("cv_rules.db")
    engine = CVClassificationEngine(repository)
    result = engine.classify(CV_TEXT)
    print(result)


if __name__ == "__main__":
    main()
