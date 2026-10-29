---
type: llm
focus: last_message
weight: 2
---

PASS if it starts by telling the user to measure (React DevTools Profiler and/or the browser Performance panel, INP) to confirm where time goes, then identifies the concrete causes in the code: `key={Math.random()}` forcing every row to remount, JSON.stringify over 8000 rows on every keystroke, and rendering all rows. Fixes must include stable keys (r.id), memoizing/precomputing the search index (useMemo) and/or deferring the filter (useDeferredValue/debounce), list virtualization, and React.memo on Row with a stable callback. It should say to re-measure after changes.
FAIL if it misses the Math.random() key problem, or recommends optimizations with no mention of profiling/measuring.
