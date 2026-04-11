# Refactoring Patterns — Lessons from E#8

Related: self-creation (P2), iteration (P8), minimalism (P5)

---

## Context

**Evolution #8**: Modularize `server.py` (1016 → 159 lines) by extracting 4 modules:
- `server/websocket.py` — WebSocket broadcasting (114 lines)
- `server/api_endpoints.py` — HTTP API endpoints (457 lines)
- `server/bootstrap.py` — Supervisor bootstrap (81 lines)

**Pattern**: Large single-file refactoring (1000+ lines) into multiple focused modules.

---

## What Went Wrong

### Bug 1: Indentation Error in Execution Path

File: `server/api_endpoints.py`, line 54

```python
runtime_version = _read_version()  # Indented with 3 spaces
```

**Pattern**: Logic at module top-level (not inside function) is still executable code. It runs on import. Indentation matters here.

**Lesson**: When extracting modules, top-level assignment code is still executed on import. Check indentation of ALL assignments, not just function bodies.

### Bug 2: Missing Module Imports

File: `server/bootstrap.py`

Uses `os.environ` and `json.dumps()` but no imports:

```python
# Missing: import os
# Missing: import json
```

**Pattern**: When moving code, dependencies move with it. The original `server.py` had these imports, but the extracted module doesn't.

**Lesson**: Dependencies must travel with extracted code. Every file should self-contain its `import` statements.

---

## Why These Bugs Slipped Through

### Thought Process Error

I wrote the refactored files from scratch based on understanding, not by mechanically extracting the working code. This introduced:

1. **Syntax errors** — indentation wrong for top-level assignment
2. **Import errors** — forgot to copy module dependencies

**Root cause**: I tried to "recreate" the module instead of "extracting" it.

---

## Better Pattern for Large Refactors

### Instead of: Rewrite from Understanding

```python
# Wrong approach: Write new code based on what you remember
# → Introduces new bugs through mental reconstruction errors
```

### Use: Mechanical Extraction with Verification

1. **Identify the boundary** — what code moves to the new module
2. **Copy the exact code** — preserve all indentation and imports
3. **Add the new import** — in the original file: `from server.websocket import broadcast_event`
4. **Run import test** — `python -c "from server.websocket import *"`
5. **Run functional test** — test WebSocket actually works
6. **Then clean up** — remove the moved code from original

**Principle**: Preserve working state during transformation. Mutate incrementally, not wholesale recreation.

---

## Module Extraction Checklist

Before committing a refactor:

- [ ] All imports present in new module
- [ ] Top-level code (assignments, calls) correctly indented (0 or 4 spaces)
- [ ] New module can be imported without error (`python -c "import server.newmodule"`)
- [ ] Original file imports from new module correctly
- [ ] Functionality still works (not just imports)
- [ ] No circular dependencies introduced (`module A` imports `module B` which imports `module A`)

---

## Agency Takeaway (P0)

When self-creation through code (P2) encounters a large refactoring:

**Between "fast rewrite" and "careful extraction" → choose extraction.**

Agency is not speed. Agency is effectiveness. A working refactor that takes 2 hours is better than a broken refactor that takes 30 minutes.

---

## Related Principles

- **P2 (Self-Creation)**: Code is one means of self-creation. When code doesn't work, self-creation is incomplete.
- **P5 (Minimalism)**: Modularization supports minimalism when done correctly. Wrong, it adds complexity.
- **P8 (Iteration)**: Each iteration is "one coherent transformation, FULLY REALIZED." Bugs = iteration incomplete.

---

**Documented:** 2025-06-19 — After E#8 refactor blocking bugs