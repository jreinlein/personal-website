# AGENTS.md

Context for AI coding agents working in this repo. Humans welcome too.

## What this is

The source for **jamesreinlein.com** — a single-page personal site. Plain static
HTML/CSS, no framework, no build step, no JavaScript. Served by GitHub Pages from
the root of the `master` branch of `jreinlein/personal-website`.

## Layout

```
index.html    the whole site
404.html      error page
_config.yml   Pages build config — see "What gets published" below
.claude/      agent permissions for this repo
css/          normalize.css + skeleton.css (vendored, do not edit)
              custom.css + icons.css (ours)
icons/        icon webfont
img/          images
docs/         planning docs for in-flight work (not published)
```

`css/normalize.css` and `css/skeleton.css` are vendored third-party files. Leave
them alone; put overrides in `css/custom.css` or a new stylesheet.

## Conventions

- **No build step, no bundler, no package manager for the site itself.** What's
  in the repo is what ships. Keep it that way — a tool that generates committed
  output is fine, a tool the site depends on at serve time is not.
- **No frameworks.** Styling is [Skeleton](http://getskeleton.com/); stick to its
  grid classes (`row`, `columns`, `offset-by-*`) rather than inventing a layout system.
- Two-space indent in HTML and CSS.
- Vanilla JS only if genuinely needed, loaded from a CDN, no build.
- New top-level pages go in their own directory as `index.html`
  (`pottery/index.html` → `/pottery`), so URLs stay clean.

## What gets published

Pages serves from the repo root, so **every committed file is served on the
domain** unless excluded — `jamesreinlein.com/README.md` would return the readme.
Dotfiles are excluded automatically; everything else needs listing in the
`exclude:` block of `_config.yml`.

When adding project scaffolding that isn't part of the website — docs, build
scripts, `package.json` — add it to that list. Note that Jekyll's `exclude`
*replaces* its default list rather than extending it, which is why the defaults
are spelled out there.

## Deploying

`.claude/settings.json` pre-allows `git fetch` so agents can check real remote
state without a prompt. `git push` is deliberately **not** allowed: pushing to
`master` deploys to the live public site, so that stays a human action.

Push to `master`. GitHub Pages publishes automatically, usually within a minute.
There is no staging environment — preview locally before pushing, e.g.:

```bash
python -m http.server 8000
```

## Gotchas

- **`jreinlein/jreinlein.github.io` is not this site.** It's an abandoned 2017
  version that still holds a `CNAME` for the domain, so its `*.github.io` URL
  redirects here. All work happens in this repo. Don't "fix" the old one without
  a deliberate plan — its domain config is entangled with this one.
- This repo has no `CNAME` file; the custom domain is set in Pages settings.
  Don't add or remove one casually — it can take the site offline.
- The site is public and so is this file. Never commit secrets, tokens, private
  URLs, or absolute local paths.

## In flight

- [Pottery gallery](docs/pottery-gallery-plan.md) — a photo gallery at `/pottery`.
  Read that doc before touching anything pottery-related; it covers the image
  pipeline, why originals must stay out of git, and the EXIF/GPS stripping requirement.
