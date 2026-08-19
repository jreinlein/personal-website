# Next Steps

Single entry point for outstanding work. Last updated 2026-08-19.

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
- **No environment variables are set at all — no `NODE_VERSION` pinned.** Had
  Phase 1 added `package.json` without pinning a version, a future build would
  have run against whatever ancient default Netlify resolves to. One more
  reason the Pillow/no-npm decision below is the right one.
- DNS is externally managed, not Netlify DNS. Netlify subdomain is
  `jreinlein.netlify.app`. Image CDN is available but its free-plan quota
  isn't documented in-dashboard — check the pricing page if it's going to be
  relied on.

---

## Next up, in order

### 1. Gallery architecture — challenged and decided, 2026-08-18

The plan originally called for `sharp`, a `package.json`, `node_modules`, a Node
build script, and a CDN lightbox library on a site whose entire virtue is being
five static files that have not broken in nine years. That got a hard look
before the first `npm install` rather than after. Decisions:

- **Pillow, not `sharp`.** Python 3.10 with Pillow 9.5 is already installed and
  already proved sufficient — the 2026-08-17 audit read EXIF dates, pixel
  dimensions, orientation, camera make, and GPS presence from all 126 photos
  with zero installs. Pillow also resizes, writes WebP, and strips metadata.
  This removes `package.json`, `node_modules`, and the entire npm dependency —
  and with them the risk that Netlify auto-detects a build.
- **Generate the HTML on every run, don't hand-edit.** The script already has
  every photo's EXIF and `pottery.json` note loaded to do the resize/strip
  pass, so emitting `pottery/index.html` from the same data is nearly free —
  and far less error-prone than hand-splicing new `<figure>` blocks into a
  newest-first sorted list every month for years.
- **Two static derivative sizes, skip the Netlify Image CDN.** Its free-tier
  quota isn't documented anywhere in the dashboard or pricing page; a live
  per-request dependency on an unknown limit is worse than baking two WebP
  sizes ahead of time with a tool that's already running.
- **Keep a script — one Python (Pillow) script, not a manual per-batch tool.**
  125 of 126 photos are geotagged. **GPS stripping must be guaranteed, not
  remembered** — a script makes it automatic; a manual process makes it
  something to forget once. This was the strongest argument for keeping
  automation at all.
- **Full regen every run, not incremental.** The script reprocesses all of
  `originals/` each time rather than skipping already-built photos. At 126
  photos this costs seconds locally, and it guarantees a settings change
  (quality, size) reaches every derivative instead of only new ones.
- **PhotoSwipe, confirmed.** The one dependency that remains — it's the only
  thing on the site that reaches out to a CDN. Kept because sequential
  swipe-browsing and real pinch-zoom are worth it for a gallery meant to be
  browsed on mobile; a plain `<dialog>` or a hand-rolled lightbox were the
  zero-dependency alternatives considered and passed on.

→ [pottery-gallery-plan.md](pottery-gallery-plan.md) is updated to match — all
`sharp` references replaced with Pillow, `scripts/build-gallery.mjs` renamed
`scripts/build_gallery.py`.

### 2. Pottery gallery, Phase 1 — the build pipeline

→ [pottery-gallery-plan.md — Phases](pottery-gallery-plan.md#phases)

Scan `originals/`, read EXIF, emit resized WebP derivatives with metadata
stripped. **125 of the 126 photos carry GPS EXIF**, so verify stripping on real
output rather than trusting any library's default. Tooling is Pillow (Python),
per the decision in step 1 above.

Phases 2 (the page itself) and 3 (content and annotations) follow.

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
