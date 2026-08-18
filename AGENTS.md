# AGENTS.md

Context for AI coding agents working in this repo. Humans welcome too.

## What this is

The source for **jamesreinlein.com** — a single-page personal site. Plain static
HTML/CSS, no framework, no build step, no JavaScript.

**Hosting is Netlify, not GitHub Pages**, despite the site living on GitHub and
looking exactly like a Pages setup. Netlify deploys the repo root verbatim on
every push to `master` — no build command, no site generator.

**→ [docs/hosting.md](docs/hosting.md) has the full picture** and is worth
reading before any infrastructure, deploy, or DNS work. It covers the two-repo
topology, what is publicly reachable and why, and the git remote's history. The
GitHub-Pages assumption has already cost one round of wasted work.

## Layout

```
index.html    the whole site
404.html      error page
_redirects    Netlify routing — see "What gets published" below
.claude/      agent permissions for this repo
css/          normalize.css + skeleton.css (vendored, do not edit)
              custom.css + icons.css (ours)
icons/        icon webfont
img/          images
docs/         planning docs for in-flight work (not reachable, see _redirects)
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

**Every committed file ships to the CDN and is reachable by URL** — the deploy
is a verbatim copy, with no build phase that could filter anything out. Dotfiles
are the only automatic exception.

So when adding scaffolding that isn't part of the website — docs, build scripts,
`package.json` — add a forced-404 rule to `_redirects`. The trailing `!` is
required or the rule is silently ignored. Conversely, anything the site actually
serves must stay *off* that list. Details and verification commands in
[docs/hosting.md](docs/hosting.md).

## Deploying

`.claude/settings.json` pre-allows `git fetch` so agents can check real remote
state without a prompt. `git push` is deliberately **not** allowed: pushing to
`master` deploys to the live public site, so that stays a human action.

Push to `master`; Netlify deploys automatically, usually within a minute.
There is no staging environment — preview locally before pushing, e.g.:

```bash
python -m http.server 8000
```

## Gotchas

- **`jreinlein/jreinlein.github.io` is not this site.** Abandoned 2017 repo that
  still redirects here. Don't "fix" it without a deliberate plan.
- **Don't add a `CNAME` file.** GitHub Pages mechanism; does nothing on Netlify.
- **Don't trust `origin/master` without fetching.** It has been years stale, and
  history has silently diverged before. Matching site *content* does not mean
  matching *commits*.
- The site is public and so is this file. Never commit secrets, tokens, private
  URLs, or absolute local paths.

## In flight

**→ [docs/next-steps.md](docs/next-steps.md) — start here.** Current status and
what to pick up next, linking out to the detail.

- [Pottery gallery](docs/pottery-gallery-plan.md) — a photo gallery at `/pottery`,
  planned but not started. Read that doc before touching anything
  pottery-related; it covers the image pipeline, why originals must stay out of
  git, and the EXIF/GPS stripping requirement.
- [Hosting & infrastructure](docs/hosting.md) — how the site is actually wired,
  plus a checklist of things still to confirm in the Netlify dashboard.
