# README Architecture Diagram and Documentation Design

## Intent

Make the repository easier to understand for new users and contributors by
adding a colored, GitHub-rendered architecture diagram and organizing the
README around setup, operation, and extension workflows.

## Goals

- Show the end-to-end job discovery flow from scheduled execution to
  notifications and Airtable persistence.
- Distinguish application components from external services with Mermaid
  colors.
- Make the README answer the most common onboarding and maintenance questions
  without duplicating implementation details.

## Non-goals

- No application-code or runtime behavior changes.
- No new diagram image assets or documentation tooling.
- No claims about deployment infrastructure beyond what the repository already
  supports.

## Approaches

1. **Colored Mermaid in `README.md` (selected):** native GitHub rendering,
   versioned with the documentation, searchable, and easy to update.
2. **Standalone SVG/PNG:** more pixel-level visual control, but adds an asset
   that is harder to review and maintain.
3. **ASCII diagram:** maximally portable, but cannot satisfy the color
   requirement and communicates less structure.

## Design

Add a Mermaid flowchart under the Architecture section. It will show:

- APScheduler and the application entry point.
- Airtable configuration retrieval and job persistence.
- The scraper factory and ATS-specific Apify-backed scrapers.
- Validation, filtering, and diff tracking.
- SendGrid email notifications.
- External services styled separately from internal components.

Restructure related README content into these sections:

- Overview and features
- Architecture and data flow
- Supported ATS platforms
- Requirements and installation
- Configuration
- Airtable setup
- Usage and operations
- Testing and quality checks
- Extending the scraper
- Troubleshooting
- Contributing and license

Keep existing commands, environment variables, supported platforms, Airtable
schema, and development guidance accurate while removing redundant explanations
where the new sections cover the same material.
