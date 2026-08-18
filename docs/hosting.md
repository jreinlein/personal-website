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

## TODO: check these in the Netlify dashboard

Everything above was determined from outside the dashboard — HTTP headers, DNS,
and the repo. These are the gaps. They are ordered by how much damage the wrong
assumption would do.

**Do not record access tokens, deploy keys, build hooks, or environment variable
values here or paste them into a chat.** None of the questions below need them;
settings names and values are enough.

- [ ] **Build settings** — *Site configuration → Build & deploy → Build settings*.
      Record the build command, publish directory, and base directory.
      **Why it matters most:** the pottery gallery adds a `package.json`, and
      Netlify auto-detects those and may start running a build. That would turn
      a deploy which currently works by doing nothing into one that can fail.
      If a build command is empty, confirm it stays empty — or pin it explicitly
      in a `netlify.toml` before Phase 1 lands.
      *Assumed today: no build command, publish directory = repo root.*

- [ ] **Latest deploy log** — *Deploys → click the top entry*.
      Shows definitively what happens on a push: whether anything is executed,
      how long it takes, and what gets published. Settles the above by evidence
      rather than by reading a settings field.

- [ ] **Post processing / asset optimization** — *Build & deploy → Post
      processing*. Note whether image compression, CSS/JS bundling or minifying,
      and Pretty URLs are on.
      **Why:** if image compression is enabled, Netlify may re-encode the WebP
      derivatives the gallery build tunes by hand, silently undoing that work.
      Pretty URLs decides whether `/pottery` resolves without a trailing slash.

- [ ] **Site name** — the `<name>.netlify.app` subdomain.
      Gives a permanent URL to test deploys against that doesn't depend on DNS,
      which is useful for isolating "is this a DNS problem or a deploy problem".

- [ ] **Domain management** — which domains are attached, and whether DNS is
      Netlify DNS or an external registrar. The apex resolves to `104.198.14.52`
      (a Netlify load balancer), but *who manages the zone* is still unknown.
      Only matters if the old GitHub repo is ever retired.

- [ ] **Netlify Image CDN availability** and its limits on the current plan.
      If available, `/.netlify/images?url=…&w=500` resizes on the fly, so the
      gallery could commit only the ~1600px derivatives and let the CDN generate
      thumbnails — roughly halving what goes into git. Trade-off: it adds a
      runtime dependency to a site whose main virtue is being static files.
      Evaluate, don't assume.

## Open cleanup

- Retire `jreinlein/jreinlein.github.io` (archive or delete) to remove the
  ambiguity permanently. Verified 2026-08-17 that it cannot affect the live
  site: the apex resolves to Netlify, and GitHub serves only a 301 from its own
  `*.github.io` URL. The only thing lost is that redirect, which may appear in
  old links. Archiving is preferable to deleting; afterwards confirm with
  `curl -sSI https://jreinlein.github.io` whether Pages (and the redirect)
  survived archiving — that is not certain.
- Remove the stale `~/.ssh/id_rsa` on Windows, or replace it with an ed25519 key
  registered to GitHub, if SSH is ever wanted again.
