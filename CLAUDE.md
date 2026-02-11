# CLAUDE.md

## Project Overview

**kldata** is a data repository for Key Lab. It is currently in an early stage with minimal structure.

## Repository Structure

```
kldata/
├── CLAUDE.md       # AI assistant guidance (this file)
└── README.md       # Project description
```

## Current State

- The repository contains no application code, build tooling, tests, or CI/CD configuration.
- There is no `.gitignore` file configured.
- The sole branch with content history is `master`.

## Development Workflows

### Git

- **Remote**: `origin` (GitHub via `caminsar/kldata`)
- **Primary branch**: `master`
- No branch protection rules, CI checks, or automated pipelines are configured.

### Build / Test / Lint

No build system, test framework, or linter is set up. When tooling is added in the future, update this section with:
- How to install dependencies
- How to build the project
- How to run tests (`test`, `test:unit`, `test:integration`, etc.)
- How to lint and format code

## Conventions

### Commit Messages

Follow standard conventions: use imperative mood, keep the subject line under 72 characters, and provide context in the body when needed.

### Adding Code or Data

When adding new content to this repository:
1. Add a `.gitignore` appropriate for the language/framework being used.
2. Set up linting and formatting from the start.
3. Update this `CLAUDE.md` file to reflect the new structure and workflows.

## Notes for AI Assistants

- This is a data-oriented repository; do not assume it follows typical application patterns.
- Always read existing files before proposing changes.
- Keep changes minimal and focused.
- Update this file whenever significant structural changes are made to the repository.
