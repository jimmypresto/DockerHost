import sqlite3
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
import os

DB_PATH = os.environ.get("DB_PATH", "/data/db/faces.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id                INTEGER PRIMARY KEY,
            path              TEXT UNIQUE,
            face_detected     BOOLEAN,
            embedding         BLOB,
            cluster_id        INTEGER,
            manually_assigned BOOLEAN DEFAULT 0,
            processed_at      TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS clusters (
            id         INTEGER PRIMARY KEY,
            label      TEXT,
            created_at TIMESTAMP
        );
    """)
    # Migrate existing DB that may not have the column yet
    try:
        conn.execute("ALTER TABLE snapshots ADD COLUMN manually_assigned BOOLEAN DEFAULT 0")
        conn.commit()
    except Exception:
        pass  # column already exists
    conn.close()


def snapshot_exists(path: str) -> bool:
    conn = get_conn()
    row = conn.execute("SELECT 1 FROM snapshots WHERE path = ?", (path,)).fetchone()
    conn.close()
    return row is not None


def insert_snapshot(path: str, face_detected: bool, embedding: np.ndarray | None):
    emb_bytes = embedding.astype(np.float32).tobytes() if embedding is not None else None
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO snapshots (path, face_detected, embedding, cluster_id, processed_at) "
        "VALUES (?, ?, ?, -1, ?)",
        (path, face_detected, emb_bytes, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def load_embeddings() -> tuple[list[int], np.ndarray]:
    """Return (ids, embeddings) for all snapshots with a face detected."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, embedding FROM snapshots WHERE face_detected = 1 AND embedding IS NOT NULL"
    ).fetchall()
    conn.close()
    ids = [r["id"] for r in rows]
    embeddings = np.array(
        [np.frombuffer(r["embedding"], dtype=np.float32) for r in rows]
    )
    return ids, embeddings


def update_cluster_assignments(assignments: dict[int, int]):
    """assignments: {snapshot_id: cluster_id} — skips manually assigned snapshots."""
    conn = get_conn()
    conn.executemany(
        "UPDATE snapshots SET cluster_id = ? WHERE id = ? AND manually_assigned = 0",
        [(cid, sid) for sid, cid in assignments.items()],
    )
    conn.commit()
    conn.close()


def sync_clusters_table(cluster_ids: set[int]):
    """Ensure a clusters row exists for each non-noise cluster_id."""
    conn = get_conn()
    existing = {r[0] for r in conn.execute("SELECT id FROM clusters").fetchall()}
    new_ids = cluster_ids - existing
    now = datetime.now(timezone.utc).isoformat()
    conn.executemany(
        "INSERT INTO clusters (id, label, created_at) VALUES (?, NULL, ?)",
        [(cid, now) for cid in new_ids],
    )
    conn.commit()
    conn.close()


def create_cluster(label: str | None = None) -> int:
    """Create a new empty cluster and return its id."""
    conn = get_conn()
    # Use an id above any HDBSCAN-assigned id to avoid collisions
    max_id = conn.execute("SELECT COALESCE(MAX(id), -1) FROM clusters").fetchone()[0]
    new_id = max(max_id + 1, 10000)
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO clusters (id, label, created_at) VALUES (?, ?, ?)",
        (new_id, label or None, now),
    )
    conn.commit()
    conn.close()
    return new_id


def get_all_clusters() -> list[sqlite3.Row]:
    conn = get_conn()
    rows = conn.execute("""
        SELECT c.id, c.label,
               COUNT(s.id) AS face_count
        FROM clusters c
        LEFT JOIN snapshots s ON s.cluster_id = c.id
        GROUP BY c.id
        ORDER BY face_count DESC
    """).fetchall()
    conn.close()
    return rows


def get_cluster(cluster_id: int) -> sqlite3.Row | None:
    conn = get_conn()
    row = conn.execute("SELECT * FROM clusters WHERE id = ?", (cluster_id,)).fetchone()
    conn.close()
    return row


def get_snapshots_in_cluster(cluster_id: int) -> list[sqlite3.Row]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM snapshots WHERE cluster_id = ? ORDER BY processed_at",
        (cluster_id,),
    ).fetchall()
    conn.close()
    return rows


def get_noise_snapshots() -> list[sqlite3.Row]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM snapshots WHERE cluster_id = -1 AND face_detected = 1 ORDER BY processed_at"
    ).fetchall()
    conn.close()
    return rows


def set_cluster_label(cluster_id: int, label: str):
    conn = get_conn()
    conn.execute("UPDATE clusters SET label = ? WHERE id = ?", (label, cluster_id))
    conn.commit()
    conn.close()


def merge_clusters(source_id: int, target_id: int):
    """Move all snapshots from source_id into target_id, then delete source cluster."""
    conn = get_conn()
    conn.execute(
        "UPDATE snapshots SET cluster_id = ?, manually_assigned = 1 WHERE cluster_id = ?",
        (target_id, source_id),
    )
    conn.execute("DELETE FROM clusters WHERE id = ?", (source_id,))
    conn.commit()
    conn.close()


def delete_cluster(cluster_id: int):
    """Delete cluster and return its snapshots to noise (-1)."""
    conn = get_conn()
    conn.execute(
        "UPDATE snapshots SET cluster_id = -1, manually_assigned = 0 WHERE cluster_id = ?",
        (cluster_id,),
    )
    conn.execute("DELETE FROM clusters WHERE id = ?", (cluster_id,))
    conn.commit()
    conn.close()


def move_snapshot(snapshot_id: int, target_cluster_id: int):
    conn = get_conn()
    conn.execute(
        "UPDATE snapshots SET cluster_id = ?, manually_assigned = 1 WHERE id = ?",
        (target_cluster_id, snapshot_id),
    )
    conn.commit()
    conn.close()


def get_stats() -> dict:
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
    faces = conn.execute("SELECT COUNT(*) FROM snapshots WHERE face_detected = 1").fetchone()[0]
    clusters = conn.execute("SELECT COUNT(*) FROM clusters").fetchone()[0]
    noise = conn.execute(
        "SELECT COUNT(*) FROM snapshots WHERE cluster_id = -1 AND face_detected = 1"
    ).fetchone()[0]
    conn.close()
    return {"total": total, "faces": faces, "clusters": clusters, "noise": noise}
