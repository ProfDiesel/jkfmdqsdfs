import os
import sqlite3

def semver_loadable_path():
  loadable_path = os.path.join(os.path.dirname(__file__), "semver")
  return os.path.normpath(loadable_path)

def load_semver(conn: sqlite3.Connection)  -> None:
  conn.load_extension(semver_loadable_path())

def load(conn: sqlite3.Connection)  -> None:
  load_semver(conn)

