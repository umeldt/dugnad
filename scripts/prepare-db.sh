#!/bin/sh

cat <<EOF | sqlite3 dugnad.db
CREATE TABLE IF NOT EXISTS
  sources(id, project, completed, skipped, priority, difficulty, data);
CREATE TABLE IF NOT EXISTS
  entries(id, user, project, date, data, finished, updated);
CREATE TABLE IF NOT EXISTS
  markings(id, user, project, date, entry, page, markings);
EOF

