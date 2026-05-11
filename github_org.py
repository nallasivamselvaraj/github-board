# ============================================================
# github_org.py — GitHub Data Fetcher
# Fetches: Repositories, Issues, PRs, Releases, Contributors
# ============================================================

import requests
import json
from datetime import datetime
import os

from config import GITHUB_TOKEN, ORG_NAME, BASE_URL, ISSUE_STATE

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# ============================================================
# HELPERS
# ============================================================

def gh_get(url, params=None):
    """GET a GitHub API URL, return JSON or None."""
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if r.status_code == 200:
            return r.json()
        print(f"  [WARN] {r.status_code} — {url}")
        return None
    except Exception as e:
        print(f"  [ERROR] {e}")
        return None

def paginate(url, extra_params=None):
    """Fetch all pages from a GitHub list endpoint."""
    results = []
    page = 1
    while True:
        params = {"per_page": 100, "page": page}
        if extra_params:
            params.update(extra_params)
        data = gh_get(url, params)
        if not data:
            break
        results.extend(data)
        if len(data) < 100:
            break
        page += 1
    return results

# ============================================================
# REPOSITORIES
# ============================================================

def get_all_repositories():
    print("  Fetching repositories...")
    url = f"{BASE_URL}/orgs/{ORG_NAME}/repos"
    repos = paginate(url, {"sort": "updated", "direction": "desc"})
    print(f"  → {len(repos)} repositories found")
    return repos

# ============================================================
# ISSUES
# ============================================================

def get_repo_issues(repo_name):
    url = f"{BASE_URL}/repos/{ORG_NAME}/{repo_name}/issues"
    raw = paginate(url, {"state": ISSUE_STATE})
    return [i for i in raw if "pull_request" not in i]

# ============================================================
# PULL REQUESTS
# ============================================================

def get_repo_prs(repo_name):
    url = f"{BASE_URL}/repos/{ORG_NAME}/{repo_name}/pulls"
    return paginate(url, {"state": "all"})

# ============================================================
# RELEASES
# ============================================================

def get_repo_releases(repo_name):
    url = f"{BASE_URL}/repos/{ORG_NAME}/{repo_name}/releases"
    return paginate(url)

# ============================================================
# CONTRIBUTORS
# ============================================================

def get_repo_contributors(repo_name):
    url = f"{BASE_URL}/repos/{ORG_NAME}/{repo_name}/contributors"
    return paginate(url)

# ============================================================
# EXTRACT HELPERS
# ============================================================

def extract_issue(repo_name, issue):
    labels = [lb["name"] for lb in issue.get("labels", [])]
    return {
        "repository":    repo_name,
        "issue_number":  issue["number"],
        "title":         issue["title"],
        "state":         issue["state"],
        "author":        (issue.get("user") or {}).get("login", ""),
        "created_at":    issue.get("created_at", ""),
        "updated_at":    issue.get("updated_at", ""),
        "closed_at":     issue.get("closed_at", ""),
        "comments":      issue.get("comments", 0),
        "labels":        ", ".join(labels),
        "issue_url":     issue.get("html_url", ""),
        "body_length":   len(issue.get("body") or ""),
    }

def extract_pr(repo_name, pr):
    labels = [lb["name"] for lb in pr.get("labels", [])]
    return {
        "repository":    repo_name,
        "pr_number":     pr["number"],
        "title":         pr["title"],
        "state":         pr["state"],
        "draft":         pr.get("draft", False),
        "merged":        pr.get("merged_at") is not None,
        "author":        (pr.get("user") or {}).get("login", ""),
        "created_at":    pr.get("created_at", ""),
        "updated_at":    pr.get("updated_at", ""),
        "closed_at":     pr.get("closed_at", ""),
        "merged_at":     pr.get("merged_at", ""),
        "comments":      pr.get("comments", 0),
        "commits":       pr.get("commits", 0),
        "additions":     pr.get("additions", 0),
        "deletions":     pr.get("deletions", 0),
        "changed_files": pr.get("changed_files", 0),
        "labels":        ", ".join(labels),
        "pr_url":        pr.get("html_url", ""),
        "base_branch":   (pr.get("base") or {}).get("ref", ""),
        "head_branch":   (pr.get("head") or {}).get("ref", ""),
    }

def extract_release(repo_name, rel):
    return {
        "repository":    repo_name,
        "tag":           rel.get("tag_name", ""),
        "name":          rel.get("name", ""),
        "author":        (rel.get("author") or {}).get("login", ""),
        "created_at":    rel.get("created_at", ""),
        "published_at":  rel.get("published_at", ""),
        "prerelease":    rel.get("prerelease", False),
        "draft":         rel.get("draft", False),
        "release_url":   rel.get("html_url", ""),
        "body_length":   len(rel.get("body") or ""),
    }

def extract_repo(repo):
    return {
        "name":          repo["name"],
        "full_name":     repo.get("full_name", ""),
        "language":      repo.get("language") or "—",
        "stars":         repo.get("stargazers_count", 0),
        "forks":         repo.get("forks_count", 0),
        "open_issues":   repo.get("open_issues_count", 0),
        "size_kb":       repo.get("size", 0),
        "default_branch": repo.get("default_branch", "main"),
        "created_at":    repo.get("created_at", ""),
        "updated_at":    repo.get("pushed_at", ""),
        "repo_url":      repo.get("html_url", ""),
        "description":   repo.get("description") or "",
        "private":       repo.get("private", False),
        "archived":      repo.get("archived", False),
        "fork":          repo.get("fork", False),
        "topics":        ", ".join(repo.get("topics", [])),
    }

def extract_contributor(repo_name, c):
    return {
        "repository":    repo_name,
        "author":        c.get("login", ""),
        "contributions": c.get("contributions", 0),
        "avatar_url":    c.get("avatar_url", ""),
        "profile_url":   c.get("html_url", ""),
    }

# ============================================================
# MAIN
# ============================================================

def main():
    print("\n" + "=" * 50)
    print("  GitHub Org Fetcher — " + ORG_NAME)
    print("=" * 50 + "\n")

    repos = get_all_repositories()

    all_issues      = []
    all_prs         = []
    all_releases    = []
    all_contributors = []
    all_repo_meta   = []

    for idx, repo in enumerate(repos, 1):
        name = repo["name"]
        print(f"[{idx:3}/{len(repos)}] {name}")

        all_repo_meta.append(extract_repo(repo))

        issues = get_repo_issues(name)
        print(f"         issues={len(issues)}", end="")
        all_issues.extend([extract_issue(name, i) for i in issues])

        prs = get_repo_prs(name)
        print(f"  prs={len(prs)}", end="")
        all_prs.extend([extract_pr(name, p) for p in prs])

        releases = get_repo_releases(name)
        print(f"  releases={len(releases)}", end="")
        all_releases.extend([extract_release(name, r) for r in releases])

        contributors = get_repo_contributors(name)
        print(f"  contributors={len(contributors)}")
        all_contributors.extend([extract_contributor(name, c) for c in contributors])

    # Save all JSON files
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    datasets = {
        f"github_all_repo_issues_{ts}.json":       all_issues,
        f"github_all_repo_prs_{ts}.json":          all_prs,
        f"github_all_repo_releases_{ts}.json":     all_releases,
        f"github_all_repo_contributors_{ts}.json": all_contributors,
        f"github_all_repo_meta_{ts}.json":         all_repo_meta,
    }

    for filename, data in datasets.items():
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"  Saved {filename}  ({len(data)} records)")

    print("\n" + "=" * 50)
    print(f"  Repos        : {len(repos)}")
    print(f"  Issues       : {len(all_issues)}")
    print(f"  Pull Requests: {len(all_prs)}")
    print(f"  Releases     : {len(all_releases)}")
    print(f"  Contributors : {len(all_contributors)}")
    print("=" * 50)


if __name__ == "__main__":
    main()
