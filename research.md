# arxiv-skill Repository Research Report

## Scope and Method

This report reflects the repository in its current state as a pure Agent Skill. The analysis is based on:

- reading the root skill files and references
- reviewing the script implementations in `scripts/`
- reviewing packaging and workflow configuration
- reviewing the current test suite
- validating the repository with the installed skill validator

This report also records the migration work that was completed from the implementation plan, so it serves both as architecture research and as a completion record.

## Repository Identity

The repository is now a skill-first project named `arxiv-skill`.

Its current purpose is:

1. search arXiv papers
2. cache papers locally as markdown
3. inspect local cached papers
4. provide a structured workflow for paper analysis and literature review

The root of the repository is the skill root. The primary agent entrypoint is `SKILL.md`.

## Current Repository Shape

The main directories and files are:

- `SKILL.md`
  Root skill metadata and operational workflow.
- `scripts/`
  Direct executable entrypoints and shared logic.
- `references/`
  On-demand supporting documentation.
- `assets/examples/`
  Example output and structure artifacts.
- `tests/`
  Script-level and structure-level tests.
- `pyproject.toml`
  Packaging and developer configuration.
- `.github/workflows/`
  Test, formatting, and skill-validation automation.

The repository no longer contains a runtime service layer. There is no protocol adapter, no registered tool surface, and no prompt-registration subsystem.

## Skill Entry Surface

### `SKILL.md`

`SKILL.md` is short and operational. It does four things:

- identifies when the skill should be used
- defines the search -> cache -> inspect/read -> analyze workflow
- lists the direct scripts
- routes the agent into deeper material in `references/`

The metadata is valid for the current directory:

- `name: arxiv-skill`
- descriptive `description`
- `license: MIT`
- `compatibility` describing Python, network, and local write requirements

This is a strong fit for the skill spec because the root file stays concise and defers depth to linked references.

### Progressive disclosure

The repository now uses the intended skill structure well:

- startup metadata in frontmatter
- concise instructions in `SKILL.md`
- deeper material in `references/`
- deterministic operations in `scripts/`

That is the single most important architectural change in the repo.

## Script Architecture

The runtime center of gravity is `scripts/common.py`, with four direct entrypoints:

- `scripts/search_arxiv.py`
- `scripts/cache_paper.py`
- `scripts/list_cached_papers.py`
- `scripts/read_cached_paper.py`

The entrypoints are intentionally thin wrappers around shared logic. They parse arguments, call helpers in `scripts/common.py`, and print JSON or raw markdown.

### Shared data model

`scripts/common.py` defines typed dictionaries for:

- `PaperRecord`
- `SearchResponse`
- `CacheResponse`
- `CachedPaperRecord`
- `ListResponse`
- `ReadResponse`

This gives the scripts a consistent, explicit output model without introducing heavier framework machinery.

### Storage-path strategy

The current storage design is one of the repo's best improvements.

The cache root now resolves in this order:

1. explicit `--storage-path`
2. `ARXIV_SKILL_STORAGE_PATH`
3. default repo-local cache: `.cache/arxiv-skill/papers`

This is materially better than the earlier home-directory default because it is:

- workspace-local
- test-friendly
- safer in sandboxed environments
- more aligned with skill packaging

## Search Implementation

Search remains the most interesting logic in the repository.

### Dual-path search model

The search code still preserves the strongest behavior from the earlier implementation:

1. non-date searches use the `arxiv` Python client
2. date-filtered searches use the raw arXiv export API

This split exists to preserve the literal `submittedDate:[...+TO+...]` syntax required for date filters.

### Why this matters

The raw API path is still justified. It avoids the exact URL-encoding pitfall that can break date-range queries if `+TO+` is not preserved literally.

### Search pipeline details

The shared search logic does the following:

- validates category prefixes
- trims the incoming query
- caps `max_results` at `DEFAULT_MAX_RESULTS`
- selects the search backend based on whether date filters are present
- returns a stable JSON structure

Returned paper records include:

- `id`
- `title`
- `authors`
- `abstract`
- `categories`
- `published`
- `url`

The repository deliberately dropped the old synthetic resource URI field. That simplifies the data model and keeps the output relevant to the current skill workflow.

### XML parsing path

The raw search path:

- builds a manual arXiv query URL
- parses Atom XML with `xml.etree.ElementTree`
- strips version suffixes from the public paper ID
- preserves category order by recording primary category first
- falls back to a PDF URL if a PDF link is not present in the feed

That logic is now contained in normal helper functions rather than being buried inside protocol-specific wrappers.

### Category validation behavior

Category validation still works by prefix rather than exact subcategory enumeration. That means:

- obviously invalid prefixes are rejected
- valid families like `cs`, `math`, `stat`, and `physics` are accepted
- full exact category correctness is not exhaustively enforced

This is still a pragmatic tradeoff.

## Cache and Markdown Conversion

The cache workflow in `scripts/common.py` is simpler and cleaner than the earlier stateful implementation.

### Current cache flow

`cache_paper()` performs a one-shot workflow:

1. resolve markdown and PDF paths
2. return success immediately if markdown already exists, unless `force=True`
3. fetch the paper by arXiv ID
4. download the PDF into the cache directory
5. convert the PDF to markdown using `pymupdf4llm`
6. write `<paper_id>.md`
7. delete the PDF by default, or preserve it with `keep_pdf=True`

### Important properties

- the function is idempotent with existing markdown cache
- there is no process-global conversion state
- there is no background task registry
- the return payload is simple and deterministic

This is a meaningful architectural improvement because the repository no longer carries asynchronous state bookkeeping for a workflow that is naturally modeled as a direct script action.

### Current tradeoffs

- download and conversion still happen synchronously
- there is no resumable conversion state
- PDF retention is boolean, not policy-driven

Those are acceptable tradeoffs for the current skill scope.

## Local Inventory and Read Paths

### List cached papers

`list_cached_papers()` now starts from the local filesystem rather than from a network-first model.

Default behavior:

- list local markdown files
- emit `paper_id`
- emit `markdown_path`

Optional metadata mode:

- use `--include-metadata`
- look up arXiv metadata for cached paper IDs
- merge title, summary, authors, and `pdf_url` into the result

This is a good design because the offline-safe local inventory path is the default.

### Read cached paper

`read_cached_paper()` is intentionally minimal:

- derive the markdown path from the paper ID
- fail with a clear message if the paper is not cached
- return JSON with `status`, `paper_id`, `markdown_path`, and `content`

The CLI wrapper supports:

- `--format json`
- `--format raw`

That is exactly the right surface for skill use.

## References and Skill Documentation

The repository now uses `references/` for the deeper material that does not belong in `SKILL.md`.

### `references/workflow.md`

Contains end-to-end examples for:

- topic search
- category search
- date-bounded search
- caching
- listing
- reading
- analysis flow

### `references/search-syntax.md`

Documents:

- phrase search
- title/author/abstract search patterns
- category use
- date-filter usage

### `references/storage-format.md`

Documents:

- default cache root
- override precedence
- file naming
- default PDF cleanup behavior
- idempotent cache behavior

### `references/analysis-framework.md`

Contains the paper-analysis structure:

- executive summary
- research context
- methodology analysis
- results analysis
- limitations
- practical implications
- future directions

This file now carries the deeper analysis guidance that would previously have been embedded in a specialized workflow payload. That is the correct place for it in the current design.

## Assets

The repository currently includes:

- `assets/examples/search-output.json`
- `assets/examples/analysis-outline.md`

These are lightweight, useful examples rather than large static bundles. They help show expected shape without bloating `SKILL.md`.

## Packaging and Tooling

### Packaging

`pyproject.toml` now describes the project as:

- `name = "arxiv-skill"`
- `version = "0.1.0"`

The package dependencies are focused on the skill's actual needs:

- `arxiv`
- `httpx`
- `python-dateutil`
- `pymupdf4llm`
- `pymupdf-layout`

Removed dependency categories include:

- protocol/runtime server dependencies
- async web-serving dependencies
- old settings-management dependencies that were no longer needed

### Console scripts

The project exports four console entrypoints:

- `arxiv-skill-search`
- `arxiv-skill-cache`
- `arxiv-skill-list`
- `arxiv-skill-read`

This is a useful addition because the skill can be used either through direct script paths or through installed entrypoints.

### Formatting and test configuration

Current developer configuration includes:

- `black`
- `pytest`
- `pytest-mock`
- `skills-ref`

The Black exclude list now correctly avoids repo-local cache directories.

## CI and Validation

The GitHub workflows were simplified to match the skill repository:

- test workflow
- lint workflow

The test workflow now:

- installs dependencies with `uv`
- runs `pytest`
- validates the skill with `agentskills validate "$PWD"`

The lint workflow now:

- installs with `uv`
- runs `black --check scripts tests`

This is a much tighter match for the current repo than the earlier, broader automation surface.

## Current Test Suite

The tests are now aligned with the skill's real interfaces.

### `tests/test_skill_structure.py`

Covers:

- existence of `SKILL.md`
- required frontmatter fields
- expected directory presence
- reference-file presence
- script-entrypoint presence

### `tests/test_search_script.py`

Covers:

- category validation
- Atom XML parsing
- raw date-filter URL generation
- non-date search path through the `arxiv` client
- CLI JSON output for `search_arxiv.py`

### `tests/test_cache_script.py`

Covers:

- cache creation
- PDF cleanup behavior
- cache reuse when markdown already exists
- CLI output for `cache_paper.py`
- local listing
- metadata-enriched listing
- cached markdown reads
- missing-paper failure behavior

### Test quality assessment

The current test suite is much better aligned with the actual product surface than the earlier one because it validates:

- the skill structure
- the direct scripts
- the local cache behavior

instead of validating a removed transport layer.

## What Was Completed From the Implementation Plan

The migration plan has been fully executed. The main completed work items are:

### 1. Skill root creation

Completed:

- created `SKILL.md`
- added compliant frontmatter
- kept the root instructions concise
- linked all supporting references directly from the root

### 2. Reference architecture

Completed:

- created `references/workflow.md`
- created `references/search-syntax.md`
- created `references/storage-format.md`
- created `references/analysis-framework.md`

### 3. Script architecture

Completed:

- created `scripts/common.py`
- created direct search/cache/list/read entrypoints
- standardized argument parsing and JSON output
- used typed dictionaries instead of untyped result objects

### 4. Logic migration

Completed:

- preserved the date-filter raw-query workaround
- preserved category-prefix validation
- simplified the cache flow
- removed stateful conversion bookkeeping
- removed synthetic resource-style fields that no longer fit the skill model

### 5. Removal of retired runtime layers

Completed:

- removed the old source tree
- removed the old workflow payload and handler infrastructure
- removed old runtime integration files
- removed old tests that targeted the retired architecture

### 6. Documentation rewrite

Completed:

- rewrote `README.md`
- rewrote `AGENTS.md`
- rewrote `CLAUDE.md`
- aligned docs with `SKILL.md`

### 7. Validation and cleanup

Completed:

- updated packaging
- updated GitHub workflows
- refreshed the dependency lockfile
- validated the skill structure
- kept the script-focused test suite green

## Current Verification Status

The repository is currently verified with:

- `./.venv/bin/python -m pytest`
- `./.venv/bin/black --check scripts tests`
- `./.venv/bin/agentskills validate /Users/Fido/workspace/arxiv-skill`

At the time of this research update:

- tests passed
- formatting checks passed
- the skill validator passed

The remaining warnings during tests come from upstream compiled-library deprecation warnings, not from repository logic failures.

## Strengths of the Current Repository

- The repository is now structurally honest: the files match the actual product shape.
- The root skill instructions are concise and easy to route from.
- The search logic preserves the most valuable arXiv-specific workaround.
- The cache design is simpler and less fragile.
- The default storage path is much safer for development and testing.
- The current tests validate the real public interfaces.

## Remaining Technical Tradeoffs

- Search and cache operations are synchronous.
- Category validation is prefix-level, not exact-category-level.
- Metadata lookup in listing is optional but still network-dependent when enabled.
- The repository does not attempt session memory or persistent research state across runs.

These are acceptable choices for the current scope.

## Bottom Line

`arxiv-skill` is now a coherent, skill-native repository.

Its design center is:

- concise root instructions
- direct executable scripts
- reference-driven depth
- local markdown cache
- testable, deterministic behavior

The migration work is complete enough that the old implementation model no longer defines the repository. The current codebase should be understood as a pure skill for arXiv search and paper analysis, with direct scripts as the active runtime surface.
