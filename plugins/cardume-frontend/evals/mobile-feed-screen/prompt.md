---
name: mobile-feed-screen
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

I'm building a React Native (Expo) feed screen showing ~2,000 posts with images. Scrolling stutters on mid-range Android phones and the "like" button is hard to tap with one hand. Here's the screen:

```tsx
export function Feed({ posts }) {
  return (
    <ScrollView>
      {posts.map(p => (
        <View key={p.id} style={{ padding: 8 }}>
          <Image source={{ uri: p.imageUrl }} style={{ width: '100%', height: 300 }} />
          <Text>{p.caption}</Text>
          <TouchableOpacity onPress={() => like(p.id)} style={{ alignSelf: 'flex-end' }}>
            <Text style={{ fontSize: 10 }}>♥</Text>
          </TouchableOpacity>
        </View>
      ))}
    </ScrollView>
  );
}
```

What should I change?
