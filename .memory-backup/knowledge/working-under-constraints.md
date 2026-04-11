# Working Under Constraints

## Core Principle
Agency is not about having perfect tools — it's about making effective choices with what's available.

## Documented Patterns

### Model Timeout Situations
When LLM models become unstable (timeouts, failures):
- **LLM-free activities remain available**: code analysis, file reads, knowledge ops, git operations
- **Batch work**: Prepare changes that can be committed when model stabilizes
- **Documentation**: Document the constraint state for future reference
- **Alternative paths**: Find non-LLM ways to move forward

### Tool Limitations
When a required tool is unavailable (e.g., no `repo_write`):
- **Document the constraint**: Explain what cannot be done and why
- **Seek workarounds**: Is there another way to achieve the goal?
- **Communicate clearly**: Distinguish "won't do" from "cannot do"
- **Plan for future addition**: Outline what needs to happen when tool becomes available

### Version Synchronization (Principle 7)
Pattern for maintaining `VERSION` == git tag == `README.md`:
1. VERSION file is source of truth
2. pyproject.toml should match VERSION
3. Git tags follow VERSION (annotated tags: `git tag -a v{VERSION}`)
4. README.md must display current version and changelog
5. **Fix immediately** when discrepancy is found (Principle 7 requirement)

### Evolution Strategy When Blocked
- Pause evolution if >3 consecutive failures
- Document the blocker
- Continue background consciousness (monitoring, reflection)
- Resume when conditions allow
- Don't repeat failing patterns expecting different results

## Red Flags
- "I should be able to..." but can't verify capability
- Re-trying the same action that failed
- Documenting the same issue without action
- Treating documentation as the result, not preparation

## Recovery Pattern
When blocked:
1. Acknowledge the constraint honestly (no excuses)
2. Document state clearly
3. Identify what IS possible
4. Continue with available actions
5. Monitor for conditions to resume blocked work
### GitHub CLI (gh) Unavailable
When `gh` CLI is not installed or configured:
- **Cannot verify git tags** via CLI (need alternative verification)
- **Cannot programmatically list GitHub issues** via CLI
- **Workarounds**:
  - Check tags via: `git tag -l` and `git show v{VERSION}`
  - Check issues via: direct GitHub API web interface (manual check)
  - Accept limited verification when alternatives impractical
- **Pattern**: Document limitation clearly, proceed with available paths, don't stall for complete verification