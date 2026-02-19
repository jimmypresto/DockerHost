"""
Batch processor: scan Frigate snapshots → detect faces → embed → cluster → store.
"""

import os
import sys
import logging
import numpy as np
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [processor] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

SNAPSHOT_DIR = os.environ.get("SNAPSHOT_DIR", "/data/snapshots")
MIN_CLUSTER_SIZE = int(os.environ.get("MIN_CLUSTER_SIZE", "3"))
MIN_SAMPLES = int(os.environ.get("MIN_SAMPLES", "2"))
CLUSTER_EPSILON = float(os.environ.get("CLUSTER_EPSILON", "0.35"))
MIN_DET_SCORE = 0.5


def load_insightface():
    from insightface.app import FaceAnalysis
    app = FaceAnalysis(
        name="buffalo_l",
        root=os.environ.get("INSIGHTFACE_HOME", "/app/models"),
        providers=["CPUExecutionProvider"],
    )
    app.prepare(ctx_id=-1, det_size=(640, 640))
    return app


def scan_snapshots(snapshot_dir: str) -> list[Path]:
    """Return list of image paths to process (jpg preferred, -clean.png as fallback)."""
    base = Path(snapshot_dir)
    if not base.exists():
        log.warning("Snapshot directory does not exist: %s", snapshot_dir)
        return []

    # Collect all jpg files; include -clean.png only if no matching jpg exists
    jpgs = set(base.rglob("*.jpg"))
    pngs = set(base.rglob("*-clean.png"))

    # For each png, skip if a sibling jpg exists with the same stem (minus -clean)
    paths = list(jpgs)
    for png in pngs:
        stem = png.stem.removesuffix("-clean")
        sibling_jpg = png.parent / f"{stem}.jpg"
        if sibling_jpg not in jpgs:
            paths.append(png)

    paths.sort()
    return paths


def process_snapshots(face_app) -> int:
    """Scan and embed new snapshots. Returns count of newly processed images."""
    import cv2
    from app import database as db

    paths = scan_snapshots(SNAPSHOT_DIR)
    log.info("Found %d snapshot files in %s", len(paths), SNAPSHOT_DIR)

    new_count = 0
    face_count = 0

    for path in paths:
        path_str = str(path)
        if db.snapshot_exists(path_str):
            continue

        img = cv2.imread(path_str)
        if img is None:
            log.warning("Could not read image: %s", path_str)
            db.insert_snapshot(path_str, face_detected=False, embedding=None)
            new_count += 1
            continue

        try:
            faces = face_app.get(img)
        except Exception as exc:
            log.warning("InsightFace error on %s: %s", path_str, exc)
            db.insert_snapshot(path_str, face_detected=False, embedding=None)
            new_count += 1
            continue

        # Filter by detection confidence
        faces = [f for f in faces if f.det_score >= MIN_DET_SCORE]

        if not faces:
            db.insert_snapshot(path_str, face_detected=False, embedding=None)
            new_count += 1
            continue

        # Pick highest-confidence face
        best = max(faces, key=lambda f: f.det_score)
        embedding = best.normed_embedding  # already L2-normalised, shape (512,)
        db.insert_snapshot(path_str, face_detected=True, embedding=embedding)
        face_count += 1
        new_count += 1

    log.info("Processed %d new images, found %d faces", new_count, face_count)
    return new_count


def run_clustering() -> dict:
    """Re-cluster all stored face embeddings. Returns summary dict."""
    from sklearn.cluster import HDBSCAN
    from app import database as db

    ids, embeddings = db.load_embeddings()
    if len(ids) < 2:
        log.info("Not enough faces to cluster (%d found)", len(ids))
        return {"faces": len(ids), "clusters": 0, "noise": len(ids)}

    log.info("Clustering %d face embeddings (min_cluster_size=%d, epsilon=%.2f)...",
             len(ids), MIN_CLUSTER_SIZE, CLUSTER_EPSILON)

    hdb = HDBSCAN(
        min_cluster_size=MIN_CLUSTER_SIZE,
        min_samples=MIN_SAMPLES,
        metric="cosine",
        cluster_selection_epsilon=CLUSTER_EPSILON,
    )
    labels = hdb.fit_predict(embeddings)

    assignments = {sid: int(lbl) for sid, lbl in zip(ids, labels)}
    db.update_cluster_assignments(assignments)

    unique_clusters = {int(lbl) for lbl in labels if lbl >= 0}
    db.sync_clusters_table(unique_clusters)

    noise_count = int(np.sum(labels == -1))
    log.info(
        "Clustering complete: %d clusters, %d noise/unassigned out of %d faces",
        len(unique_clusters), noise_count, len(ids),
    )
    return {
        "faces": len(ids),
        "clusters": len(unique_clusters),
        "noise": noise_count,
    }


def main():
    from app import database as db

    log.info("Initialising database...")
    db.init_db()

    log.info("Loading InsightFace buffalo_l model...")
    face_app = load_insightface()

    log.info("Scanning snapshots...")
    process_snapshots(face_app)

    log.info("Running HDBSCAN clustering...")
    summary = run_clustering()

    log.info(
        "Done. faces=%d  clusters=%d  noise=%d",
        summary["faces"], summary["clusters"], summary["noise"],
    )


if __name__ == "__main__":
    main()
