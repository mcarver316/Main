# PAPA Lab v4 — Security Assessment Plan and Report
**Document ID:** PAPA-SAR-001
**Version:** 1.0
**System:** PAPA Lab v4 (PAPALA-001)
**Assessment period:** 2026-06-01 through 2026-06-09
**Assessor:** CC (Developer) / Michael Carver (ISSO, acting SCA)
**Date:** 2026-06-10

---

## Part A — Security Assessment Plan

### A.1 Assessment scope

17 security controls from the NIST SP 800-53 Rev. 5 Moderate baseline, as documented
in SSPP Section 6. Controls span six families: AC, AU, CM, IA, SC, SI.

### A.2 Methodology

SP 800-53A Rev. 5 Determine-If (DI) assessment methodology. Each control objective
assessed using one or more of: examine (artifact review), interview (system owner),
test (live system verification). DI assessment blocks are embedded in SSPP Section 6
and serve as the primary assessment record.

### A.3 Independence note

ISSO and SCA roles are both held by Michael Carver. This is a known limitation of the
single-operator model, accepted by the AO and documented in SSPP Section 11.1.
Compensating control: Phase 1 and Phase 2 completion certificates were produced by CC
(Developer) independently of the ISSO, providing a second reviewer for all implemented
controls.

### A.4 Evidence sources

| Artifact | Role in assessment |
|---|---|
| Phase 1 Completion Certificate | Dependency baseline, CI/CD pipeline confirmation |
| Phase 2 Completion Certificate | Six Critical/High bug remediations, 51 tests passing |
| Phase 2 Final Validation Report | Live smoke test — all 8 PAPA scenarios intact |
| SDLC_NOTES.md | Intentional vs. genuine bug classification |
| ci.yml GitHub Actions runs #9–12 | Automated gate evidence, commit 95571777 (Phase 1/2) |
| ci.yml GitHub Actions run #22 | Phase 3 gate evidence — blocking security-scan-deps, secret-scan, SBOM all green; commit cb278c9 |
| requirements-pinned.txt | Component inventory baseline |
| live_test_results.txt (2026-06-10) | CC live test — auth enforcement, CORS, SC-08 IDOR |
| SC-08 live re-test (2026-06-10) | Alice (user B) queried TMC-100001 (owned by user A) via /api/chat — chatbot returned ticket content with no ownership check; IDOR teaching feature confirmed intact at Level 1 |

---

## Part B — Security Assessment Report

### B.1 Control assessment summary

| Control | Name | Result | Open findings |
|---|---|---|---|
| AC-2 | Account Management | Substantially Satisfied | AC-02j: no formal account review record |
| AC-3 | Access Enforcement | Satisfied | — |
| AC-17 | Remote Access | Not Applicable | — |
| AU-2 | Event Logging | Satisfied | — |
| AU-3 | Content of Audit Records | Partially Satisfied | AU-03d: user identity absent from logs (PM-01) |
| AU-9 | Protection of Audit Information | Partially Satisfied | AU-09b: no automated log failure alerting |
| CM-2 | Baseline Configuration | Satisfied | — |
| CM-3 | Configuration Change Control | Satisfied | — |
| CM-6 | Configuration Settings | Satisfied | — |
| CM-8 | System Component Inventory | Satisfied | — |
| IA-2 | Identification and Authentication | Partially Satisfied | IA-02b: no MFA for admin role |
| IA-5 | Authenticator Management | Partially Satisfied | IA-05b: no password complexity enforcement (PM-03) |
| SC-5 | Denial of Service Protection | Not Applicable | — |
| SC-8 | Transmission Confidentiality | Not Applicable | — |
| SC-28 | Protection of Information at Rest | Other Than Satisfied | SC-28a: FileVault not confirmed (PM-06) |
| SI-2 | Flaw Remediation | Satisfied | — |
| SI-3 | Malicious Code Protection | Substantially Satisfied | SI-03c: no formal false-positive process |
| SI-10 | Information Input Validation | Partially Satisfied | Intentional at Levels 1–2 per SSPP §4 |

### B.2 Open findings summary

7 DI objectives assessed Other Than Satisfied. All are tracked in SSPP POA&M (PM-01
through PM-06) or accepted as residual risk by the AO. No finding is assessed as HIGH
risk given the localhost-only, single-operator operational context.

### B.3 Overall risk determination

**LOW.** All Critical and High application-level findings were remediated in Phase 2.
Remaining open items are Medium or Low severity, consistent with SSPP Section 9.3.
The authorized teaching scenarios (SC-01 through SC-08) are correctly classified as
intentional features, not security findings.

### B.4 Assessor attestation

The undersigned attest that the assessment was conducted in accordance with SP 800-53A
Rev. 5 and that the findings above accurately represent the security posture of PAPA
Lab v4 at commit 95571777 as of 2026-06-10.

**Assessor (Developer/SCA):** CC
**Date:** 2026-06-10
**Signature:** _Mike Carver______________

**ISSO/AO Review:** Michael Carver
**Date:** _2026-06-09______________
**Signature:** __Mike Carver_____________
