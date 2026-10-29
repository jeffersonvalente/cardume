---
title: Use Item Types for Heterogeneous Lists
impact: HIGH
impactDescription: efficient recycling, less layout thrashing
tags: list, performance, recycling, heterogeneous, LegendList
---

## Use Item Types for Heterogeneous Lists

When a list has different item layouts (messages, images, headers, etc.), use a
`type` field on each item and provide `getItemType` to the list. This puts items
into separate recycling pools so a message component never gets recycled into an
image component.

**Incorrect (single component with conditionals):**

```tsx
type Item = { id: string; text?: string; imageUrl?: string; isHeader?: boolean }

function ListItem({ item }: { item: Item }) {
  if (item.isHeader) {
    return <HeaderItem title={item.text} />
  }
  if (item.imageUrl) {
    return <ImageItem url={item.imageUrl} />
  }
  return <MessageItem text={item.text} />
}

function Feed({ items }: { items: Item[] }) {
  return (
    <LegendList
      data={items}
      renderItem={({ item }) => <ListItem item={item} />}
      recycleItems
    />
  )
}
```

**Correct (typed items with separate components):**

```tsx
type HeaderItem = { id: string; type: 'header'; title: string }
type MessageItem = { id: string; type: 'message'; text: string }
type ImageItem = { id: string; type: 'image'; url: string }
type FeedItem = HeaderItem | MessageItem | ImageItem

function Feed({ items }: { items: FeedItem[] }) {
  return (
    <LegendList
      data={items}
      keyExtractor={(item) => item.id}
      getItemType={(item) => item.type}
      renderItem={({ item }) => {
        switch (item.type) {
          case 'header':
            return <SectionHeader title={item.title} />
          case 'message':
            return <MessageRow text={item.text} />
          case 'image':
            return <ImageRow url={item.url} />
        }
      }}
      recycleItems
    />
  )
}
```

**Why this matters:**

- **Recycling efficiency**: Items with the same type share a recycling pool
- **No layout thrashing**: A header never recycles into an image cell
- **Type safety**: TypeScript can narrow the item type in each branch
- **Size hints**: LegendList v3 removed `getEstimatedItemSize`; dynamic rows need
  no estimate, and `getFixedItemSize` (with `itemType`) covers exactly-known sizes

```tsx
<LegendList
  data={items}
  keyExtractor={(item) => item.id}
  getItemType={(item) => item.type}
  // only for sizes known exactly; return undefined to measure (LegendList v3)
  getFixedItemSize={(item, index, itemType) =>
    itemType === 'header' ? 48 : undefined
  }
  renderItem={({ item }) => {
    /* ... */
  }}
  recycleItems
/>
```

Reference:
[LegendList v3 docs](https://legendapp.com/open-source/list/v3/llms-full.md)
(`getItemType`, `getFixedItemSize`)
