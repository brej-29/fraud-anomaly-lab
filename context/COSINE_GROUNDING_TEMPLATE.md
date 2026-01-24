# Cosine Grounding Template

This template defines **non-negotiable grounding rules** for any future work in this repository. Every new task, PR, or feature should start by following these steps.

---

## 1) Read `context/*.md` First

Before writing code or changing files:

1. Read (or re-read) the key context documents:
   - `context/GOAL.md`
   - `context/COMPONENTS.md`
   - `context/DECISIONS.md`
   - `context/METRICS.md`
   - `context/ACCEPTANCE_CRITERIA.md`
2. Ensure your changes align with:
   - The project’s **goal** and constraints (free-only, HF Spaces + Streamlit).
   - The current **architecture** (ML → artifacts → FastAPI → dashboard).
   - The documented **metrics, thresholds, and decision rationale**.

---

## 2) Don’t Invent Files That Don’t Exist

When implementing a task:

- Use the existing folder structure; **do not** create new top-level directories unless explicitly justified and documented.
- Before introducing a new module or file:
  - Check if a similar helper or component exists (e.g., in `shared/`, `ml/`, or `backend/`).
  - Reuse and extend existing code where reasonable.
- If you must add a new file:
  - Make sure it fits the existing naming and style conventions.
  - Document any significant new component in:
    - `context/COMPONENTS.md` (architecture),
    - and/or `context/DECISIONS.md` (rationale).

---

## 3) Update `ACCEPTANCE_CRITERIA.md` When Adding Features

Every meaningful feature or milestone should:

1. Add or update checklist items in `context/ACCEPTANCE_CRITERIA.md`.
2. Mark items as completed only when:
   - The feature is implemented.
   - Basic tests pass locally (and ideally in CI).
   - Documentation and/or comments are updated where appropriate.

Think of `ACCEPTANCE_CRITERIA.md` as the **single source of truth** for project progress.

---

## 4) Prefer Simple, Testable Code; Add Logging + Exception Handling

When implementing logic:

- Favor **small, composable functions** with clear responsibilities.
- Add **unit tests** for critical paths (e.g., data preprocessing, model scoring, API endpoints).
- Use **structured logging**:
  - Log at appropriate levels (info, warning, error).
  - Include enough context for debugging without leaking sensitive data.
- Use **basic, targeted exception handling**:
  - Catch specific, expected exceptions (e.g., missing files, malformed inputs).
  - Return or log actionable error messages.
  - Avoid blanket `except Exception:` handlers that silently hide errors.

---

## How to Use This Template

For any new task:

1. Start by stating:  
   **"I have read the context documents in `context/` and will follow `COSINE_GROUNDING_TEMPLATE.md`."**
2. Confirm which acceptance criteria you aim to satisfy or extend.
3. Implement changes with simplicity, tests, and logging in mind.
4. Update:
   - `context/ACCEPTANCE_CRITERIA.md`
   - and relevant context docs (`DECISIONS.md`, `COMPONENTS.md`, etc.) as needed.

This discipline keeps the project **coherent, maintainable, and aligned** with its original goals.