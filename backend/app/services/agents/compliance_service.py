"""
services/agents/compliance_service.py
─────────────────────────────────────
Compliance Agent.
Runs deterministic Cypher queries to audit graph data against compliance rules.
"""
from app.infrastructure.logger import log
from app.infrastructure.neo4j_client import neo4j_client


class ComplianceService:
    async def run_audit(self) -> dict:
        log.info("compliance_service.audit.started")
        results = {}
        
        async with neo4j_client.session() as session:
            cypher_1 = """
            MATCH (e:Equipment {criticality: 'High'})
            OPTIONAL MATCH (e)<-[:INSPECTS]-(i:Inspection)
            WHERE i.date >= date() - duration({days: 90})
            WITH e, collect(i) AS inspections
            WHERE size(inspections) = 0
            RETURN e.id AS equipment_id, "Missing recent inspection" AS gap
            """
            res_1 = await session.run(cypher_1)
            results["rule_1_critical_inspections"] = await res_1.data()

            cypher_2 = """
            MATCH (w:WorkOrder)-[:USES]->(p:Procedure)
            WHERE p.title CONTAINS 'LOTO' OR p.title CONTAINS 'Lockout'
            OPTIONAL MATCH (w)<-[:PERFORMS]-(person:Person)
            WHERE person.certification CONTAINS 'LOTO'
            WITH w, collect(person) AS certified_workers
            WHERE size(certified_workers) = 0
            RETURN w.id AS work_order_id, "LOTO procedure performed without certified personnel" AS gap
            """
            res_2 = await session.run(cypher_2)
            results["rule_2_loto_certification"] = await res_2.data()

            cypher_3 = """
            MATCH (f:Failure)
            OPTIONAL MATCH (f)<-[:RESOLVES]-(w:WorkOrder {status: 'Completed'})
            WITH f, collect(w) AS resolutions
            WHERE size(resolutions) = 0
            RETURN f.id AS failure_id, "Failure not resolved by a completed work order" AS gap
            """
            res_3 = await session.run(cypher_3)
            results["rule_3_failure_resolution"] = await res_3.data()

            cypher_4 = """
            MATCH (e:Equipment)-[:GOVERNED_BY]->(r:Regulation)
            OPTIONAL MATCH (e)-[:HAS_PROCEDURE]->(p:Procedure)
            WITH e, r, collect(p) AS procedures
            WHERE size(procedures) = 0
            RETURN e.id AS equipment_id, r.id AS regulation_id, "Regulated equipment missing procedure" AS gap
            """
            res_4 = await session.run(cypher_4)
            results["rule_4_regulated_procedures"] = await res_4.data()

            cypher_5 = """
            MATCH (i:Incident)
            OPTIONAL MATCH (i)<-[:ADDRESSES]-(w:WorkOrder {status: 'Completed'})
            WITH i, collect(w) AS addresses
            WHERE size(addresses) = 0
            RETURN i.id AS incident_id, "Incident has no completed corrective action" AS gap
            """
            res_5 = await session.run(cypher_5)
            results["rule_5_incident_closure"] = await res_5.data()

        total_gaps = sum(len(gaps) for gaps in results.values())
        log.info("compliance_service.audit.completed", total_gaps=total_gaps)
        
        return {
            "status": "passed" if total_gaps == 0 else "failed",
            "total_gaps": total_gaps,
            "details": results
        }

compliance_service = ComplianceService()
