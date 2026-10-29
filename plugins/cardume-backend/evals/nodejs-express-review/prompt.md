---
name: nodejs-express-review
tags: [trigger]
runs: 3
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
---

This Express endpoint sometimes crashes the whole Node process in production and the event loop lag spikes when someone uploads a big report. What's wrong and how should I fix it?

```js
app.post('/reports', async (req, res) => {
  const user = await db.users.findOne({ id: req.body.userId });
  const data = fs.readFileSync('/data/' + req.body.file);
  const hash = crypto.pbkdf2Sync(data, 'salt', 100000, 64, 'sha512');
  const rows = JSON.parse(data);
  rows.forEach(async r => { await db.reports.insert({ ...r, owner: user.id }); });
  res.json({ ok: true, hash: hash.toString('hex') });
});
```
