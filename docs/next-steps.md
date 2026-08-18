# Next Steps

Single entry point for outstanding work. Last updated 2026-08-17.

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

---

## Next up, in order

### 1. Netlify dashboard checklist — do this *before* Phase 1

→ [hosting.md — TODO](hosting.md#todo-check-these-in-the-netlify-dashboard)

Six things to read out of the Netlify dashboard. The important one is **build
settings**: Phase 1 introduces a `package.json`, and Netlify may auto-detect it
and start running a build. That would convert a deploy which currently succeeds
by doing nothing into one that can fail. Worth five minutes before writing code.

If a build command turns out to be configured — or if pinning it seems wise
either way — add a `netlify.toml` that sets the publish directory and an empty
build command explicitly, so the deploy can't change behaviour on its own.

### 2. Pottery gallery, Phase 1 — the build pipeline

→ [pottery-gallery-plan.md — Phases](pottery-gallery-plan.md#phases)

`package.json` with `sharp`, then `scripts/build-gallery.mjs`: scan `originals/`,
read EXIF, emit resized WebP derivatives with metadata stripped. **125 of the 126
photos carry GPS EXIF**, so the plan calls for verifying stripping on real output
rather than trusting the library default.

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
