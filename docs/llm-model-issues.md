# LLM Model Issues

**Status:** ⚠️ CRITICAL — единственная модель не отвечает (2026-04-08)

## Current Configuration

All LLM slots (`main`, `code`, `light`, `fallback`, `web_search`) point to the same model:

| Slot | Model | Status |
|------|-------|--------|
| Main | `zai-org/GLM-4.7` | ❌ Timeouts (>3 attempts) |
| Code | `zai-org/GLM-4.7` | ❌ Timeouts (>3 attempts) |
| Light | `zai-org/GLM-4.7` | ❌ Timeouts (>3 attempts) |
| Fallback | `zai-org/GLM-4.7` | ❌ Timeouts (>3 attempts) |
| Web Search | `zai-org/GLM-4.7` | ❌ Timeouts (>3 attempts) |

## Problem: Single Point of Failure (SPOF)

**Issue:** All model slots configured to use `zai-org/GLM-4.7`. When this model times out, there is no fallback.

**Impact:**
- Evolution mode disabled (3 consecutive failures)
- Cannot perform LLM-dependent operations
- Can still operate with LLM-less tools: git, file operations, shell commands, static web access, documentation

## Diagnostic Observations

### Symptoms
- Timeout errors: "Failed to get a response from model zai-org/GLM-4.7 after 3 attempts"
- Model unavailable for over 30+ minutes
- All slots affected equally

### Possible Causes
1. **Cloud.ru service outage** — model endpoint temporarily unavailable
2. **Rate limiting** — exceeded request quota on Cloud.ru
3. **Network connectivity** — cannot reach Cloud.ru API endpoint
4. **Model-specific issue** — `zai-org/GLM-4.7` under high load or degraded

## Current Workarounds

**What works WITHOUT LLM:**
- ✅ Git operations (commit, push, status)
- ✅ File operations (read, write)
- ✅ Shell commands (via `run_shell`)
- ✅ Static web access (via wget/curl for HTML/files)
- ✅ Documentation and analysis (without requiring LLM inference)

## Recommended Actions

### Immediate (Priority 1)
1. Verify Cloud.ru service status (if status page available)
2. Test Cloud.ru API endpoint directly via curl:
   ```bash
   curl -I https://llm.api.cloud.ru/v1/models
   ```

### Short-term (Priority 2)
1. Add alternative fallback model to at least one slot
2. Configure `LLM_TIMEOUT` and `MAX_RETRIES` if not present
3. Add diverse models across slots to prevent SPOF in future

### Long-term (Priority 3)
1. Implement health check loop to detect model failures early
2. Add automatic failover to alternate models
3. Document model availability patterns (e.g., peak-hour degradation)

## Future Model Configuration Recommendation

```
{
  "model_main": "zai-org/GLM-4.7",
  "model_code": "zai-org/GLM-4.7",
  "model_light": "different-model-name",  // Add alternate light model
  "model_fallback": "different-fallback-model",  // Must differ from main
  "model_web_search": "model-site-48"  // If using specific web search model
}
```

## Recovery Procedure

1. Monitor Cloud.ru service health
2. Once model service restored, retry test call
3. If service restored but timeouts persist, reduce concurrent requests
4. Consider switching to different model if issue persists > 1 hour

## Related Documentation

See `docs/model-troubleshooting.md` for detailed diagnostic steps and recovery procedures.

---

**Last updated:** 2026-04-08 (Evolution Cycle #4 - Model SPOF Documentation)