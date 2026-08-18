# Hosting & Infrastructure

How jamesreinlein.com is actually wired together. Written 2026-08-17 after a
session where several reasonable-looking assumptions turned out to be wrong.

Everything here is empirically verified — each claim lists how to re-check it,
because the surprising parts are surprising precisely because the obvious
assumption is wrong.

---

## The one-paragraph version

`jamesreinlein.com` is served by **Netlify**, which deploys the root of the
`master` branch of `jreinlein/personal-website` verbatim on every push. There is
no build step and no site generator. A second GitHub repo,
`jreinlein/jreinlein.github.io`, is an abandoned 2017 site that still holds a
GitHub Pages `CNAME` for the domain; it serves nothing but does cause a
confusing redirect.

## Topology

```
              DNS for jamesreinlein.com
                        │
                        ▼
                    ┌────────┐
                    │Netlify │ ── serves the live site
                    └────────┘
                        ▲
                        │ deploys repo root on push to master
                        │
   ┌────────────────────────────────────┐
   │ github.com/jreinlein/personal-website │  ← all work happens here
   └────────────────────────────────────┘

   ┌──────────────────────────────────────┐
   │ github.com/jreinlein/jreinlein.github.io │  ← abandoned 2017, DECOY
   └──────────────────────────────────────┘
        │ GitHub Pages enabled, CNAME = jamesreinlein.com
        └──► 301s jreinlein.github.io ──► jamesreinlein.com ──► Netlify
```

The decoy is why this looks like a GitHub Pages site from the outside: the
`*.github.io` URL really does redirect to the custom domain. But the domain's
DNS points at Netlify, so GitHub Pages never serves a byte of the live site.

**Verify the host:**

```bash
curl -sSI https://jamesreinlein.com/ | grep -iE "^(server|x-nf-request-id)"
```

Returns `server: Netlify` and an `x-nf-request-id`. If that ever changes, the
rest of this document is suspect.

## Deploys

Push to `master` → Netlify picks it up → live in about a minute. No CI, no build
command, no staging environment. Preview locally before pushing:

```bash
python -m http.server 8000
```

Because the deploy is a verbatim copy of the repo root, **what's in the repo is
what's on the internet**. There is no build phase in which files could be
filtered out.

## What is publicly reachable

Everything committed, with two exceptions:

| Category | Reachable? | Mechanism |
|---|---|---|
| Dotfiles (`.gitignore`, `.claude/`) | No | Netlify skips them automatically |
| `_redirects`, `_headers` | No | Netlify consumes rather than serves them |
| Scaffolding (`docs/`, `AGENTS.md`, …) | No | forced 404 rules in `_redirects` |
| Everything else | **Yes** | verbatim deploy |

Underscore-prefixed files are **not** special to Netlify — `_config.yml` was
served at `/_config.yml` until it was removed. Only `_redirects` and `_headers`
get consumed.

Rules in `_redirects` need a trailing `!` to take effect. Without it a matching
file wins and the rule is silently ignored — static files beat redirects unless
the rule is forced.

**Verify what's exposed:**

```bash
for f in README.md AGENTS.md docs/hosting.md index.html; do printf "%-22s " "$f"; curl -sS -o /dev/null -w "%{http_code}\n" "https://jamesreinlein.com/$f"; done
```

The first three should be 404, `index.html` 200.

## Git

The remote is **HTTPS**, not SSH:

```
origin  https://github.com/jreinlein/personal-website.git
```

It was switched from SSH in Aug 2026 because the Windows checkout had no key
GitHub accepts — the working SSH key lives in WSL, whose `~/.ssh` is a separate
filesystem from `C:\Users\<user>\.ssh`. HTTPS + Git Credential Manager sidesteps
this. A stale `~/.ssh/id_rsa` (2022) is still present on Windows and is offered
first by SSH; it is rejected by GitHub.

**History has diverged before.** In March 2024 the same edit was committed twice
— once locally, once via GitHub's web editor — leaving twin commits with
identical trees (`2c5fca4` local, `5f58411` remote) that sat unreconciled for
two years. It surfaced only when a push was finally attempted. `git rebase`
dropped the duplicate automatically as an already-applied patch.

Lesson: `origin/master` can be years stale if nobody fetches. Don't infer
push state from it, and don't infer it from the live site either — matching
*content* does not mean matching *commits*.

## Things not verified

Written from the outside; confirm against the Netlify dashboard if it matters:

- Whether a build command or publish directory is configured in Netlify's site
  settings (assumed: none and repo root respectively).
- Whether Netlify's asset optimization / post-processing is enabled.
- Whether DNS is managed by Netlify DNS or an external registrar.
- Whether the old repo's Pages setup can be retired without disturbing the
  domain. It's inert today; the risk is in the config, not the content.

## Open cleanup

- Retire `jreinlein/jreinlein.github.io` (archive it, drop its `CNAME`) to remove
  the ambiguity permanently. Low priority — inert today, and touching
  custom-domain config risks downtime.
- Remove the stale `~/.ssh/id_rsa` on Windows, or replace it with an ed25519 key
  registered to GitHub, if SSH is ever wanted again.
