"""
services/agents/rca_service.py
──────────────────────────────
Root Cause Analysis (RCA) Agent.
Traverses the graph for a given equipment or failure and generates a report.
"""
import asyncio

from google import genai

from app.infrastructure.logger import log
from app.infrastructure.neo4j_client import neo4j_client
from app.providers.gemini_provider import GeminiProvider


class RCAService:
    def __init__(self):
        self.provider = GeminiProvider()

    async def generate_rca(self, equipment_id: str) -> dict:
        log.info("rca_service.started", equipment_id=equipment_id)
        
        context_data = []
        async with neo4j_client.session() as session:
            cypher = """
            MATCH (e:Equipment {id: $eq_id})-[r*1..2]-(m)
            RETURN labels(m)[0] AS node_type, m, type(r[-1]) AS rel_type
            LIMIT 100
            """
            result = await session.run(cypher, eq_id=equipment_id)
            records = await result.data()
            
            for record in records:
                node_type = record['node_type']
                m = dict(record['m'])
                context_data.append(f"{node_type}: {m}")
                
        if not context_data:
            return {"error": f"No data found for equipment {equipment_id}"}
            
        context_formatted = "\n".join(context_data)
        prompt = f"""
        You are an expert Root Cause Analysis (RCA) AI Agent for industrial equipment.
        Perform an RCA for Equipment ID: {equipment_id}.
        
        Analyze the following graph database records containing its failures, inspections, incidents, and procedures:
        {context_formatted}
        
        Write a highly structured RCA report including:
        1. Executive Summary
        2. Timeline of Events (Chronological if dates available)
        3. Root Cause Hypothesis
        4. Contributing Factors
        5. Corrective Actions (Recommended)
        """
        
        async def _call_api_with_retry():
            models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-pro"]
            for outer in range(2):
                for m in models:
                    for attempt in range(2):
                        try:
                            return await asyncio.to_thread(
                                self.provider.client.models.generate_content,
                                model=m,
                                contents=prompt,
                                config=genai.types.GenerateContentConfig(temperature=0.3)
                            )
                        except Exception as e:
                            err_msg = str(e)
                            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                                await asyncio.sleep(2.0)
                            else:
                                raise e
                await asyncio.sleep(4.0)
            return None

        try:
            response = await _call_api_with_retry()
            if response and response.text:
                report = response.text.strip()
            else:
                report = (
                    f"# Root Cause Analysis Report for Equipment: {equipment_id}\n\n"
                    f"## 1. Executive Summary\n"
                    f"Graph RAG analysis completed for equipment `{equipment_id}` with {len(context_data)} evidence records.\n\n"
                    f"## 2. Graph Evidence & Failure History\n" +
                    "\n".join(f"- {c}" for c in context_data[:20]) +
                    f"\n\n## 3. Recommended Corrective Actions\n"
                    f"- Perform technical inspection on `{equipment_id}` and resolve open failure logs."
                )
        except Exception as exc:
            log.warning("rca_service.llm_fallback", error=str(exc))
            report = (
                f"# Root Cause Analysis Report for Equipment: {equipment_id}\n\n"
                f"## 1. Executive Summary\n"
                f"Graph analysis completed for equipment `{equipment_id}` ({len(context_data)} graph records).\n\n"
                f"## 2. Graph Evidence\n" +
                "\n".join(f"- {c}" for c in context_data[:20]) +
                f"\n\n## 3. Immediate Actions\n"
                f"- Review active work orders and inspection protocols for `{equipment_id}`."
            )
        
        log.info("rca_service.completed", equipment_id=equipment_id)
        
        return {
            "equipment_id": equipment_id,
            "report": report,
            "evidence_count": len(context_data)
        }

rca_service = RCAService()
