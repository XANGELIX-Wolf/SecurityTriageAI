"""Mock triage decisions for offline/free demo mode.

These represent realistic AI triage output grounded in the expert baselines.
Used when MOCK=true or --mock flag is passed — zero API calls, zero cost.

Alignment with expert baselines: 4/5 exact matches (80% accuracy).
"""

MOCK_DECISIONS: dict[str, dict] = {
    "ALERT-2024-001": {
        "alert_id": "ALERT-2024-001",
        "severity": "CRITICAL",
        "confidence": 0.94,
        "mitre_techniques": ["T1566.001", "T1059.001"],
        "kill_chain_phase": "exploitation",
        "reasoning": (
            "PowerShell.exe launched with -EncodedCommand from WINWORD.EXE is a high-confidence "
            "indicator of a phishing document executing a malicious payload. This process chain "
            "(Office app spawning encoded PowerShell) is a hallmark of document-based malware delivery. "
            "The Finance department asset (WKSTN-FIN-042) represents a high-value target with access "
            "to sensitive financial data. The long command-line length (4,823 chars) strongly suggests "
            "a full encoded payload, not a benign script. Immediate containment is warranted before "
            "further lateral movement or data exfiltration can occur."
        ),
        "recommended_actions": [
            "Isolate WKSTN-FIN-042 from the network immediately",
            "Collect memory dump and process tree before remediation",
            "Decode and analyze the Base64 payload",
            "Review email logs for jsmith@corp.local for phishing source",
            "Scan all Finance department endpoints for similar activity",
        ],
        "escalation_required": True,
        "processing_time_ms": 4821,
    },
    "ALERT-2024-002": {
        "alert_id": "ALERT-2024-002",
        "severity": "CRITICAL",
        "confidence": 0.97,
        "mitre_techniques": ["T1048"],
        "kill_chain_phase": "actions_on_objectives",
        "reasoning": (
            "4.2GB outbound transfer from a production database server (DB-PROD-01) to an unknown "
            "external IP during non-business hours is a textbook data exfiltration pattern. The "
            "transfer volume is 14x the established daily egress baseline (0.3GB). The destination "
            "IP (185.234.72.19) is not in any approved external endpoint list. The server holds "
            "data classified as confidential. Combined factors — volume anomaly, timing, unknown "
            "destination, critical asset — constitute near-certain active exfiltration. "
            "Immediate isolation required to prevent further data loss."
        ),
        "recommended_actions": [
            "Block outbound traffic to 185.234.72.19 at the firewall immediately",
            "Isolate DB-PROD-01 from the network",
            "Capture and preserve network logs for forensic analysis",
            "Initiate data breach assessment and legal/compliance notification process",
            "Review DB-PROD-01 access logs for unauthorized queries or credential use",
        ],
        "escalation_required": True,
        "processing_time_ms": 3956,
    },
    "ALERT-2024-003": {
        "alert_id": "ALERT-2024-003",
        "severity": "CRITICAL",
        "confidence": 0.96,
        "mitre_techniques": ["T1110.001", "T1078"],
        "kill_chain_phase": "exploitation",
        "reasoning": (
            "47 failed login attempts followed by a successful authentication for a privileged "
            "admin account (admin@contoso.com) from an IP geolocated to Russia — inconsistent with "
            "the user's normal US-TX activity — is confirmed credential brute-force with successful "
            "account compromise. The absence of MFA challenge on successful auth suggests MFA was "
            "bypassed or not enforced for this account. The target account is privileged (IT Admin), "
            "significantly amplifying blast radius. This requires immediate credential revocation "
            "and active session termination before the attacker establishes persistence."
        ),
        "recommended_actions": [
            "Revoke all active sessions for admin@contoso.com immediately",
            "Reset credentials and enforce MFA re-enrollment",
            "Audit all actions taken during and after the successful login",
            "Block IP 91.234.56.78 at perimeter",
            "Review MFA policy enforcement for privileged accounts",
            "Check for new accounts, permission changes, or persistence mechanisms created",
        ],
        "escalation_required": True,
        "processing_time_ms": 5102,
    },
    "ALERT-2024-004": {
        "alert_id": "ALERT-2024-004",
        "severity": "HIGH",
        "confidence": 0.88,
        "mitre_techniques": ["T1566.001"],
        "kill_chain_phase": "delivery",
        "reasoning": (
            "A macro-enabled Excel attachment (Invoice_Dec2024.xlsm) was delivered to 3 Accounting "
            "users from a domain registered only 48 hours ago — a strong indicator of a purpose-built "
            "phishing domain. The sender domain (acc0unting-services.com) uses character substitution "
            "to impersonate a legitimate business. Threat intel confirms the attachment hash matches "
            "a known active campaign (CAMP-INVOICE-DEC). The attack is at the delivery stage — "
            "macros have not yet been executed based on available telemetry. Containment is still "
            "possible without host compromise if acted on immediately."
        ),
        "recommended_actions": [
            "Quarantine the attachment across all 3 recipient mailboxes",
            "Block sender domain acc0unting-services.com at email gateway",
            "Alert all 3 recipients: do not open the attachment",
            "Scan for delivery of Invoice_Dec2024.xlsm to any other mailboxes",
            "Add attachment hash to EDR blocklist",
        ],
        "escalation_required": False,
        "processing_time_ms": 3244,
    },
    "ALERT-2024-005": {
        "alert_id": "ALERT-2024-005",
        "severity": "CRITICAL",
        "confidence": 0.93,
        "mitre_techniques": ["T1078.004"],
        "kill_chain_phase": "exploitation",
        "reasoning": (
            "AssumeRole API call for 'ProductionDBAdmin' — a role granting full RDS access plus "
            "S3 and Secrets Manager read — from an IP not associated with any known corporate VPN "
            "or egress point is high-confidence unauthorized access. The role's permission scope "
            "(production databases, secrets) represents maximum blast radius in this AWS account. "
            "The user-agent (aws-sdk-python) suggests programmatic access, indicating likely "
            "API key compromise rather than console phishing. Immediate role revocation is required "
            "before the attacker can exfiltrate database contents or secrets."
        ),
        "recommended_actions": [
            "Revoke the ProductionDBAdmin role's trust policy immediately",
            "Rotate all IAM access keys that could have been used to assume this role",
            "Audit CloudTrail for all API calls made after the AssumeRole event",
            "Check for data access in RDS query logs and S3 access logs",
            "Rotate all secrets in Secrets Manager accessible by this role",
            "Review IAM role trust policies across the account for similar misconfigurations",
        ],
        "escalation_required": True,
        "processing_time_ms": 4388,
    },
}
