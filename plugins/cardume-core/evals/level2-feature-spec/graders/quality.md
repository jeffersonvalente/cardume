---
type: llm
focus: last_message
weight: 2
---

PASS if the reply classifies this as a feature (level 2) and, before any implementation code, either asks clarifying questions that change the design (rate source and timing, rounding, historical rates for past invoices, which date's rate applies, reporting period) or presents testable requirements with acceptance criteria (EARS-style or equivalent), and names a decision worth an ADR (e.g. exchange-rate source or storing original vs converted amounts).
FAIL if it jumps straight into writing implementation code or gives a generic plan without acceptance criteria.
