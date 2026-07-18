"""
tests/unit/test_ontology.py
────────────────────────────
Unit tests for shared/ontology.py — ensures all enum members are
consistent and expected values exist. No DB or LLM connection required.
"""
import pytest

from app.shared.ontology import (
    AgentType,
    ComplianceRuleId,
    Criticality,
    DocType,
    NodeLabel,
    Prop,
    RelType,
    Severity,
)


class TestNodeLabel:
    def test_all_expected_labels_present(self):
        expected = {
            "Equipment", "Failure", "Procedure", "Person",
            "Regulation", "Inspection", "WorkOrder", "Incident",
        }
        actual = {label.value for label in NodeLabel}
        assert expected == actual, f"Missing labels: {expected - actual}"

    def test_str_enum_behaviour(self):
        # Use .value explicitly — portable across all Python versions
        assert NodeLabel.EQUIPMENT.value == "Equipment"
        assert f"MATCH (n:{NodeLabel.EQUIPMENT.value})" == "MATCH (n:Equipment)"


class TestRelType:
    def test_all_expected_rel_types_present(self):
        expected = {
            "HAS_FAILURE", "RESOLVED_BY", "PERFORMED_BY",
            "GOVERNED_BY", "INSPECTED_ON", "REFERENCES",
            "SIMILAR_FAILURE_MODE",
        }
        actual = {r.value for r in RelType}
        assert expected == actual, f"Missing rel types: {expected - actual}"


class TestComplianceRuleId:
    def test_five_rules_defined(self):
        assert len(ComplianceRuleId) == 5

    def test_rule_ids_match_pattern(self):
        for rule in ComplianceRuleId:
            assert rule.value.startswith("CR-"), f"{rule} does not start with CR-"


class TestDocType:
    def test_pid_doc_type_exists(self):
        assert DocType.PID.value == "pid"

    def test_all_doc_types_are_lowercase(self):
        for dt in DocType:
            assert dt.value == dt.value.lower(), f"{dt.value!r} is not lowercase"


class TestSeverityAndCriticality:
    def test_severity_levels(self):
        assert Severity.LOW.value == "Low"
        assert Severity.CRITICAL.value == "Critical"

    def test_criticality_matches_severity(self):
        # Both should have identical string values
        sev_values = {s.value for s in Severity}
        crit_values = {c.value for c in Criticality}
        assert sev_values == crit_values


class TestAgentType:
    def test_three_agent_types(self):
        assert len(AgentType) == 3
        assert AgentType.RCA.value == "rca"
