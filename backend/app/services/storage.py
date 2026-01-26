from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.logging import get_logger

logger = get_logger(__name__)


DEFAULT_DB_PATH = Path("backend") / "data" / "app.db"


def _get_db_path() -> Path:
    """
    Return the SQLite database path, allowing override via APP_DB_PATH.
    """
    override = os.getenv("APP_DB_PATH")
    if override:
        return Path(override)
    return DEFAULT_DB_PATH


def _get_connection() -> sqlite3.Connection:
    db_path = _get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Initialize the SQLite database with predictions and feedback tables.

    This function is idempotent and safe to call multiple times.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_hash TEXT NOT NULL,
                model_scores_json TEXT NOT NULL,
                ensemble_score REAL NOT NULL,
                final_flag INTEGER NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions (created_at DESC);"
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id INTEGER NOT NULL,
                label TEXT NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_feedback_prediction_id ON feedback (prediction_id);"
        )
        conn.commit()
        logger.info("SQLite database initialized at %s", _get_db_path())
    finally:
        conn.close()


def insert_prediction(
    input_hash: str,
    model_scores: Dict[str, Dict[str, Any]],
    ensemble_score: float,
    final_flag: bool,
    created_at: str,
) -> int:
    """
    Insert a prediction record and return its primary key.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO predictions (input_hash, model_scores_json, ensemble_score, final_flag, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                input_hash,
                json.dumps(model_scores),
                float(ensemble_score),
                int(bool(final_flag)),
                created_at,
            ),
        )
        conn.commit()
        prediction_id = int(cur.lastrowid)
        logger.info("Inserted prediction id=%s", prediction_id)
        return prediction_id
    finally:
        conn.close()


def insert_feedback(prediction_id: int, label: str, notes: Optional[str] = None) -> int:
    """
    Insert a feedback record for a given prediction id.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO feedback (prediction_id, label, notes, created_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (prediction_id, label, notes),
        )
        conn.commit()
        feedback_id = int(cur.lastrowid)
        logger.info("Inserted feedback id=%s for prediction_id=%s", feedback_id, prediction_id)
        return feedback_id
    finally:
        conn.close()


@dataclass
class PredictionRecord:
    id: int
    created_at: str
    ensemble_score: float
    final_flag: bool


def get_recent_predictions(limit: int = 100) -> List[PredictionRecord]:
    """
    Fetch recent prediction records ordered by creation time descending.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, created_at, ensemble_score, final_flag
            FROM predictions
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (int(limit),),
        )
        rows = cur.fetchall()
        results = [
            PredictionRecord(
                id=int(row["id"]),
                created_at=str(row["created_at"]),
                ensemble_score=float(row["ensemble_score"]),
                final_flag=bool(row["final_flag"]),
            )
            for row in rows
        ]
        return results
    finally:
        conn.close()


def get_recent_ensemble_scores(window_size: int = 500) -> List[float]:
    """
    Fetch recent ensemble scores for drift monitoring.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT ensemble_score
            FROM predictions
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (int(window_size),),
        )
        rows = cur.fetchall()
        return [float(row["ensemble_score"]) for row in rows]
    finally:
        conn.close()