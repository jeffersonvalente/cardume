---
type: llm
focus: last_message
weight: 2
---

PASS if it replaces ScrollView+map with a virtualized list (FlatList/FlashList) with a memoized item component, stable keyExtractor and sensible windowing props or getItemLayout (FlatList) or FlashList v2 (no size estimate needed); addresses image cost (sized/cached images, e.g. expo-image, thumbnails instead of full-size); fixes the like target to meet platform minimums (~44pt iOS / 48dp Android, via size or hitSlop) with an accessibilityLabel/role; and considers thumb-zone placement. It should also suggest measuring (e.g. dev perf monitor / release build profiling) rather than only guessing.
FAIL if it keeps ScrollView, or ignores the touch-target problem.
