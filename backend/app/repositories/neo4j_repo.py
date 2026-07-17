"""
repositories/neo4j_repo.py
──────────────────────────
Graph repository for persisting entities and relationships.
"""
from app.infrastructure.logger import log
from app.infrastructure.neo4j_client import neo4j_client
from app.shared.schemas import ExtractionResult


class Neo4jRepo:
    """Repository for Neo4j operations."""
    
    @staticmethod
    async def write_extraction_result(result: ExtractionResult):
        async with neo4j_client.session() as session:
            tx = await session.begin_transaction()
            try:
                # 1. Equipment
                for e in result.equipment:
                    await tx.run("""
                    MERGE (n:Equipment {id: $id})
                    ON CREATE SET n.type = $type, n.location = $location, n.criticality = $criticality, 
                                  n.aliases = $aliases, n.source_doc_ids = [$doc_id]
                    ON MATCH SET n.aliases = [x IN n.aliases WHERE NOT x IN $aliases] + $aliases,
                                 n.source_doc_ids = [x IN n.source_doc_ids WHERE x <> $doc_id] + [$doc_id]
                    """, id=e.tag_id, type=e.type, location=e.location, criticality=e.criticality, 
                         aliases=e.aliases, doc_id=result.doc_id)
                
                # 2. Failure
                for f in result.failures:
                    await tx.run("""
                    MERGE (n:Failure {id: $id})
                    ON CREATE SET n.description = $desc, n.date = $date, n.severity = $severity, 
                                  n.source_doc_ids = [$doc_id]
                    ON MATCH SET n.source_doc_ids = [x IN n.source_doc_ids WHERE x <> $doc_id] + [$doc_id]
                    MERGE (e:Equipment {id: $eq_id})
                    MERGE (n)-[:AFFECTS]->(e)
                    """, id=f.failure_id, desc=f.description, date=f.date, severity=f.severity, 
                         eq_id=f.equipment_tag, doc_id=result.doc_id)
                
                # 3. Procedure
                for p in result.procedures:
                    await tx.run("""
                    MERGE (n:Procedure {id: $id})
                    ON CREATE SET n.title = $title, n.version = $version, n.governing_reg = $reg, 
                                  n.source_doc_ids = [$doc_id]
                    ON MATCH SET n.source_doc_ids = [x IN n.source_doc_ids WHERE x <> $doc_id] + [$doc_id]
                    """, id=p.procedure_id, title=p.title, version=p.version, reg=p.governing_reg, doc_id=result.doc_id)

                # 4. Person
                for p in result.personnel:
                    await tx.run("""
                    MERGE (n:Person {id: $id})
                    ON CREATE SET n.name = $name, n.role = $role, n.certification = $cert, 
                                  n.source_doc_ids = [$doc_id]
                    ON MATCH SET n.source_doc_ids = [x IN n.source_doc_ids WHERE x <> $doc_id] + [$doc_id]
                    """, id=p.person_id, name=p.name, role=p.role, cert=p.certification, doc_id=result.doc_id)

                # 5. Regulation
                for r in result.regulations:
                    await tx.run("""
                    MERGE (n:Regulation {id: $id})
                    ON CREATE SET n.source = $source, n.clause = $clause, 
                                  n.source_doc_ids = [$doc_id]
                    ON MATCH SET n.source_doc_ids = [x IN n.source_doc_ids WHERE x <> $doc_id] + [$doc_id]
                    """, id=r.reg_id, source=r.source, clause=r.clause, doc_id=result.doc_id)

                # 6. Inspection
                for i in result.inspections:
                    await tx.run("""
                    MERGE (n:Inspection {id: $id})
                    ON CREATE SET n.date = $date, n.result = $result, 
                                  n.source_doc_ids = [$doc_id]
                    ON MATCH SET n.source_doc_ids = [x IN n.source_doc_ids WHERE x <> $doc_id] + [$doc_id]
                    MERGE (e:Equipment {id: $eq_id})
                    MERGE (n)-[:INSPECTS]->(e)
                    """, id=i.inspection_id, date=i.date, result=i.result, eq_id=i.equipment_tag, doc_id=result.doc_id)
                    if i.inspector_ref:
                        await tx.run("""
                        MERGE (n:Inspection {id: $id})
                        MERGE (p:Person {id: $p_id})
                        MERGE (p)-[:PERFORMS]->(n)
                        """, id=i.inspection_id, p_id=i.inspector_ref)

                # 7. WorkOrder
                for w in result.work_orders:
                    await tx.run("""
                    MERGE (n:WorkOrder {id: $id})
                    ON CREATE SET n.date = $date, n.description = $desc, n.status = $status, 
                                  n.source_doc_ids = [$doc_id]
                    ON MATCH SET n.source_doc_ids = [x IN n.source_doc_ids WHERE x <> $doc_id] + [$doc_id]
                    """, id=w.wo_id, date=w.date, desc=w.description, status=w.status, doc_id=result.doc_id)

                # 8. Incident
                for i in result.incidents:
                    await tx.run("""
                    MERGE (n:Incident {id: $id})
                    ON CREATE SET n.date = $date, n.description = $desc, n.severity = $severity, 
                                  n.source_doc_ids = [$doc_id]
                    ON MATCH SET n.source_doc_ids = [x IN n.source_doc_ids WHERE x <> $doc_id] + [$doc_id]
                    """, id=i.incident_id, date=i.date, desc=i.description, severity=i.severity, doc_id=result.doc_id)

                # Relationships
                for rel in result.relationships:
                    await tx.run(f"""
                    MERGE (a:{rel.from_label} {{id: $from_id}})
                    MERGE (b:{rel.to_label} {{id: $to_id}})
                    MERGE (a)-[r:{rel.rel_type}]->(b)
                    ON CREATE SET r.source_doc_ids = [$doc_id]
                    ON MATCH SET r.source_doc_ids = [x IN r.source_doc_ids WHERE x <> $doc_id] + [$doc_id]
                    """, from_id=rel.from_id, to_id=rel.to_id, doc_id=result.doc_id)

                await tx.commit()
                log.info("neo4j.write_extraction_result.success", doc_id=result.doc_id)
            except Exception as e:
                await tx.rollback()
                log.error("neo4j.write_extraction_result.failed", error=str(e), doc_id=result.doc_id)
                raise

neo4j_repo = Neo4jRepo()
