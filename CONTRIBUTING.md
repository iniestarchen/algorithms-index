# Contributing Algorithms to OpenQC

Thank you for contributing! Every algorithm makes quantum computing more accessible.

## Two Ways to Contribute

### Option A: Use Our Template (recommended)

1. Go to [iniestarchen/algo-template](https://github.com/iniestarchen/algo-template)
2. Click **"Use this template"** → creates a new repo in your account
3. Fill in `algorithm.json`, `circuit.qasm`, `template.py`, `README.md`
4. Push your changes
5. Submit a PR to [iniestarchen/algorithms-index](https://github.com/iniestarchen/algorithms-index):
   - Edit `SUBMISSIONS.json` and add your repo to the `community_repos` array:
   ```json
   {
     "community_repos": [
       {"repo": "your-username/your-repo-name", "submitted_by": "your-username", "submitted_at": "2026-03-24"}
     ]
   }
   ```
6. CI validates your algorithm automatically
7. Maintainer reviews → merge → your algorithm appears on the platform!

### Option B: Use Your Existing Repo

Already have a quantum algorithm repo? Just add `algorithm.json` to the root:

1. Create `algorithm.json` in your repo root following [schema.json](https://github.com/iniestarchen/algorithms-index/blob/main/schema.json)
2. Submit a PR to [iniestarchen/algorithms-index](https://github.com/iniestarchen/algorithms-index):
   - Edit `SUBMISSIONS.json` and add your repo:
   ```json
   {"repo": "your-username/your-repo-name", "submitted_by": "your-username", "submitted_at": "2026-03-24"}
   ```
3. That's it — your repo stays under your account

## algorithm.json Requirements

Minimum required fields:
```json
{
  "slug": "your-algorithm-slug",
  "name": "Your Algorithm Name",
  "description": "What it does in 1-2 sentences.",
  "qubit_count": 4,
  "industries": ["education"],
  "techniques": ["gate"],
  "tags": ["your", "tags"]
}
```

See [schema.json](./schema.json) for all available fields.
See [TAXONOMY.json](./TAXONOMY.json) for valid industry and technique labels.

## Access Tiers

When publishing, choose an access tier in `algorithm.json`:

| Tier | What to include in repo | Who can run it |
|------|------------------------|----------------|
| `"access": "open"` | Full code (circuit.qasm + template.py) | Everyone |
| `"access": "gated"` | Metadata only (algorithm.json + README) | Approved users |
| `"access": "paid"` | Metadata only | Paying users |

For gated/paid algorithms, the full code is uploaded to the platform separately.

## Quality Guidelines

- **README.md**: Explain the algorithm clearly enough for a university student
- **circuit.qasm**: Must be valid OpenQASM 2.0
- **template.py**: Must have `build()` and `interpret()` methods
- **benchmarks/**: Include expected results for at least one backend
- **Tags**: Use existing tags from TAXONOMY.json when possible

## Review Process

1. Submit PR to `algorithms-index`
2. CI checks: schema valid? QASM parses? No duplicate slug?
3. Maintainer reviews: quality, accuracy, no malicious code
4. Merge → indexed within 6 hours → live on platform

## Questions?

Open an issue on [algorithms-index](https://github.com/iniestarchen/algorithms-index/issues).
