# CLAUDE.md

Guidance for Claude Code (and other AI assistants) working in this repository.

## Project overview

Despite the repo name, this is **not** a deep-learning/ML codebase. It's a small,
self-contained **bilingual (English / 中文) study tool for ISO 13485:2016**, the
medical device quality management system (QMS) standard. The app presents all 69
clauses of the standard as interactive cards with three study modes: Browse,
Flashcard (spaced repetition), and Quiz.

Title shown in-app: "ISO 13485:2016 · QMS 学习手册".

## Architecture

The entire application is **one file**: `index.html` (~1,335 lines). There is:

- No build step, no bundler, no transpiler.
- No package manager / dependency file (no `package.json`, no `requirements.txt`, etc.).
- No external JS/CSS libraries — vanilla HTML/CSS/JS only.
- One external dependency: Google Fonts, loaded via `<link>` tags in `<head>`
  (Fraunces, Inter, IBM Plex Mono).

`index.html` contains inline `<style>` and `<script>` blocks rather than separate
asset files. Treat it as the single source of truth for markup, styling, and logic.

## Code map (within `index.html`)

Approximate regions (line numbers will drift as the file changes — use them as a
starting orientation, not a guarantee):

- **`<head>` / meta** (~1-13): title, description, font links, theme-color.
- **CSS** (~14-421): custom properties define the palette and switch between
  light/dark via `html[data-theme="dark"]` (`--paper`, `--ink`, `--teal`,
  `--amber`, etc.), plus CSS Grid layout for the card view.
- **HTML markup** (~1-541, interleaved with CSS): header, nav/filter bar, card
  grid, flashcard overlay, quiz modal.
- **Data layer** (~548-967):
  - `CLAUSES` — array of 69 clause objects, each with `ref`, `cat`, `en`, `zh`,
    `intentEn`, `intentZh`, `reqs[]` (key requirements), and `audit` (what
    auditors look for).
  - `CATS` — 7 category groupings used for filtering/navigation.
- **UI logic** (~992-1071): search/filter, category pills, language toggle
  (EN / 中文 / bilingual), theme toggle.
- **Study modes** (~1073-1307):
  - **Browse** — flip-card reading interface.
  - **Flashcard / spaced repetition** — SM-2 scheduling algorithm, progress
    persisted to `localStorage` under key `iso13485_sr_v1`.
  - **Quiz** — four question types (intent→clause, audit→clause, ref→title,
    title→ref).

## Development workflow

There is nothing to install or compile. To preview changes:

```bash
# simplest: open directly in a browser
xdg-open index.html   # or just open the file in any browser

# or serve it (needed if testing things sensitive to file:// origin issues)
python3 -m http.server
```

There are **no tests and no linter configured**. Don't invent a test/lint command
that doesn't exist — verify changes manually in a browser:

- Exercise all three modes (Browse, Flashcard, Quiz).
- Check both languages (EN, 中文, and bilingual mode).
- Check both themes (light and dark).
- Confirm search/filter and category pills still work.

## Deployment

`.github/workflows/pages.yml` deploys to GitHub Pages on every push to `main`
(or manual `workflow_dispatch`). It does **not** run a build — it publishes the
repo root as-is via `actions/upload-pages-artifact`. This means anything
committed to `main` is what ships; there's no staging/build transformation step.

## Conventions

- Keep this a dependency-free, single-file app unless there's a strong reason to
  split it up — the simplicity is intentional, not an oversight.
- When editing or adding clause data in `CLAUSES`, maintain English/Chinese
  parity: every `en` needs a matching `zh`, every `intentEn` needs a matching
  `intentZh`. Don't add English-only or Chinese-only content.
- When touching CSS, preserve the existing light/dark theme variable pattern
  (define values in `:root` and override in `html[data-theme="dark"]`) rather
  than hardcoding colors.
- The clause data encodes real regulatory content from ISO 13485:2016
  (requirements, audit focus areas). Edits to `CLAUSES` should be checked for
  accuracy against the actual standard, not just for code correctness — wrong
  regulatory content is worse than a bug.
