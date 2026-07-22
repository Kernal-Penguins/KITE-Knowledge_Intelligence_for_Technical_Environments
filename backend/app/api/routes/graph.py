"""
api/routes/graph.py
───────────────────
GET /api/v1/graph/nodes  — Return graph nodes + edges for the frontend explorer.
GET /api/v1/graph/stats  — Quick counts (nodes + edges by label).
"""
from fastapi import APIRouter, HTTPException, Query

from app.infrastructure.logger import log
from app.infrastructure.neo4j_client import neo4j_client
from app.shared.api_models import GraphExplorerEdge, GraphExplorerNode, GraphExplorerResponse

router = APIRouter(prefix="/graph", tags=["Graph"])


@router.get("/nodes", response_model=GraphExplorerResponse)
async def get_graph_nodes(
    limit: int = Query(default=100, ge=1, le=500, description="Max nodes to return."),
    node_type: str | None = Query(default=None, description="Filter by node label, e.g. 'Equipment'."),
) -> GraphExplorerResponse:
    """
    Return a sample of graph nodes and their relationships for the Graph Explorer.
    Optionally filter by node label (Equipment, Failure, Procedure, etc.).
    """
    nodes: list[GraphExplorerNode] = []
    edges: list[GraphExplorerEdge] = []

    try:
        async with neo4j_client.session() as session:
            # ── Nodes ──────────────────────────────────────────────────────────
            if node_type:
                node_query = (
                    f"MATCH (n:`{node_type}`) RETURN n LIMIT $limit"  # noqa: S608
                )
            else:
                node_query = "MATCH (n) RETURN n LIMIT $limit"

            node_result = await session.run(node_query, limit=limit)
            node_records = await node_result.data()

            for rec in node_records:
                raw = rec["n"]
                props = dict(raw)
                node_id = props.get("id") or props.get("equipment_id") or str(id(raw))
                label = props.get("name") or props.get("tag") or props.get("id") or node_id
                # Get the primary label (first label on the node)
                labels = list(raw.labels) if hasattr(raw, "labels") else []
                ntype = labels[0] if labels else "Unknown"

                nodes.append(
                    GraphExplorerNode(
                        id=str(node_id),
                        label=str(label),
                        properties={k: str(v) for k, v in props.items()},
                        node_type=ntype,
                    )
                )

            # ── Edges (only between the nodes we already fetched) ──────────────
            if nodes:
                node_ids = [n.id for n in nodes]
                edge_result = await session.run(
                    """
                    MATCH (a)-[r]->(b)
                    WHERE a.id IN $ids AND b.id IN $ids
                    RETURN a.id AS src, b.id AS tgt, type(r) AS rel
                    LIMIT $elimit
                    """,
                    ids=node_ids,
                    elimit=min(limit * 3, 1500),
                )
                edge_records = await edge_result.data()
                for rec in edge_records:
                    if rec.get("src") and rec.get("tgt"):
                        edges.append(
                            GraphExplorerEdge(
                                source=str(rec["src"]),
                                target=str(rec["tgt"]),
                                rel_type=str(rec["rel"]),
                            )
                        )

    except RuntimeError as exc:
        # Neo4j driver not yet initialised (startup race condition)
        log.warning("graph.nodes.driver_not_ready", error=str(exc))
        return GraphExplorerResponse(nodes=[], edges=[], total_nodes=0, total_edges=0)
    except Exception as exc:
        log.error("graph.nodes.failed", error=str(exc))
        raise HTTPException(status_code=503, detail="Graph database unavailable.") from exc

    return GraphExplorerResponse(
        nodes=nodes,
        edges=edges,
        total_nodes=len(nodes),
        total_edges=len(edges),
    )


@router.get("/stats")
async def get_graph_stats() -> dict:
    """Return node and edge counts grouped by label — used for the Overview page."""
    try:
        async with neo4j_client.session() as session:
            label_result = await session.run(
                "MATCH (n) UNWIND labels(n) AS lbl RETURN lbl, count(*) AS c ORDER BY c DESC LIMIT 20"
            )
            label_data = await label_result.data()

            rel_result = await session.run(
                "MATCH ()-[r]->() RETURN type(r) AS rel, count(*) AS c ORDER BY c DESC LIMIT 20"
            )
            rel_data = await rel_result.data()

        return {
            "node_counts_by_label": {r["lbl"]: r["c"] for r in label_data},
            "edge_counts_by_type": {r["rel"]: r["c"] for r in rel_data},
        }
    except RuntimeError:
        return {"node_counts_by_label": {}, "edge_counts_by_type": {}}
    except Exception as exc:
        log.error("graph.stats.failed", error=str(exc))
        raise HTTPException(status_code=503, detail="Graph database unavailable.") from exc
