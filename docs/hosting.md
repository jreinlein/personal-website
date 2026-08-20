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

The remote is **SSH** (switched back from HTTPS 2026-08-20):

```
origin  git@github.com:jreinlein/personal-website.git
```

Earlier in Aug 2026 this was switched to HTTPS because the Windows checkout had
no key GitHub accepted — the old `~/.ssh/id_rsa` (2022) was stale and rejected,
and the only working key lived in WSL, a separate filesystem from
`C:\Users\<user>\.ssh`. Fixed 2026-08-20 by generating a fresh ed25519 keypair
directly on Windows (`~/.ssh/id_ed25519`), registering its public key on
GitHub as an **authentication key** (not a signing key), and pointing
`~/.ssh/config` at it for `github.com`:

```
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    AddKeysToAgent yes
```

The key has **no passphrase**, so `ssh` reads it straight off disk on every
invocation — no `ssh-agent` needs to be running, and nothing needs re-doing
after a reboot or a fresh shell. The old `~/.ssh/id_rsa` is still present but
unused (superseded, not registered on GitHub); harmless to leave or remove.

**History has diverged before.** In March 2024 the same edit was committed twice
— once locally, once via GitHub's web editor — leaving twin commits with
identical trees (`2c5fca4` local, `5f58411` remote) that sat unreconciled for
two years. It surfaced only when a push was finally attempted. `git rebase`
dropped the duplicate automatically as an already-applied patch.

Lesson: `origin/master` can be years stale if nobody fetches. Don't infer
push state from it, and don't infer it from the live site either — matching
*content* does not mean matching *commits*.

## Netlify dashboard checklist — completed 2026-08-18

Checked directly in the dashboard (project `jreinlein`, team "James Reinlein's
team", Free/Legacy plan). Ordered as originally planned, by how much damage the
wrong assumption would have done.

- [x] **Build settings** — *Project configuration → Build & deploy →
      Continuous deployment*. Confirmed: Runtime not set, Base directory `/`,
      Package directory not set, **Build command: Not set**, **Publish
      directory: Not set** (defaults to repo root), Functions directory
      `netlify/functions` (unused), Deploy log visibility public, Build status
      Active. Matches the assumption exactly — nothing to pin yet, but see the
      Node version note below before Phase 1 adds `package.json`.

- [x] **Latest deploy log** — deploy `ad55b8e` (2026-08-17 9:43 PM). Summary:
      "3 new files uploaded, 3 assets changed. 7 redirect rules processed, all
      deployed without errors." Build time 5s, total deploy time 4s. This is
      upload-and-redirect-processing time, not compilation — confirms by
      evidence (not just settings) that nothing currently executes on push.

- [x] **Post processing / asset optimization** — *Build & deploy → Post
      processing*. The image-compression/CSS-JS-minify toggle described in the
      original TODO **no longer exists in Netlify's UI** — apparently removed
      as a product, not just off. What's actually there: Legacy Prerendering
      (deprecated, unused), Snippet injection (none added), **Pretty URLs:
      enabled**. Pretty URLs being on means `/pottery` (no trailing slash,
      no `.html`) will resolve once that page exists, without needing a
      redirect rule for it.

- [x] **Site name** — `jreinlein.netlify.app`, not `jamesreinlein` — the
      Netlify project is named `jreinlein`. Useful as a DNS-independent test
      URL; use the actual subdomain, not an assumed one.

- [x] **Domain management** — Production domains: `jamesreinlein.com`
      (primary), `www.jamesreinlein.com` (auto-redirects to primary),
      `jreinlein.netlify.app`. No Netlify-DNS nameserver panel is shown on
      this page, which means the zone is **externally managed**, not Netlify
      DNS — consistent with only the apex IP being previously known. SSL is
      Let's Encrypt, auto-renews before Oct 8 2026.

- [x] **Netlify Image CDN availability** — "Image transformations" exists as
      a tracked usage category under Team → Usage & billing → Account usage
      insights, currently zero usage, so the feature is available to use.
      Its exact quota isn't in the Free/Legacy plan's bullet list of included
      features, though (300 build minutes, 100 GB bandwidth, 1M Edge Function
      invocations, 1 concurrent build, 500 projects) — confirm the real limit
      on the pricing page before designing around it rather than assuming.

### New finding: no environment variables are set

*Project configuration → Environment variables* shows **zero variables of any
kind** — no `NODE_VERSION`, nothing. This is what's actually behind the
"Your project uses Node.js 10" banner on the project overview page: that
banner is Netlify nudging toward its new **Agent Runners** AI-agent feature,
which wants Node 22+, and Node 10 is what it detects as the effective default
in this project's config. It is **not** a warning about the live deploy
pipeline — a red herring for that purpose, since no build runs today.

It's still directly relevant to next-steps.md's item 2, though: if
Phase 1 adds a `package.json` without pinning a version (via `NODE_VERSION` or
`.nvmrc`), a future build would run against whatever Netlify's ancient default
resolves to, not a version anyone chose. If the Pillow/no-npm route is taken
instead, this whole class of problem disappears along with `package.json`
itself — one more point in its favor.

Build image, separately, is current: **Ubuntu Noble 24.04 (default)** — no
action needed there.

## Open cleanup

- Optionally delete the now-unused `~/.ssh/id_rsa`/`id_rsa.pub` on Windows —
  superseded by `id_ed25519` (see [Git](#git)), left in place but inert.

## Done

- **`jreinlein/jreinlein.github.io` archived (2026-08-20).** Verified
  2026-08-17 it couldn't affect the live site: the apex resolves to Netlify,
  and GitHub only ever served a 301 from its own `*.github.io` URL. Confirmed
  2026-08-20 that the redirect **did survive archiving** —
  `curl -sSI https://jreinlein.github.io` still returns
  `301 → http://jamesreinlein.com/`.
