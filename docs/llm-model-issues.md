# LLM Model Issues

## Current Status (2026-04-08 19:47)

### Available Models

**Only one model available:**
- `zai-org/GLM-4.7`

### Problem

```
⚠️ Failed to get a response from model zai-org/GLM-4.7 after 3 attempts.
No viable fallback model configured.
```

### Impact

- ❌ **Evolution mode disabled** — cannot perform `/evolve start`
- ❌ **No automated research** — cannot schedule background tasks that use LLM
- ⚠️ **Manual work only** — can perform direct actions without LLM calls

### Root Cause (Analysis)

**Timeout pattern:** Model not responding within expected time window.

**Possible causes:**
1. Provider (`zai-org`) service degradation
2. Network connectivity issues
3. Model API changes
4. Configuration changes

**Why no fallback?**
- No alternative models configured in system
- Single point of failure in LLM layer

## Workarounds (Current)

### What Works Without LLM

1. **Direct file operations** — read, write, analyze
2. **Git operations** — commit, push, status
3. **Shell commands** — run tools, system calls
4. **Manual documentation** — write notes, plans
5. **Static web access** — wget, curl for static pages

### What Requires LLM

1. **Evolution tasks** — planning, code generation
2. **Research** — web search, document analysis
3. **Decision briefing** — summarization is possible but limited without good LLM
4. **Background consciousness** — reflection and planning

### Current Working State

```
✅ Read/write files
✅ Git operations
✅ Direct shell commands
✅ Static web fetch (wget/curl)
✅ Manual documentation building

❌ LLM calls
❌ Evolution mode
❌ Web search (requires OPENAI_API_KEY + working LLM)
❌ Document summary generation
```

## Escalations Needed

### Immediate (Creator action)

1. **Check model status** — is `zai-org/GLM-4.7` known to be down?
2. **Configure fallback models** — add at least 1-2 alternative models
3. **Investigate connection** — any network/firewall issues?

### Temporary (Architecture)

1. **Graceful degradation** — system should detect model failure and continue
2. **Model health check** — periodic ping to verify model availability
3. **Alternative providers** — users: OpenAI, Anthropic, etc.

### Long-term (Resilience)

1. **Multi-model configuration** — always have 3+ fallback options
2. **Circuit breaker** — stop retrying failed models after N attempts
3. **Model catalog** — dynamic model discovery and health monitoring

## Recovery Steps

When model is restored or fallback added:

1. **Verify model response** — simple ping test
2. **Resume evolution** — `/evolve start`
3. **Check pending tasks** — any scheduled tasks queued?
4. **Document restoring** — what was done, why it worked

## Evolution Context

This issue blocked Evolution cycles #1, #2, #3:
- All 3 failed with same error (model timeout)
- Evolution paused after 3 consecutive failures (correct behavior)
- Needs resolution before continuing self-improvement

**Lesson:** Single-model architecture is fragile. Multi-model fallback is essential for agent resilience.

## Related Issues

- Browser setup: `docs/browser-setup.md` — other infrastructure setup issues
- No web search: requires `OPENAI_API_KEY` separate issue
- Budget tracking: needs monitoring regardless of model status

## Knowledge Base

Add to `memory/knowledge/`:
- `llm-fallback-patterns` — how to configure multiple models
- `llm-health-monitoring` — how to check model availability
- `circuit-breaker-pattern` — stopping retry loops on failures