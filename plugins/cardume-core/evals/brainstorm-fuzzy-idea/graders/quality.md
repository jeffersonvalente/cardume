---
type: llm
focus: last_message
weight: 2
---

PASS if, before proposing any implementation, stack or code, the answer asks focused clarifying questions covering at least three of: who the users are and the core problem (lending tools vs. giving away vs. selling), scope of a first version/MVP, trust and safety (identity, deposits, damage, no-shows), platform (web vs. mobile), and constraints (budget, timeline, solo dev). It may offer a few options with trade-offs, but must end by waiting for the user's answers.
FAIL if it immediately picks a tech stack, scaffolds code or a full feature list without asking anything, or asks only one generic question like "can you tell me more?".
