DELETE FROM rule_keywords;
DELETE FROM rule_nodes;
DELETE FROM rulesets;

INSERT INTO rulesets (id, version, is_active) VALUES (1, '2026.01', 1);

-- Classification
INSERT INTO rule_nodes (id, ruleset_id, node_type, name, min_score, parent_node_id)
VALUES
  (100, 1, 'classification', 'Technology', 2.0, NULL),
  (101, 1, 'classification', 'Finance', 2.0, NULL);

-- Sub-family (required gate)
INSERT INTO rule_nodes (id, ruleset_id, node_type, name, min_score, parent_node_id)
VALUES
  (200, 1, 'sub_family', 'Software Engineering', 2.0, 100),
  (201, 1, 'sub_family', 'Data Engineering', 2.0, 100),
  (210, 1, 'sub_family', 'Accounting', 2.0, 101);

-- Specialisms (multi-select)
INSERT INTO rule_nodes (id, ruleset_id, node_type, name, min_score, parent_node_id)
VALUES
  (300, 1, 'specialism', 'Backend', 1.0, 200),
  (301, 1, 'specialism', 'Frontend', 1.0, 200),
  (302, 1, 'specialism', 'DevOps', 1.0, 200),
  (310, 1, 'specialism', 'ETL', 1.0, 201),
  (311, 1, 'specialism', 'Data Platform', 1.0, 201),
  (320, 1, 'specialism', 'Tax', 1.0, 210);

INSERT INTO rule_keywords (ruleset_id, node_id, keyword, weight) VALUES
  (1, 100, 'software', 1.2),
  (1, 100, 'engineering', 1.0),
  (1, 100, 'developer', 1.0),
  (1, 101, 'finance', 1.2),
  (1, 101, 'accounting', 1.0),
  (1, 101, 'ledger', 1.0),

  (1, 200, 'python', 1.0),
  (1, 200, 'java', 1.0),
  (1, 200, 'api', 1.0),
  (1, 201, 'spark', 1.0),
  (1, 201, 'airflow', 1.0),
  (1, 201, 'pipeline', 1.0),
  (1, 210, 'ifrs', 1.0),
  (1, 210, 'balance sheet', 1.0),
  (1, 210, 'audit', 1.0),

  (1, 300, 'microservices', 1.0),
  (1, 300, 'rest', 1.0),
  (1, 301, 'react', 1.0),
  (1, 301, 'javascript', 1.0),
  (1, 302, 'kubernetes', 1.0),
  (1, 302, 'terraform', 1.0),
  (1, 310, 'etl', 1.0),
  (1, 310, 'dbt', 1.0),
  (1, 311, 'snowflake', 1.0),
  (1, 311, 'bigquery', 1.0),
  (1, 320, 'corporate tax', 1.0),
  (1, 320, 'vat', 1.0);
