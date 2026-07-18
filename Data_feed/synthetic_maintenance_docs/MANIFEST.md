# Synthetic Document Set — Manifest

**Total documents: 54** (within the 45–55 target range)

| Type | Count | Folder |
|---|---|---|
| Maintenance logs | 15 | `maintenance_logs/` |
| Work orders | 11 | `work_orders/` |
| Inspection reports | 9 | `inspection_reports/` |
| SOPs / procedures | 8 | `sops/` |
| Incident / near-miss reports | 7 | `incident_reports/` |
| Deliberately corrupted files | 4 | `corrupted/` |

Facility used throughout: **Cedar Point Processing Facility**.

## Equipment coverage (8 items)

| Equipment | Type | Role in test design | Docs it appears in |
|---|---|---|---|
| **P-104** | Centrifugal pump, Unit 3 | RCA pattern #1: 3× mechanical seal failure, root cause = seal material not rated for elevated process temp | 2 inspections, 3 logs, 3 work orders, 1 incident |
| **CV-220** | Control valve, Unit 2 | RCA pattern #2: 3× positioner failure after rain, root cause = NEMA 3R enclosure inadequate for outdoor exposure | 2 inspections, 3 logs, 3 work orders, 1 incident |
| **CB-15** | Conveyor belt drive 15 | RCA pattern #3: 3× drive motor bearing failure, root cause = lubrication interval mismatched to duty cycle | 2 inspections, 3 logs, 3 work orders, 1 incident |
| **AC-12** | Air compressor 12 | Lessons-learned pair (A): bearing overheat from wrong grease grade | 1 inspection, 1 log, 1 work order, 1 incident + shared lessons-learned report |
| **FN-33** | Cooling tower fan 33 | Lessons-learned pair (B): same root cause as AC-12, different equipment class — tests cross-equipment pattern detection | 1 log, 1 work order, 1 incident + shared lessons-learned report |
| **TK-301** | Storage tank 301 | Seeded compliance issue: annual inspection overdue since 2025-01-15 | 1 inspection (last valid, now overdue), 1 log, 1 incident |
| **GEN-04** | Emergency diesel generator 4 | Seeded compliance issue: load-bank test passed but EHS certification sign-off missing | 1 inspection (pass, sign-off pending), 1 log |
| **MTR-501** | General purpose motor 501 | Clean/compliant control item — confirms the compliance agent doesn't flag everything | 2 logs (both "satisfactory") |

`INC-2025-025` is the explicit lessons-learned document tying AC-12 and FN-33 together by shared root cause — this is the key artifact for testing cross-equipment pattern detection.

## Entity resolution stress-test (deliberate naming variance)

**Equipment** (3 items varied on purpose):
- P-104 → `P-104`, `Pump 104`, `P104`
- CV-220 → `CV-220`, `Control Valve 220`, `CV220`
- CB-15 → `CB-15`, `Conveyor 15`, `Belt Drive CB-15`

**Personnel** (3 people varied on purpose):
- James Whitfield → `James Whitfield`, `J. Whitfield`, `Jim Whitfield` (in narrative text only)
- Sarah Chen → `Sarah Chen`, `S. Chen`
- Robert Alvarez → `Robert Alvarez`, `R. Alvarez`, `Bobby Alvarez` (in narrative text only)

Other personnel (Maria Torres, David Kim, Lisa Nguyen, Tom Baxter) are referenced consistently with no variation, so you have a control group for entity resolution scoring.

## Timeline consistency

Each RCA equipment item follows a chronologically sane sequence across document types: **inspection → failure (maintenance log) → work order → next inspection**, repeated across three occurrences, with the final occurrence resolving the root cause:

- P-104: IR (2025-03) → ML/WO (2025-04-12) → ML/WO (2025-09-18) → IR (2025-12) → ML/WO/INC (2026-03-05, root cause fixed)
- CV-220: IR (2025-02) → ML/WO/INC (2025-05-20) → ML/WO/INC (2025-11-14) → IR (2026-05) → ML/WO (2026-06-09, temp fix, permanent fix pending)
- CB-15: IR (2025-01) → ML/WO (2025-04-25) → ML/WO/INC (2025-10-08) → IR (2026-02, flags early wear) → ML/WO (2026-05-14, root cause fixed)
- AC-12 / FN-33: IR AC-12 (2025-01) → ML/WO/INC AC-12 (2025-06-11) → ML/WO/INC FN-33 (2025-08-22) → lessons-learned report (2025-12-05)
- TK-301: IR (2024-01-15, passed, next due 2025-01-15) → ML (2025-08-30, flags overdue) → INC (2026-02-10, near-miss possibly tied to overdue inspection)
- GEN-04: ML (2026-05-02, monthly test ok) → IR (2026-06-16, load test passed, sign-off pending)

## Held-back set for live re-ingestion testing

To demonstrate the "continuously updated graph" behavior, ingest everything **except** the 5 files below first, run your benchmark queries, then ingest these and re-run to confirm the graph and answers update (new failure occurrence added to P-104 and CV-220 history, GEN-04 compliance status resolved to fully pass, etc.):

1. `maintenance_logs/ML-CV220-2026-06-09.txt`
2. `work_orders/WO-10312.txt`
3. `inspection_reports/IR-GEN04-2026-06.txt`
4. `maintenance_logs/ML-CB15-2026-05-14.txt`
5. `work_orders/WO-10305.txt`

These are the five most recent documents chronologically (May–June 2026) and represent: a third recurring failure being added to an existing RCA pattern (CV-220), a root-cause resolution being added to another (CB-15), and a compliance finding appearing for the first time (GEN-04).

## GOVERNED_BY links (SOPs referenced by equipment/work)

- P-104 → SOP-MP-014 (seal replacement)
- CV-220 → SOP-CV-022 (positioner calibration)
- CB-15 → SOP-CB-005 (lubrication)
- TK-301 → SOP-TK-011 (tank inspection)
- GEN-04 → SOP-GEN-030 (generator testing/certification)
- AC-12, FN-33, CB-15, MTR-501 → SOP-AC-018 (lubrication standard, referenced across multiple equipment)
- All work orders → SOP-LOTO-002 (lockout/tagout, referenced universally)
- All incident reports → SOP-INC-001 (incident reporting procedure)
