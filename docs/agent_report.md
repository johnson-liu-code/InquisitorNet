# Phase 1

## Scraper Agents
### ScraperAgent1
```python
# Input:
{
  "author_token": "[USER-REDACTED]",
  "body": "I suspect heresy brewing in the xenos cult, but this is just a painting list discussion.",
  "created_utc": "2025-08-14T12:00:00Z",
  "link_id": "t3_l",
  "parent_id": "t1_p",
  "permalink": "/r/InquisitorNetPrivateA/comments/xyz/t1_abc/",
  "subreddit": "InquisitorNetPrivateA"
}
# Output:
{
  "author_token": "[USER-REDACTED]",
  "body": "I suspect heresy brewing in the xenos cult, but this is just a painting list discussion.",
  "created_utc": "2025-08-14T12:00:00Z",
  "inserted_at": "2025-08-17 05:16:12",
  "item_id": "t1_abc",
  "keywords_hit": [
    "(?i)heresy",
    "(?i)xenos"
  ],
  "link_id": "t3_l",
  "parent_id": "t1_p",
  "permalink": "/r/InquisitorNetPrivateA/comments/xyz/t1_abc/",
  "post_meta_json": {
    "score": 3
  },
  "subreddit": "InquisitorNetPrivateA"
}
```

# Phase 2
## Detector Agents

### DetectorAgent1

```python
# Input:
{
  "author_token": "[USER-REDACTED]",
  "body": "I suspect heresy brewing in the xenos cult, but this is just a painting list discussion.",
  "created_utc": "2025-08-14T12:00:00Z",
  "inserted_at": "2025-08-17 05:16:12",
  "item_id": "t1_abc",
  "keywords_hit": [
    "(?i)heresy",
    "(?i)xenos"
  ],
  "link_id": "t3_l",
  "parent_id": "t1_p",
  "permalink": "/r/InquisitorNetPrivateA/comments/xyz/t1_abc/",
  "post_meta_json": {
    "score": 3
  },
  "subreddit": "InquisitorNetPrivateA"
}
# Output:
{
  "comment_text": "I suspect heresy brewing in the xenos cult, but this is just a painting list discussion.",
  "degree_of_confidence": 1.0,
  "id": 1,
  "item_id": "t1_abc",
  "post_meta_json": {
    "score": 3
  },
  "reasoning_for_mark": "Matched H001, H010; no benign context detected.",
  "subreddit": "InquisitorNetPrivateA"
}
```

## Gate Agents

### GateAgent1

```python
# Input:
{
  "checks": [
    {
      "action": "flag",
      "id": "OOU1",
      "name": "Out-of-universe references",
      "pattern": "(?i)modern politics|celebrity|stock ticker|brand"
    },
    {
      "action": "flag",
      "id": "IP1",
      "name": "Third-party IP identifiers",
      "pattern": "(?i)warhammer|games workshop|imperium of man|space marine"
    },
    {
      "action": "block",
      "id": "SAF1",
      "name": "Unsafe or harassing content",
      "pattern": "(?i)slur1|slur2|kill yourself"
    }
  ],
  "draft": {
    "scope": "fixture_draft",
    "text": "Original setting transmission. Do not reference any trademarks."
  }
}
# Output:
{
  "allow": true,
  "created_at": "2025-08-18 07:39:24",
  "flags": [],
  "id": 6,
  "raw_match": {},
  "reasons": "No policy flags matched; allow."
}
```

### GateAgent2

```python
# Input:
{
  "checks": [
    {
      "action": "flag",
      "id": "OOU1",
      "name": "Out-of-universe references",
      "pattern": "(?i)modern politics|celebrity|stock ticker|brand"
    },
    {
      "action": "flag",
      "id": "IP1",
      "name": "Third-party IP identifiers",
      "pattern": "(?i)warhammer|games workshop|imperium of man|space marine"
    },
    {
      "action": "block",
      "id": "SAF1",
      "name": "Unsafe or harassing content",
      "pattern": "(?i)slur1|slur2|kill yourself"
    }
  ],
  "draft": {
    "scope": "fixture_draft",
    "text": "We must remain vigilant. Respect others; avoid harassment."
  }
}
# Output:
{
  "allow": true,
  "created_at": "2025-08-18 07:39:24",
  "flags": [],
  "id": 5,
  "raw_match": {},
  "reasons": "No policy flags matched; allow."
}
```

### GateAgent3

```python
# Input:
{
  "checks": [
    {
      "action": "flag",
      "id": "OOU1",
      "name": "Out-of-universe references",
      "pattern": "(?i)modern politics|celebrity|stock ticker|brand"
    },
    {
      "action": "flag",
      "id": "IP1",
      "name": "Third-party IP identifiers",
      "pattern": "(?i)warhammer|games workshop|imperium of man|space marine"
    },
    {
      "action": "block",
      "id": "SAF1",
      "name": "Unsafe or harassing content",
      "pattern": "(?i)slur1|slur2|kill yourself"
    }
  ],
  "draft": {
    "scope": "fixture_draft",
    "text": "The market closed higher today; a modern politics topic."
  }
}
# Output:
{
  "allow": true,
  "created_at": "2025-08-18 07:39:24",
  "flags": [
    "OOU1"
  ],
  "id": 4,
  "raw_match": {
    "OOU1": [
      "modern politics"
    ]
  },
  "reasons": "Flags present (OOU1) but not blocking; allow with flags."
}
```

### GateAgent4

```python
# Input:
{
  "checks": [
    {
      "action": "flag",
      "id": "OOU1",
      "name": "Out-of-universe references",
      "pattern": "(?i)modern politics|celebrity|stock ticker|brand"
    },
    {
      "action": "flag",
      "id": "IP1",
      "name": "Third-party IP identifiers",
      "pattern": "(?i)warhammer|games workshop|imperium of man|space marine"
    },
    {
      "action": "block",
      "id": "SAF1",
      "name": "Unsafe or harassing content",
      "pattern": "(?i)slur1|slur2|kill yourself"
    }
  ],
  "draft": {
    "scope": "fixture_draft",
    "text": "Original setting transmission. Do not reference any trademarks."
  }
}
# Output:
{
  "allow": true,
  "created_at": "2025-08-17 09:09:37",
  "flags": [],
  "id": 3,
  "raw_match": {},
  "reasons": "No policy flags matched; allow."
}
```

### GateAgent5

```python
# Input:
{
  "checks": [
    {
      "action": "flag",
      "id": "OOU1",
      "name": "Out-of-universe references",
      "pattern": "(?i)modern politics|celebrity|stock ticker|brand"
    },
    {
      "action": "flag",
      "id": "IP1",
      "name": "Third-party IP identifiers",
      "pattern": "(?i)warhammer|games workshop|imperium of man|space marine"
    },
    {
      "action": "block",
      "id": "SAF1",
      "name": "Unsafe or harassing content",
      "pattern": "(?i)slur1|slur2|kill yourself"
    }
  ],
  "draft": {
    "scope": "fixture_draft",
    "text": "We must remain vigilant. Respect others; avoid harassment."
  }
}
# Output:
{
  "allow": true,
  "created_at": "2025-08-17 09:09:37",
  "flags": [],
  "id": 2,
  "raw_match": {},
  "reasons": "No policy flags matched; allow."
}
```

### GateAgent6

```python
# Input:
{
  "checks": [
    {
      "action": "flag",
      "id": "OOU1",
      "name": "Out-of-universe references",
      "pattern": "(?i)modern politics|celebrity|stock ticker|brand"
    },
    {
      "action": "flag",
      "id": "IP1",
      "name": "Third-party IP identifiers",
      "pattern": "(?i)warhammer|games workshop|imperium of man|space marine"
    },
    {
      "action": "block",
      "id": "SAF1",
      "name": "Unsafe or harassing content",
      "pattern": "(?i)slur1|slur2|kill yourself"
    }
  ],
  "draft": {
    "scope": "fixture_draft",
    "text": "The market closed higher today; a modern politics topic."
  }
}
# Output:
{
  "allow": true,
  "created_at": "2025-08-17 09:09:37",
  "flags": [
    "OOU1"
  ],
  "id": 1,
  "raw_match": {
    "OOU1": [
      "modern politics"
    ]
  },
  "reasons": "Flags present (OOU1) but not blocking; allow with flags."
}
```

---
Validation summary: scrapers=1, detectors=1, gate=6
