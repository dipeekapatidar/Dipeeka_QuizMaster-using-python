"""Database helper for the Quiz Application (SQLite)."""
import json
import os
import random
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "quiz.db")
JSON_PATH = os.path.join(BASE_DIR, "questions.json")


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create tables and load any new questions from questions.json."""
    with get_conn() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                question TEXT NOT NULL UNIQUE,
                option1 TEXT NOT NULL,
                option2 TEXT NOT NULL,
                option3 TEXT NOT NULL,
                option4 TEXT NOT NULL,
                answer INTEGER NOT NULL
            )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player TEXT NOT NULL,
                category TEXT NOT NULL,
                score REAL NOT NULL,
                correct INTEGER NOT NULL,
                wrong INTEGER NOT NULL,
                skipped INTEGER NOT NULL,
                played_on TEXT NOT NULL
            )"""
        )
        if os.path.exists(JSON_PATH):
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                items = json.load(f)
            for q in items:
                o = q["options"]
                conn.execute(
                    "INSERT OR IGNORE INTO questions "
                    "(category, question, option1, option2, option3, option4, answer) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (q["category"], q["question"], o[0], o[1], o[2], o[3], q["answer"]),
                )


def get_categories():
    with get_conn() as conn:
        rows = conn.execute("SELECT DISTINCT category FROM questions ORDER BY category").fetchall()
    return [r[0] for r in rows]


def count_questions(category="All"):
    with get_conn() as conn:
        if category == "All":
            return conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        return conn.execute(
            "SELECT COUNT(*) FROM questions WHERE category = ?", (category,)
        ).fetchone()[0]


def get_random_questions(category="All", n=10):
    """Return up to n random questions; options are shuffled each time."""
    with get_conn() as conn:
        if category == "All":
            rows = conn.execute(
                "SELECT category, question, option1, option2, option3, option4, answer "
                "FROM questions ORDER BY RANDOM() LIMIT ?", (n,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT category, question, option1, option2, option3, option4, answer "
                "FROM questions WHERE category = ? ORDER BY RANDOM() LIMIT ?", (category, n)
            ).fetchall()

    questions = []
    for cat, text, o1, o2, o3, o4, ans in rows:
        options = [o1, o2, o3, o4]
        correct_text = options[ans]
        random.shuffle(options)
        questions.append(
            {
                "category": cat,
                "question": text,
                "options": options,
                "answer": options.index(correct_text),
            }
        )
    return questions


def save_score(player, category, score, correct, wrong, skipped):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO leaderboard (player, category, score, correct, wrong, skipped, played_on) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (player, category, score, correct, wrong, skipped,
             datetime.now().strftime("%Y-%m-%d %H:%M")),
        )


def get_leaderboard(category="All", limit=10):
    with get_conn() as conn:
        if category == "All":
            return conn.execute(
                "SELECT player, category, score, correct, wrong, played_on FROM leaderboard "
                "ORDER BY score DESC, played_on ASC LIMIT ?", (limit,)
            ).fetchall()
        return conn.execute(
            "SELECT player, category, score, correct, wrong, played_on FROM leaderboard "
            "WHERE category = ? ORDER BY score DESC, played_on ASC LIMIT ?", (category, limit)
        ).fetchall()
