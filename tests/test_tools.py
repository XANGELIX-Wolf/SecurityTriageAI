"""Unit tests for agent tools."""

import json
import pytest
from src.tools.mitre_lookup import MitreLookupTool
from src.tools.alert_enrichment import AlertEnrichmentTool
from src.tools.severity_scorer import SeverityScorerTool


class TestMitreLookupTool:
    def setup_method(self):
        self.tool = MitreLookupTool()

    def test_lookup_by_technique_id(self):
        result = self.tool._run("T1566")
        assert "Phishing" in result

    def test_lookup_by_name(self):
        result = self.tool._run("brute force")
        assert "T1110" in result

    def test_lookup_by_tactic(self):
        result = self.tool._run("exfiltration")
        assert "T1048" in result

    def test_lookup_no_match(self):
        result = self.tool._run("xyznonexistent")
        assert "No exact match" in result

    def test_lookup_powershell(self):
        result = self.tool._run("PowerShell")
        assert "T1059.001" in result


class TestAlertEnrichmentTool:
    def setup_method(self):
        self.tool = AlertEnrichmentTool()

    def test_enrich_ip(self):
        result = json.loads(self.tool._run("192.168.1.1", "ip"))
        assert "reputation_score" in result

    def test_enrich_domain(self):
        result = json.loads(self.tool._run("evil.example.com", "domain"))
        assert result["known_malicious"] is True

    def test_enrich_hash(self):
        result = json.loads(self.tool._run("abc123", "hash"))
        assert "malware_family" in result

    def test_enrich_user(self):
        result = json.loads(self.tool._run("jsmith", "user"))
        assert "risk_score" in result


class TestSeverityScorerTool:
    def setup_method(self):
        self.tool = SeverityScorerTool()

    def test_critical_ransomware(self):
        result = json.loads(self.tool._run("ransomware", "critical", 0.95, "actions_on_objectives"))
        assert result["severity"] == "CRITICAL"

    def test_low_anomaly(self):
        result = json.loads(self.tool._run("anomaly", "low", 0.3, "recon"))
        assert result["severity"] in ["LOW", "INFORMATIONAL"]

    def test_confidence_increases_score(self):
        low = json.loads(self.tool._run("malware", "high", 0.3, "exploitation"))
        high = json.loads(self.tool._run("malware", "high", 0.95, "exploitation"))
        assert high["normalized_score"] > low["normalized_score"]
