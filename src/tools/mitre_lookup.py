"""MITRE ATT&CK Lookup Tool - Maps indicators to ATT&CK techniques."""

from typing import Type
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

ATTACK_TECHNIQUES = {
    "T1566": {"name": "Phishing", "tactic": "Initial Access", "kill_chain": "delivery"},
    "T1566.001": {"name": "Spearphishing Attachment", "tactic": "Initial Access", "kill_chain": "delivery"},
    "T1566.002": {"name": "Spearphishing Link", "tactic": "Initial Access", "kill_chain": "delivery"},
    "T1059": {"name": "Command and Scripting Interpreter", "tactic": "Execution", "kill_chain": "exploitation"},
    "T1059.001": {"name": "PowerShell", "tactic": "Execution", "kill_chain": "exploitation"},
    "T1059.003": {"name": "Windows Command Shell", "tactic": "Execution", "kill_chain": "exploitation"},
    "T1078": {"name": "Valid Accounts", "tactic": "Persistence", "kill_chain": "exploitation"},
    "T1078.004": {"name": "Cloud Accounts", "tactic": "Persistence", "kill_chain": "exploitation"},
    "T1110": {"name": "Brute Force", "tactic": "Credential Access", "kill_chain": "exploitation"},
    "T1110.001": {"name": "Password Guessing", "tactic": "Credential Access", "kill_chain": "exploitation"},
    "T1110.003": {"name": "Password Spraying", "tactic": "Credential Access", "kill_chain": "exploitation"},
    "T1486": {"name": "Data Encrypted for Impact", "tactic": "Impact", "kill_chain": "actions_on_objectives"},
    "T1071": {"name": "Application Layer Protocol", "tactic": "Command and Control", "kill_chain": "command_and_control"},
    "T1071.001": {"name": "Web Protocols", "tactic": "Command and Control", "kill_chain": "command_and_control"},
    "T1048": {"name": "Exfiltration Over Alternative Protocol", "tactic": "Exfiltration", "kill_chain": "actions_on_objectives"},
    "T1027": {"name": "Obfuscated Files or Information", "tactic": "Defense Evasion", "kill_chain": "exploitation"},
    "T1053": {"name": "Scheduled Task/Job", "tactic": "Persistence", "kill_chain": "installation"},
    "T1547": {"name": "Boot or Logon Autostart Execution", "tactic": "Persistence", "kill_chain": "installation"},
    "T1070": {"name": "Indicator Removal", "tactic": "Defense Evasion", "kill_chain": "actions_on_objectives"},
    "T1562": {"name": "Impair Defenses", "tactic": "Defense Evasion", "kill_chain": "exploitation"},
}


class MitreLookupInput(BaseModel):
    query: str = Field(description="Indicator, behavior, or technique name/ID to look up")


class MitreLookupTool(BaseTool):
    name: str = "mitre_attack_lookup"
    description: str = (
        "Look up MITRE ATT&CK techniques by ID or keyword. "
        "Maps observed behaviors to known attack techniques and kill chain phase."
    )
    args_schema: Type[BaseModel] = MitreLookupInput

    def _run(self, query: str) -> str:
        query_lower = query.lower()
        matches = [
            f"- {tid}: {info['name']} (Tactic: {info['tactic']}, Kill Chain: {info['kill_chain']})"
            for tid, info in ATTACK_TECHNIQUES.items()
            if query_lower in tid.lower() or query_lower in info["name"].lower() or query_lower in info["tactic"].lower()
        ]
        if matches:
            return f"Found {len(matches)} matching techniques:\n" + "\n".join(matches)
        return f"No exact match for '{query}'. Try keywords like 'phishing', 'brute force', 'exfiltration'."
