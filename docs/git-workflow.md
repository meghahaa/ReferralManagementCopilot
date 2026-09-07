# Git Workflow & Branching Strategy

This document describes the branching model, commit conventions, and repository contribution guidelines for the Referral Management Copilot.

---

## 1. Branching Strategy

The repository follows a feature-branch workflow:
- **`main`**: Production-ready, stable codebase.
- **`feature/*`**: Feature branches for discrete functional milestones (e.g. `feature/data-and-config`, `feature/langgraph-agents`, `feature/mcp-memory-rag`).

---

## 2. Pull Request & Merge Guidelines

- All feature implementations are merged into `main` using non-fast-forward merges (`git merge --no-ff`).
- Direct commits to `main` without PR review are restricted.

---

## 3. Commit Message Conventions

Commit messages follow standard Conventional Commits formatting:
- `feat(scope)`: New features or components (e.g. `feat(mcp): add custom FastMCP server`).
- `fix(scope)`: Bug fixes (e.g. `fix(graph): resolve checkpointer thread_id requirement`).
- `test(scope)`: Unit tests and evidence logs (e.g. `test(memory): add cross-session persistence test`).
- `docs(scope)`: Documentation updates (e.g. `docs(architecture): add single-vs-multi agent rationale`).
