"""
FastAPI web UI for reviewing face clusters.
"""

import os
import logging
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from typing import List
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app import database as db

log = logging.getLogger(__name__)

SNAPSHOT_DIR = os.environ.get("SNAPSHOT_DIR", "/data/snapshots")

app = FastAPI(title="Face Clustering UI")
templates = Jinja2Templates(directory="/app/app/templates")


@app.on_event("startup")
def startup():
    db.init_db()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _snapshot_url(path: str) -> str:
    """Convert absolute container path to a URL served by /snapshots/."""
    rel = Path(path).relative_to(SNAPSHOT_DIR)
    return f"/snapshots/{rel}"


def _cluster_thumbnails(cluster_id: int, limit: int = 3) -> list[str]:
    rows = db.get_snapshots_in_cluster(cluster_id)
    return [_snapshot_url(r["path"]) for r in rows[:limit]]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    clusters = db.get_all_clusters()
    stats = db.get_stats()

    cluster_data = []
    for c in clusters:
        thumbs = _cluster_thumbnails(c["id"])
        cluster_data.append({
            "id": c["id"],
            "label": c["label"] or f"Cluster {c['id']}",
            "face_count": c["face_count"],
            "thumbnails": thumbs,
        })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "clusters": cluster_data,
        "stats": stats,
    })


@app.get("/cluster/{cluster_id}", response_class=HTMLResponse)
def cluster_detail(request: Request, cluster_id: int):
    cluster = db.get_cluster(cluster_id)
    if cluster is None:
        raise HTTPException(status_code=404, detail="Cluster not found")

    snapshots = db.get_snapshots_in_cluster(cluster_id)
    all_clusters = db.get_all_clusters()

    snap_data = [
        {
            "id": s["id"],
            "url": _snapshot_url(s["path"]),
            "path": s["path"],
            "processed_at": s["processed_at"],
        }
        for s in snapshots
    ]

    other_clusters = [
        {"id": c["id"], "label": c["label"] or f"Cluster {c['id']}"}
        for c in all_clusters
        if c["id"] != cluster_id
    ]

    return templates.TemplateResponse("cluster.html", {
        "request": request,
        "cluster": {"id": cluster["id"], "label": cluster["label"] or f"Cluster {cluster['id']}"},
        "snapshots": snap_data,
        "other_clusters": other_clusters,
    })


@app.post("/cluster/{cluster_id}/label")
def set_label(cluster_id: int, label: str = Form(...)):
    cluster = db.get_cluster(cluster_id)
    if cluster is None:
        raise HTTPException(status_code=404, detail="Cluster not found")
    db.set_cluster_label(cluster_id, label.strip())
    return RedirectResponse(f"/cluster/{cluster_id}", status_code=303)


@app.post("/cluster/{cluster_id}/merge/{other_id}")
def merge(cluster_id: int, other_id: int):
    if cluster_id == other_id:
        raise HTTPException(status_code=400, detail="Cannot merge a cluster with itself")
    for cid in (cluster_id, other_id):
        if db.get_cluster(cid) is None:
            raise HTTPException(status_code=404, detail=f"Cluster {cid} not found")
    # Merge other_id into cluster_id (keep cluster_id)
    db.merge_clusters(source_id=other_id, target_id=cluster_id)
    return RedirectResponse(f"/cluster/{cluster_id}", status_code=303)


@app.post("/cluster/new")
def create_cluster(label: str = Form("")):
    new_id = db.create_cluster(label.strip() or None)
    return RedirectResponse(f"/cluster/{new_id}", status_code=303)


@app.post("/cluster/{cluster_id}/delete")
def delete_cluster(cluster_id: int):
    if db.get_cluster(cluster_id) is None:
        raise HTTPException(status_code=404, detail="Cluster not found")
    db.delete_cluster(cluster_id)
    return RedirectResponse("/", status_code=303)


@app.post("/snapshots/move")
def move_snapshots_bulk(
    snapshot_ids: List[int] = Form(...),
    target_cluster_id: int = Form(...),
    from_cluster: int = Form(None),
):
    for sid in snapshot_ids:
        db.move_snapshot(sid, target_cluster_id)
    if from_cluster == -1:
        return RedirectResponse("/noise", status_code=303)
    if from_cluster is not None:
        return RedirectResponse(f"/cluster/{from_cluster}", status_code=303)
    return RedirectResponse("/", status_code=303)


@app.post("/snapshot/{snapshot_id}/move/{target_cluster_id}")
def move_snapshot(snapshot_id: int, target_cluster_id: int, from_cluster: int = None):
    db.move_snapshot(snapshot_id, target_cluster_id)
    # Redirect back to the cluster the user came from, or the target
    back = from_cluster if from_cluster is not None else target_cluster_id
    if back == -1:
        return RedirectResponse("/noise", status_code=303)
    return RedirectResponse(f"/cluster/{back}", status_code=303)


@app.get("/noise", response_class=HTMLResponse)
def noise_view(request: Request):
    rows = db.get_noise_snapshots()
    snaps = [
        {"id": r["id"], "url": _snapshot_url(r["path"]), "path": r["path"]}
        for r in rows
    ]
    all_clusters = db.get_all_clusters()
    clusters = [{"id": c["id"], "label": c["label"] or f"Cluster {c['id']}"} for c in all_clusters]
    return templates.TemplateResponse("noise.html", {
        "request": request,
        "snapshots": snaps,
        "count": len(snaps),
        "clusters": clusters,
    })


@app.get("/reprocess")
def reprocess():
    """Re-run HDBSCAN on all stored embeddings (embeddings already computed)."""
    from app.processor import run_clustering
    summary = run_clustering()
    return {
        "status": "ok",
        "faces": summary["faces"],
        "clusters": summary["clusters"],
        "noise": summary["noise"],
    }


@app.get("/snapshots/{path:path}")
def serve_snapshot(path: str):
    full_path = Path(SNAPSHOT_DIR) / path
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(str(full_path))
