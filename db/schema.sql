CREATE TABLE IF NOT EXISTS rulesets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  version TEXT NOT NULL UNIQUE,
  is_active INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rule_nodes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ruleset_id INTEGER NOT NULL,
  node_type TEXT NOT NULL CHECK (node_type IN ('classification', 'sub_family', 'specialism')),
  name TEXT NOT NULL,
  min_score REAL NOT NULL DEFAULT 1.0,
  parent_node_id INTEGER NULL,
  FOREIGN KEY(ruleset_id) REFERENCES rulesets(id),
  FOREIGN KEY(parent_node_id) REFERENCES rule_nodes(id)
);

CREATE TABLE IF NOT EXISTS rule_keywords (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ruleset_id INTEGER NOT NULL,
  node_id INTEGER NOT NULL,
  keyword TEXT NOT NULL,
  weight REAL NOT NULL DEFAULT 1.0,
  FOREIGN KEY(ruleset_id) REFERENCES rulesets(id),
  FOREIGN KEY(node_id) REFERENCES rule_nodes(id)
);

CREATE INDEX IF NOT EXISTS idx_rule_nodes_ruleset ON rule_nodes(ruleset_id);
CREATE INDEX IF NOT EXISTS idx_rule_keywords_ruleset ON rule_keywords(ruleset_id);
CREATE INDEX IF NOT EXISTS idx_rule_keywords_node ON rule_keywords(node_id);
