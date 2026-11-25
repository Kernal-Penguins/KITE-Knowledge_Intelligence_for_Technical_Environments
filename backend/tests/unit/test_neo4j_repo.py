"""Graph tokens used inside Cypher must be Neo4j names, not enum reprs."""
import pytest

from app.repositories.neo4j_repo import graph_token
from app.shared.ontology import NodeLabel, RelType


def test_enum_label_uses_neo4j_name():
    assert graph_token(NodeLabel.EQUIPMENT) == "Equipment"
    assert graph_token(RelType.HAS_FAILURE) == "HAS_FAILURE"
    assert f"MERGE (a:{graph_token(NodeLabel.EQUIPMENT)} {{id: $from_id}})" == (
        "MERGE (a:Equipment {id: $from_id})"
    )


def test_plain_label_is_kept():
    assert graph_token("WorkOrder") == "WorkOrder"


def test_dotted_enum_repr_is_rejected():
    with pytest.raises(ValueError):
        graph_token("NodeLabel.EQUIPMENT")
