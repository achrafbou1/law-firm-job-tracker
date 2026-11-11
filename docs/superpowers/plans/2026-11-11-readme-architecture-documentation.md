# README Architecture and Documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a colored Mermaid architecture diagram and make README.md accurate, navigable, and useful for setup, operations, testing, and extension.

**Architecture:** Documentation-only change centered on README.md. The diagram will represent the existing runtime flow from APScheduler and `src.main` through Airtable configuration, the scraper factory, Apify-backed ATS adapters, filtering/diff tracking, Airtable persistence, and SendGrid notifications. No application behavior or dependencies will change.

**Tech Stack:** Markdown, GitHub Mermaid flowcharts, Python 3.13, uv, Docker, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-11-11-readme-architecture-design.md`

## Global Constraints

- Use a colored Mermaid diagram rendered directly in `README.md`; do not add image assets or documentation tooling.
- Preserve existing commands, environment variables, Airtable field names, supported behavior, and development guidance unless corrected against repository evidence.
- Document only behavior supported by the current source, `Makefile`, `Dockerfile`, and `.github/workflows/main.yml`.
- Make no application-code or runtime behavior changes.

## Review Focus

- Mermaid rendering: diagram syntax and `classDef` styles must render correctly on GitHub.
- ATS coverage: Workday, Greenhouse, and SmartRecruiters must be listed consistently with `src/factories.py`.
- Repository layout: the tree must match actual tracked source files and avoid claiming nonexistent files.
- Commands: README commands must correspond to actual Makefile targets and current `uv`/Docker entry points.
- Configuration/deployment: environment variables, `DEBUG_EMAIL`, `ENV=test`, `RUN_ONCE`, and DigitalOcean deployment wording must match source and CI.

---

### Task 1: Audit and restructure README content

**Files:**
- Modify: `README.md`
- Read: `Makefile`, `pyproject.toml`, `Dockerfile`, `.github/workflows/main.yml`, `src/main.py`, `src/settings.py`, `src/factories.py`

**Interfaces:**
- Consumes: Existing README content and verified repository behavior.
- Produces: An accurate README section structure that later receives the architecture diagram.

- [ ] **Step 1: Update the opening documentation**

Keep the project purpose and feature list concise, and add a table of contents or clear heading hierarchy for the major workflows: architecture, supported ATS platforms, requirements, installation, configuration, Airtable setup, usage, operations, testing, extension, troubleshooting, and contributing.

- [ ] **Step 2: Correct stale or incomplete repository claims**

Update the supported ATS table to include SmartRecruiters and its implementation path/actor information where available. Correct the source tree to include `smartrecruiters.py`, `schemas/greenhouse.py`, and `schemas/smartrecruiters.py`; describe Airtable classes as `pyairtable` ORM models; and remove or correct any tree entries not present in the repository.

- [ ] **Step 3: Align setup and command examples with the repository**

Retain the valid `make` shortcuts only where they correspond to `Makefile` targets, show the direct `uv run`/Docker alternatives accurately, and document the actual Docker module entry point (`python -m src.main`). Keep Python `>=3.13`, `uv`, and the current dependency/setup requirements.

- [ ] **Step 4: Align configuration and deployment documentation**

Document `DEBUG_EMAIL` as an optional setting, retain `LAW_FIRM_DB_ID`, `RUN_ONCE`, and `ENV=test` with their actual defaults/behavior, and add a concise Operations/Deployment section describing the GitHub Actions test gate and DigitalOcean Docker deployment without exposing secrets.

- [ ] **Step 5: Add troubleshooting guidance**

Add targeted entries for missing/invalid credentials, unsupported ATS values, no email being sent when no NEW/CLOSED jobs match filters, test environment selection, and Docker/runtime startup issues. Phrase each item as a symptom and repository-supported check.

- [ ] **Step 6: Verify documentation references**

Search README.md for every command, environment variable, ATS name, source path, and deployment claim and compare it with the relevant repository files. Confirm no secrets or fake required values are introduced.

- [ ] **Step 7: Commit**

```bash
git add README.md
git commit -m "docs: audit and restructure README"
```

### Task 2: Add the colored architecture diagram and data-flow explanation

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: The corrected section structure and runtime relationships verified in Task 1.
- Produces: A GitHub-rendered Mermaid architecture diagram and matching concise explanation.

- [ ] **Step 1: Add a Mermaid architecture flowchart**

Place it under `## Architecture`. Show internal nodes for scheduler/entry point, Airtable client/configuration, scraper factory, ATS scraper adapters, validation/filtering/diff tracking, Airtable persistence, and email service; show external nodes for law-firm career pages/Apify, Airtable, and SendGrid. Use `classDef` styles with accessible contrasting colors and a legend or labels that distinguish application components, external services, and data-processing stages.

- [ ] **Step 2: Add the data-flow narrative**

Explain the one-shot and scheduled paths: load active firms and role keywords, choose a scraper by ATS, scrape through Apify, persist all statuses, filter NEW/CLOSED jobs by keywords and country, and send a summary only when relevant jobs exist. Note the staggered scheduler behavior without presenting it as user-configurable if it is not.

- [ ] **Step 3: Validate diagram and documentation**

Check Mermaid syntax manually against GitHub flowchart syntax, ensure every diagram node matches current code, and run the repository’s smallest documentation-relevant quality check if one exists. Review the final diff to ensure only documentation and the approved design/plan artifacts changed.

- [ ] **Step 4: Commit**

```bash
git add README.md docs/superpowers/specs/2026-11-11-readme-architecture-design.md docs/superpowers/plans/2026-11-11-readme-architecture-documentation.md
git commit -m "docs: add colored architecture diagram"
```
