---
name: perf-slow-react-list
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

Our React dashboard page got slow: typing in the search box lags about half a second per keystroke. Users say the whole page feels sluggish. Code:

```tsx
function Dashboard({ rows }) { // rows.length ≈ 8000
  const [q, setQ] = useState('');
  const filtered = rows.filter(r => JSON.stringify(r).toLowerCase().includes(q.toLowerCase()));
  return (
    <>
      <input value={q} onChange={e => setQ(e.target.value)} />
      <table><tbody>
        {filtered.map(r => <Row key={Math.random()} row={r} onSelect={() => select(r.id)} />)}
      </tbody></table>
    </>
  );
}
```

How do I make it fast?
