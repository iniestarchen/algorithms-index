#!/usr/bin/env python3
"""Build INDEX.json by scanning all openqc/algo-* repos + community submissions.

Runs as a GitHub Action (every 6h) or manually.
Uses GitHub API to discover repos and fetch algorithm.json from each.

Usage:
  GITHUB_TOKEN=ghp_xxx python scripts/build_index.py

Output:
  INDEX.json (written to repo root)
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import urllib.request
import urllib.error

GITHUB_API = "https://api.github.com"
ORG = os.environ.get("OPENQC_GITHUB_ORG", "iniestarchen")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {"Accept": "application/vnd.github+json"}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

INDEX_FILE = Path(__file__).parent.parent / "INDEX.json"
SUBMISSIONS_FILE = Path(__file__).parent.parent / "SUBMISSIONS.json"
TAXONOMY_FILE = Path(__file__).parent.parent / "TAXONOMY.json"


def github_get(url: str) -> dict | list | None:
    """Fetch JSON from GitHub API."""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {url}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  Error: {e}: {url}", file=sys.stderr)
        return None


def fetch_algo_json(repo_full_name: str, ref: str = "main") -> dict | None:
    """Fetch algorithm.json from a repo's root."""
    url = f"{GITHUB_API}/repos/{repo_full_name}/contents/algorithm.json?ref={ref}"
    data = github_get(url)
    if data and "content" in data:
        import base64
        content = base64.b64decode(data["content"]).decode("utf-8")
        return json.loads(content)
    # Try raw URL
    raw_url = f"https://raw.githubusercontent.com/{repo_full_name}/{ref}/algorithm.json"
    req = urllib.request.Request(raw_url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def get_repo_info(repo_full_name: str) -> dict | None:
    """Get repo metadata (stars, last push, default branch)."""
    url = f"{GITHUB_API}/repos/{repo_full_name}"
    return github_get(url)


def scan_org_repos() -> list[str]:
    """Find all openqc/algo-* repos in the org."""
    repos = []
    page = 1
    while True:
        url = f"{GITHUB_API}/orgs/{ORG}/repos?per_page=100&page={page}"
        data = github_get(url)
        if not data:
            break
        for repo in data:
            name = repo.get("name", "")
            if name.startswith("algo-") and not repo.get("archived"):
                repos.append(repo["full_name"])
        if len(data) < 100:
            break
        page += 1
    return repos


def load_community_submissions() -> list[str]:
    """Load community repo URLs from SUBMISSIONS.json."""
    if SUBMISSIONS_FILE.exists():
        with open(SUBMISSIONS_FILE) as f:
            data = json.load(f)
        return [s["repo"] for s in data.get("community_repos", []) if "repo" in s]
    return []


def build_index():
    """Main: scan repos, fetch algorithm.json, build INDEX.json."""
    print(f"Building algorithm index for org: {ORG}")

    # Discover repos
    org_repos = scan_org_repos()
    community_repos = load_community_submissions()
    all_repos = list(set(org_repos + community_repos))
    print(f"Found {len(org_repos)} org repos + {len(community_repos)} community repos = {len(all_repos)} total")

    # Fetch algorithm.json from each
    algorithms = []
    for repo in sorted(all_repos):
        print(f"  Scanning {repo}...")
        algo = fetch_algo_json(repo)
        if not algo:
            print(f"    No algorithm.json found — skipping")
            continue

        # Get repo metadata
        info = get_repo_info(repo) or {}

        entry = {
            "slug": algo.get("slug", ""),
            "repo": repo,
            "name": algo.get("name", ""),
            "author": algo.get("author", repo.split("/")[0]),
            "version": algo.get("version", "1.0.0"),
            "access": algo.get("access", "open"),
            "industries": algo.get("industries", []),
            "techniques": algo.get("techniques", []),
            "difficulty": algo.get("difficulty", "intermediate"),
            "computation_model": algo.get("computation_model", "gate"),
            "algorithm_type": algo.get("algorithm_type", "circuit"),
            "qubit_count": algo.get("qubit_count", 0),
            "description": algo.get("description", ""),
            "tags": algo.get("tags", []),
            "source": "official" if repo.startswith(f"{ORG}/") else "community",
            "stars": info.get("stargazers_count", 0),
            "last_updated": info.get("pushed_at", ""),
            "default_branch": info.get("default_branch", "main"),
        }

        if entry["slug"]:
            algorithms.append(entry)
            print(f"    Added: {entry['slug']} ({entry['source']})")
        else:
            print(f"    Missing slug — skipping")

    # Sort by source (official first), then name
    algorithms.sort(key=lambda a: (0 if a["source"] == "official" else 1, a["slug"]))

    # Write INDEX.json
    index = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(algorithms),
        "algorithms": algorithms,
    }

    with open(INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)

    print(f"\nINDEX.json written: {len(algorithms)} algorithms")


if __name__ == "__main__":
    build_index()
