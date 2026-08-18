# Pottery Gallery — Scoping & Plan

Status: **planned, not started**
Last updated: 2026-08-17

Adds a photo gallery at `jamesreinlein.com/pottery` showing James's pottery work.
Purely a portfolio — no commerce, no contact-about-this-piece flow.

---

## Decisions locked in

| Question | Decision |
|---|---|
| Layout | Flat grid, chronological, **newest first** |
| Grouping / filtering | Not in v1. Revisit later (see Future work) |
| Per-piece URLs | Not in v1. Lightbox only. Nice-to-have later |
| Source photos | iPhone JPGs (not HEIC — no conversion step needed) |
| Metadata | Auto from EXIF; optional hand-written notes in a sidecar file |
| Update cadence | Batches roughly once a month, once James rejoins a studio |
| Build | Local script, run by hand; commit the generated output |
| Hosting | Existing Netlify setup, no new services, no cost |

## The actual photo set (audited 2026-08-17)

126 files sitting in the gitignored `originals/`. Measured, not assumed:

```
total photos      : 126   (all .jpg — no HEIC, no conversion step needed)
missing EXIF date : 1     (IMG_0998.jpg)
WITH GPS DATA     : 125   <-- every Apple photo is geotagged
orientation       : 89 landscape / 37 portrait
megapixels        : min 3.3 · median 12.2 · max 24.5
file size         : median 2.0MB · total 256MB
date range        : 2022-12 -> 2025-08, across 16 distinct months
```

Consequences:

- **GPS stripping is load-bearing, not theoretical.** 125/126 embed location.
  `sharp` drops metadata by default on resize, but Phase 1 verifies this on real
  output rather than trusting the default.
- **`IMG_0998.jpg` has no EXIF at all** — no date, no camera make. Confirmed by
  James as his own work; the metadata was lost somewhere along the way. Its
  filename-sequential neighbours date it confidently: `IMG_0997` at
  2024-01-03 10:44:19 and `IMG_0999` at 2024-01-03 10:45:58, so it belongs to
  that same 2024-01-03 session. Resolved — no manual entry needed.
- **Mixed orientation confirms masonry** over a square-cropped grid.
- 256MB of originals should yield roughly 45MB of derivatives.

## Constraints

- **Netlify free-tier bandwidth**: ~100GB/month. Optimized derivatives keep the
  gallery around 45MB total — comfortable. Committing originals (256MB) would
  burn through it and is explicitly out of scope.
- **Git keeps binaries forever.** A bad commit of full-size originals permanently
  bloats the repo and is painful to undo. Originals stay gitignored.
- **EXIF carries GPS.** iPhone photos embed location. Every published derivative
  must have metadata stripped. This is a hard requirement, not a nice-to-have.
- **No build step exists today.** The site is hand-written static HTML. The build
  script is a local authoring tool; the deployed site stays plain static files.

---

## Architecture

```
originals/               # gitignored. Full-size iPhone JPGs, local only.
pottery.json             # committed. Optional per-photo notes, keyed by filename.
scripts/build-gallery.mjs# committed. Reads originals/ + pottery.json -> output.
img/pottery/             # committed, GENERATED. Derivatives only.
  thumb/<name>.webp      #   ~500px wide,      q75,  ~30-60KB
  large/<name>.webp      #   ~1600px long edge, q80, ~150-350KB
pottery/index.html       # committed, GENERATED. The page itself.
```

**Generated files are committed.** The published site must work without a build,
so the script's output is checked in. Never hand-edit anything under
`img/pottery/` or `pottery/index.html` — regenerate instead.

### Pipeline

1. Scan `originals/*.jpg`.
2. Per photo, read EXIF `DateTimeOriginal` + pixel dimensions via `sharp`.
   If the date is missing, interpolate from the nearest filename-sequential
   neighbours that do have one (iPhone `IMG_####` names increase monotonically,
   so a gap between two same-session shots is reliable). Fall back to a manual
   `date` in `pottery.json` only when interpolation can't bracket it.
3. Merge with `pottery.json` — sidecar values win over EXIF (lets a wrong or
   missing date be corrected by hand).
4. Emit resized WebP derivatives, **metadata stripped**, into `img/pottery/`.
5. Sort newest-first; tiebreak on filename so ordering is stable across runs.
6. Render `pottery/index.html` as static HTML.
7. Write back `pottery.json` with empty stubs added for any new photos, so the
   file doubles as the "still needs annotating" list. Never overwrite existing
   values.
8. Print a report: total photos, any missing/unparseable dates, output size.

### Metadata shape

All fields optional. A photo with no entry renders with just its date.

```json
{
  "IMG_4821.jpg": {
    "title": "Faceted tumbler",
    "clay": "Speckled buff stoneware",
    "glaze": "Shino over iron slip",
    "notes": "Thrown, faceted with a loop tool while leather-hard.",
    "date": "2023-06"
  }
}
```

`date` is an override — only needed when EXIF is missing or misleading.
Accepts `YYYY`, `YYYY-MM`, or `YYYY-MM-DD`.

### Front-end

- **Grid:** CSS `columns` masonry. Zero JS, handles mixed portrait/landscape.
- **Lightbox:** PhotoSwipe v5 (MIT, ~30KB, no deps, ESM from CDN). Chosen for
  touch handling — pinch zoom and swipe-to-dismiss — since most traffic is mobile.
  Needs `data-pswp-width/height` per image, which the script emits from EXIF.
- **Native browser wins:** `loading="lazy"`, explicit `width`/`height`,
  `srcset`/`sizes`, `decoding="async"`.
- **Degrades without JS:** grid and captions are real HTML; PhotoSwipe only
  enhances click-to-enlarge.
- Styling reuses the existing Skeleton + `css/custom.css` look. Gallery-specific
  rules go in a new `css/pottery.css` rather than growing `custom.css`.

---

## Phases

### Phase 1 — Pipeline
- [ ] Add `originals/` to `.gitignore`
- [ ] `package.json` with `sharp` + an `npm run gallery` script
- [ ] `scripts/build-gallery.mjs`: scan, EXIF read, resize, strip metadata, emit
- [ ] Verify GPS/EXIF is actually gone from output (spot-check with `exiftool`)
- [ ] Report missing dates so they can be corrected in `pottery.json`

### Phase 2 — Page
- [ ] HTML generation into `pottery/index.html`
- [ ] `css/pottery.css` — masonry grid matching site styling
- [ ] Wire up PhotoSwipe v5 + captions
- [ ] Link to `/pottery` from `index.html`
- [ ] `<title>`, description, Open Graph tags for link previews
- [ ] Check on a real phone, and with JS disabled

### Phase 3 — Content
- [x] Photo backlog in `originals/` (126 files, audited above)
- [x] `IMG_0998.jpg` confirmed as James's work; date resolved by interpolation
- [ ] Run the build; confirm all 126 land with a sensible date
- [ ] Fill in `pottery.json` from notes where they exist
- [ ] Review output size before committing

---

## Future work / nice-to-haves

Deliberately out of scope for v1. Roughly in order of likely value:

- **Per-piece URLs** (`/pottery/faceted-tumbler`). Makes a single piece
  shareable and indexable. Would mean a slug per photo in `pottery.json` and one
  generated page each. Worth doing if the collection grows or gets linked around.
- **Grouping / filtering** by year, form, or glaze. Only worth it past ~100
  pieces, and needs the metadata to actually be filled in first.
- **Multiple photos per piece.** Right now each JPG is its own gallery entry. If
  several angles of one pot should collapse into a single entry, `pottery.json`
  needs a piece-level grouping key. Open question — depends on how the backlog
  actually looks.
- **AVIF alongside WebP** via `<picture>`. Another ~20-30% off. Marginal at this
  size; adds build time and complexity.
- **Netlify build on push** instead of committing generated output. Only worth it
  if the manual run becomes annoying. At once-a-month it isn't — and the current
  no-build deploy is the thing that makes this site boring and reliable.

---

## Notes & open questions

- **Hosting is Netlify, not GitHub Pages.** Confirmed 2026-08-17 via the `server:
  Netlify` response header. Netlify deploys the repo root verbatim on every push
  to `master` — no build command, no site generator. An earlier `_config.yml`
  written on the GitHub-Pages assumption did nothing and was removed. Check the
  `server` header before assuming a hosting mechanism here.
- **`jreinlein.github.io` is a decoy.** That repo last shipped in Jan 2017 and
  its GitHub Pages setup still holds a `CNAME` for `jamesreinlein.com`, so its
  `*.github.io` URL 301s to the domain — which DNS points at Netlify. GitHub
  Pages never serves this site. Do all work in `personal-website`. Low-priority
  cleanup: retire the old repo to remove the ambiguity, but it's inert today and
  fiddling with domain config risks downtime.
- Confirm the backlog is genuinely all JPG before building — a stray HEIC will
  need `sharp` extras or a re-export from Apple Photos.
- **This doc is committed but not reachable.** Everything committed ships to the
  CDN, so `_redirects` returns a forced 404 for `docs/`, `scripts/`,
  `package.json` and the agent files. Anything added in Phase 1 that isn't part
  of the website needs a rule there — and anything the gallery serves
  (`pottery/`, `img/pottery/`, `css/pottery.css`) must stay off it.
