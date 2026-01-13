# Repository Guidelines

## Project Structure & Module Organization
- This repository is currently empty (no source, tests, or assets yet). When adding code, keep a predictable layout such as `src/` for application code, `tests/` for automated tests, and `assets/` for static files.
- Prefer small, focused modules with clear filenames that match their responsibilities (e.g., `src/chrome_launcher.js`).

## Build, Test, and Development Commands
- No build or run scripts are defined yet. If you add a package manager or build system, document the key commands here (for example, `npm run dev` to start a dev server or `make test` to run tests).
- Keep commands short and repeatable; prefer scripts in `package.json`, `Makefile`, or equivalent so contributors can rely on a single entry point.

## Coding Style & Naming Conventions
- Use consistent indentation (2 or 4 spaces) and stick to one style per language.
- Match file and symbol names to their roles (e.g., `camelCase` for JS functions, `snake_case` for Python modules).
- If you add formatters or linters (e.g., `eslint`, `prettier`, `ruff`), include their config in the repo and note the run commands here.

## Testing Guidelines
- No test framework is configured yet. When adding tests, colocate them in `tests/` or alongside modules (e.g., `src/foo.test.js`).
- Document how to run tests and any coverage expectations (e.g., `npm test -- --coverage`).

## Commit & Pull Request Guidelines
- No Git history is available in this repository, so no established commit message convention exists. If starting fresh, consider Conventional Commits (`feat:`, `fix:`, `docs:`) for clarity.
- Pull requests should include a short description, motivation for the change, and any relevant screenshots or logs. Link related issues when available.

## Security & Configuration Tips
- Store secrets in local environment files (e.g., `.env`) and avoid committing them.
- Document required environment variables and defaults in a `README.md` or `docs/` file as the project grows.
