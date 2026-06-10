# PAPA Lab v4 — STIG/SCAP Tailoring Decision
**Document ID:** PAPA-STIG-TD-001
**Version:** 1.0
**Date:** 2026-06-10
**Author:** CC (Developer), Agile Armory
**AO Review:** Michael Carver
**Status:** APPROVED — see signature below

---

## 1. Scope

This document records the formal STIG/SCAP tailoring decision for PAPA Lab v4 (PAPALA-001)
per SSDLC-DSO-001 v1.1 §10 and §4.3. STIG/SRG compliance requirements may be tailored
with documented justification and AO acceptance.

## 2. System boundary

PAPA Lab v4 operates exclusively on the loopback interface (127.0.0.1:5001) of a single
operator's macOS workstation. It has no external network connectivity, no DoD network
connection, no FCI or CUI, and no multi-user deployment. Boundary is documented in
SSPP Section 3.

## 3. STIG baselines evaluated

| Component | Applicable STIG/SRG | Decision | Rationale |
|---|---|---|---|
| macOS host | DISA macOS 14 Sonoma STIG V1R1 | Partial tailoring | See §4.1 |
| Flask application | DISA Application SRG V3R2 | Tailored out | See §4.2 |
| Python 3.11 runtime | None | Not applicable | No DISA baseline exists |
| SQLite | None | Not applicable | No DISA baseline exists |
| ChromaDB v1.5.9 | None | Not applicable | No DISA baseline exists |
| Ollama | None | Not applicable | No DISA baseline exists |

## 4. Tailoring rationale

### 4.1 macOS host — partial tailoring

Full macOS STIG compliance is not required. The following CAT I controls are satisfied by
macOS built-in security mechanisms:

- **Disk encryption:** macOS FileVault (AES-256-XTS) — partially satisfies STIG
  V-252526 encryption at rest requirement
- **Malware protection:** XProtect, MRT, Gatekeeper — satisfies STIG V-252508
- **Host-based firewall:** macOS Application Firewall — satisfies STIG V-252527

Remaining CAT I findings are accepted as residual risk because: (a) no DoD or external
network connectivity exists; (b) the system is physically controlled by a single
authorized operator; (c) the system processes no classified, CUI, or sensitive
production data.

### 4.2 Application SRG — tailored out

The DISA Application SRG applies to applications deployed on DoD networks or processing
CUI/FCI. PAPA Lab v4 is a localhost-only security training tool processing no sensitive
data with no external network exposure. The Application SRG is formally tailored out.

Compensating controls in effect:

- Network isolation: localhost only; external access is an ATO condition violation per SSPP §11.1
- Authentication enforced on all admin endpoints (SSPP §6.2, AC-3)
- Input validation active at security Levels 3–5 (SSPP §4.2)
- Session integrity maintained via persisted SECRET_KEY (Phase 2 fix C-1, commit 95571777)
- Dependency scanning on every CI/CD build (pip-audit, safety, bandit)

## 5. Risk acceptance

Applying full STIG compliance to a localhost-only, single-operator AI security training
system provides no commensurate security benefit and imposes disproportionate operational
burden. Residual risk is assessed as LOW, consistent with SSPP Section 9.3.

## 6. AO acceptance

By signing below, the Authorizing Official formally accepts the tailoring decisions in
this document and acknowledges the residual risk for PAPA Lab v4.

**Authorizing Official:** Michael Carver
**Organization:** Agile Armory (Mike Carver Services LLC)
**Date:** __2026-06-09_____________
**Signature:** __Mike Carver_____________
