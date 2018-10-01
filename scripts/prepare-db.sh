#!/bin/sh

sqlite3 dugnad.db 'CREATE TABLE IF NOT EXISTS transcriptions(id, key, user, project, date, annotation, finished, updated);'
sqlite3 dugnad.db 'CREATE TABLE IF NOT EXISTS markings(id, post, project, page, markings, user, date);'

