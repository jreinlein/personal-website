# Next Steps

Single entry point for outstanding work. Last updated 2026-08-18.

This is an **index, not a spec** — it links to the docs that hold the detail
rather than repeating them, so there's only one copy of each fact to keep
current. Delete items as they land.

---

## Where things stand

The pottery gallery is **planned but not started** — no code written yet. What
exists so far is groundwork: the infrastructure is now understood and documented,
the photo set is audited, and the repo is set up so scaffolding doesn't leak onto
the public site.

Verified working as of 2026-08-17:

- `_redirects` hides `docs/`, `AGENTS.md`, `CLAUDE.md`, `README.md` from the live
  site while every real asset still serves.
- Netlify auto-deploys on push to `master`; `git push` over HTTPS works.
- 126 source photos sit in the gitignored `originals/`, all JPG, all dated.

Verified in the Netlify dashboard as of 2026-08-18 (→ [hosting.md — checklist](hosting.md#netlify-dashboard-checklist--completed-2026-08-18)):

- No build command, no publish directory override, nothing currently executes
  on push — confirmed by both settings and the actual deploy log.
- Pretty URLs are on, so `/pottery` will resolve without a trailing slash.
- **No environment variables are set at all — no `NODE_VERSION` pinned.** If
  Phase 1 adds `package.json` without pinning a version, a future build would
  run against whatever ancient default Netlify resolves to. Reinforces the
  Pillow/no-npm option below.
- DNS is externally managed, not Netlify DNS. Netlify subdomain is
  `jreinlein.netlify.app`. Image CDN is available but its free-plan quota
  isn't documented in-dashboard — check the pricing page if it's going to be
  relied on.

---

## Next up, in order

### 1. Re-examine the gallery architecture before writing any of it

The plan currently plans to add `sharp`, a `package.json`, `node_modules`, a Node
build script, and a CDN lightbox library to a site whose entire virtue is being
five static files that have not broken in nine years. That deserves a hard look
before the first `npm install`, not after.

Specific things to challenge:

- **Is `sharp` needed at all?** Python 3.10 with Pillow 9.5 is **already
  installed on this machine and already proved sufficient** — the 2026-08-17
  audit read EXIF dates, pixel dimensions, orientation, camera make, and GPS
  presence from all 126 photos with zero installs. Pillow also resizes, writes
  WebP, and strips metadata. Going that route removes `package.json`,
  `node_modules`, and the entire npm dependency — **and with them the risk that
  Netlify auto-detects a build**, which is currently the top pre-Phase-1 concern.
- **Does the HTML need generating on every run?** Generating it once and
  hand-editing thereafter may be fine for a gallery that changes monthly.
- **Is PhotoSwipe worth it?** A native `<dialog>`, or even plain links to the
  full-size image, may be enough. Its real advantage is touch handling on mobile.
- **Two derivative sizes, or one?** If the Netlify Image CDN is available, one
  committed size plus on-the-fly resizing may be simpler.
- **Does resizing need a script at all?** A batch export from Apple Photos or a
  single ImageMagick invocation is a legitimate answer for a monthly job.

Arguments on the other side, recorded so the decision is made honestly rather
than by mood:

- **GPS stripping must be guaranteed, not remembered.** 125 of 126 photos are
  geotagged. A script makes stripping automatic; a manual process makes it
  something to forget once. This is the strongest argument for automation.
- Hand-maintaining 126 `<figure>` blocks with correct pixel dimensions is
  error-prone, and PhotoSwipe needs those dimensions to be right.
- Monthly batches over several years is a lot of repeated manual work.

The point is not to pre-decide — it is to make this an explicit choice at the top
of Phase 1 instead of inheriting it from a plan written before the photos were
audited.

### 2. Pottery gallery, Phase 1 — the build pipeline

→ [pottery-gallery-plan.md — Phases](pottery-gallery-plan.md#phases)

Scan `originals/`, read EXIF, emit resized WebP derivatives with metadata
stripped. **125 of the 126 photos carry GPS EXIF**, so verify stripping on real
output rather than trusting any library's default. Tooling choice depends on the
outcome of step 1 above — the plan document currently assumes `sharp`.

Phases 2 (the page itself) and 3 (content and annotations) follow.

### 3. Rewrite the 404 page — independent, can be done anytime

`404.html` has real problems, several of which got worse when `_redirects` began
routing all hidden scaffolding through it:

- **Relative stylesheet paths break at nested URLs.** The page links
  `css/normalize.css`, so at `/docs/hosting.md` the browser requests
  `/docs/css/normalize.css` → 404, and the page renders **completely unstyled**.
  Verified 2026-08-17. Use root-relative paths (`/css/…`, `/img/…`). This is the
  actual bug; the rest is polish.
- **Stale metadata**: the description still reads "Software Developer at Amazon",
  which has been wrong since 2019. `index.html` says Senior Software Engineer II
  at Etsy.
- **No way back.** There is no link to the homepage — it's a dead end.
- `<title>` is just "James Reinlein", giving no indication it's an error page.
- It loads three stylesheets while `index.html` loads four (no `icons.css`), and
  uses inline `style=` attributes where `custom.css` already defines `.oops`.

---

## Optional cleanup — no deadline

- **Archive `jreinlein/jreinlein.github.io`.** Confirmed it cannot affect the
  live site. Only the `jreinlein.github.io` redirect is lost.
  → [hosting.md — Open cleanup](hosting.md#open-cleanup)
- **Sort out SSH on Windows.** The stale `~/.ssh/id_rsa` is rejected by GitHub;
  the working key lives in WSL. HTTPS works today, so this is only worth doing if
  SSH is wanted again. → [hosting.md — Git](hosting.md#git)

## Deferred features

Deliberately out of scope for the gallery's first version — per-piece URLs,
grouping and filtering, collapsing multiple photos of one piece into a single
entry, AVIF output.
→ [pottery-gallery-plan.md — Future work](pottery-gallery-plan.md#future-work--nice-to-haves)

## Notes for whoever picks this up

- `.claude/settings.json` pre-allows `git fetch`. It was added mid-session, so it
  takes effect from the next session onward, not the one that created it.
- `git push` is deliberately not pre-allowed — pushing deploys the live site.
- Don't trust `origin/master` without fetching first; it has been years stale.
