# Model Troubleshooting & Recovery Guide

## Quick Assessment

**Symptom:** Model requests producing "timeout" or "Failed to get response after N attempts"

## Diagnostic Steps

### Step 1: Check Which Model Is Timing Out
- **RU:** vem-variable时间为0
    
- Check `~/Ouroboros/data/state/state.json` to see the currently configured models:

```json
{
  "model_main": "zai-org/GLM-4.7",
  "model_code": "zai-org/GLM-4.7", 
  "model_light": "zai-org/GLM-4.7",
  "model_fallback": "zai-org/GLM-4.7",
  "model_web_search": "zai-org/GLM-4.7"
}
```

**Diagnosis:**
- ✅ Same model across all slots? This is **SPOF** (Single Point of Failure)
- ✅ Timeouts on specific slots (e.g., main but code works)? Model capacity issue

### Step 2: Verify LLM Client Configuration

Check `ourootboros/config.py`:

- Look for `DEFAULT_MODELS` dictionary

- Verify timeout settings exist:
  - `LLM_TIMEOUT` (default: 30 seconds)
  - `MAX_RETRIES` (default: 3 attempts)

### Step 3: Check System Connectivity

```bash
# Test Cloud.ru API endpoint
curl -I https://llm.api.cloud.ru/v1/models

# Test authentication
curl -X POST https://llm.api.cloud.ru/v1/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"zai-org/GLM-4.7","messages":[{"role":"user","content":"test"}],"max_tokens":5}'
```

**If endpoint unreachable:** Cloud.ru outage or network issue — wait and retry

**If 401/403:** API invalid or expired — check `CLOUDRU_API_KEY` in system environment

### Step 4: Examine `ollama.log` (if using local models)

If local model active, check Ollama logs:

```bash
# If running locally via Ollama
tail -f ~/Library/Logs/ollama.log  # macOS

# Test model directly
ollama list
ollama run modelname
```

## Configuration Recommendations

### ✅ Best Practice: Model Diversity

Configure different models for different slots to avoid SPOF:

```json
{
  "model_main": "zai-org/GLM-4.7",
  "model_code": "zai-org/GLM-4.7",
  "model_light": "ai-sage/GigaChat3-10B-A1.8B",  // [LOWER-COST], but different
  "model_fallback": "zai-org/GLM-4.7",
  "model_web_search": "zai-org/GLM-4.7"
}
```

**Why:**
- If main model times out, fallback to lighter/faster model
- Group unrelated failures (main vs light) - can isolate problems

### ✅ Increase Timeouts for Complex Tasks

In `config.py`:
```python
# Default timeouts (adjust for your environment)
LLM_TIMEOUT = 30000        # 30 seconds for standard LLM calls
LLM_TIMEOUT_LONG = 120000  # 120 seconds for code generation (optional, add this)
LLM_TIMEOUT_CONSCIOUSNESS = 15000  # 15 seconds for consciousness loops (faster, simpler)
```

Routing logic in `loop.py`:
```python
timeout_ms = long_boot_cfg.get('view_point', {}).pop('LLM_TIMEOUT', LLM_TIMEOUT)
if is_code_generation:
    timeout_ms = config.LLM_TIMEOUT_LONG  # Longer for code generation
elif is_consciousness:
    timeout_ms = config.LLM_TIMEOUT_CONSCIOUSNESS  # Shorter for background loops
```

### ✅ Add Retry Logic to Key Components

If `MAX_RETRIES` is not yet in `loop.py` implement:

```python
from typing import Callable, Any, Optional
import logging
import asyncio

async def retry_with_backoff(
    operation: Callable[[], Any],
    max_retries: int = 3,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    operation_name: str = "operation"
) -> Optional[Any]:
    """Attempt operation with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return await operation()
        except TimeoutError as e:
            if attempt < max_retries - 1:
                delay = base_delay * (backoff_factor ** attempt)
                log.warning(f"{operation_name} timed out (attempt {attempt+1}/{max_retries}), retrying in {delay:.1f}s...")
                await asyncio.sleep(delay)
            else:
                log.error(f"{operation_name} failed after {max_retries} attempts")
                raise
        except Exception as e:
            log.error(f"{operation_name} failed with unexpected error: {e}")
            raise
```

Integration in `get_completion`:
```python
async def get_completion(self, *args, **kwargs) -> Dict[str, Any]:
    if 'timeout_ms' in kwargs:
        timeout_seconds = kwargs['timeout_ms'] / 1000.0
        kwargs['timeout_ms'] = timeout_seconds * 1000  # convert to ms for Cloud.ru API
    
    async def operation():
        return await self._call_cloud_api(*args, **kwargs)
    
    return await retry_with_backoff(operation, max_retries=self.config.MAX_RETRIES, operation_name="LLM call")
```

## Recovery Procedures

### Scenario 1: Temporary Cloud Model Unavailable

**Symptoms:**
- Requests timeout on Cloud.ru models
- Endpoint unreachable or 500/503 errors

**Actions:**
1. Check Cloud.ru status page (if available)
2. Wait and retry (usually resolves within minutes)
3. If persists >30min, consider switching models

**To switch models via UI:**
- Settings → Models → Configure new model for failing slot
- If new model unknown, test field to provider API directly

### Scenario 2: API Key Issues

**Symptoms:**
- 401 Unauthorized
- 403 Forbidden
- "Invalid API key" errors

**Actions:**
1. Verify `CLOUDRU_API_KEY` in system environment
2. Check key hasn't expired
3. In Settings → Accounts → Regenerate API key (if expired)
4. Restart application after key update

### Scenario 3: Network/Prohibited Hosts

**Symptoms:**
- Connection refused
- DNS resolution errors
- "Prohibited host" errors (if Cloud.ru blocking)

**Actions:**
1. Check system network proxies
`ping llm.api.cloud.ru`
`nslookup llm.api.cloud.ru`

2. Verify not blocked by firewall/content filters
3. If using corporate VPN/proxy, add exception for Cloud.ru

### Scenario 4: Local Model Slow/Timeout

**Symptoms:**
- Ollama takes 30+ seconds to respond
- Memory pressure causing timeouts
- System sluggishness

**Action:**
```bash
# Troubleshoot Ollama
ollama ps  # Check if model is loaded
top -o mem # Check memory usage
```

Possible fixes:
1. Reduce context window: limit to ~2000 tokens max
2. Switch to smaller model: e.g., GigaChat3-10B vs GigaChat4-7B
3. Close other memory-intensive applications
4. Consider cloud model if local is too slow

### Scenario 5: Persistent Unreliability

**Symptoms:**
- Same model fails consistently over days
- Patterns: always same time of day (rate limits?), always same slots

**Possible Causes:**
- Cloud.ru rate limiting
- Model under high load

**Actions:**
1. Pattern analysis: log failures to determine if time-based or load-based
2. Contact Cloud.ru support if issue persists >1 hour
3. Add off-peak fallback models: e.g., use light model during peak hours
4. Request higher rate limits if needed

## Prevention

### ✅ Health Checks

Implement periodic health check in background consciousness:

```python
async def health_check_loop():
    while True:
        await asyncio.sleep(300)  # Every 5 minutes
        try:
            client = LLMClient()
            start = time.time()
            result = await client.get_completion([{"role": "user", "content": "ping"}], max_tokens=1)
            latency = (time.time() - start) * 1000
            log.info(f"Model health check: OK ({latency:.0f}ms)")
        except Exception as e:
            log.error(f"Model health check failed: {e}")
            # Could trigger notification to user if N consecutive failures
```

### ✅ Automatic Model Failover

If multiple models configured, implement failover logic:

```python
def get_model_for_slot(slot_name: str) -> str:
    """Return working model for requested slot."""
    models = get_configured_models_for_slot(slot_name)
    for model_name in models:
        if is_model_healthy(model_name):
            return model_name
    raise Exception("No healthy models available for slot: " + slot_name)
```

### ✅ Request Queuing and Throttling

If rate limiting is suspected:

```python
from asyncio import Semaphore

MAX_CONCURRENT_REQUESTS = 3  # Adjust based on model limits
request_semaphore = Semaphore(MAX_CONCURRENT_REQUESTS)

async def rate_limited_llm_call(prompt, **kwargs):
    async with request_semaphore:
        return await llm_client.get_completion(prompt, **kwargs)
```

## Log Locations for Debugging

| Component | Log Location |
|-----------|--------------|
| LLM requests | `~/Ouroboros/data/logs/tools.jsonl` |
| Agent loops | `~/Ouroboros/data/logs/events.jsonl` |
| Supervisor events | `~/Ouroboros/data/logs/supervisor.jsonl` |
| Ollama (if used) | Platform-specific (see above) |

## When to Contact Cloud.ru Support

Contact if:
1. Persistent 500/503 errors >1 hour with no resolution
2. API suddenly returns 401/403 on valid key
3. All models in account failing simultaneously
4. Unexpected billing/usage spikes

**Information to provide:**
- Model name(s) failing
- Timestamps of failures
- Request/response samples (with API key masked)
- Cloud.ru account ID

## Testing Model Configuration

After making configuration changes:

```python
# Test each slot
 slots = ["main", "code", "light", "fallback", "web_search"]
 for slot in slots:
    model = get_model_for_slot(slot)
    try:
        result = await llm_client.get_completion([{"role": "user", "content": "test"}], model=model, max_tokens=1)
        print(f"{slot}: OK using model '{model}'")
    except Exception as e:
        print(f"{slot}: FAILED using model '{model}' — {e}")
```

## Summary Checklist

- [ ] Verify which model is timing out (all slots or just specific ones?)
- [ ] Check `~/Ouroboros/data/state/state.json` configured models
- [ ] Test Cloud.ru API endpoint directly
- [ ] Verify API key validity
- [ ] Check for rate limiting patterns (time-based or volume-based)
- [ ] Consider diversifying models across slots to avoid SPOF
- [ ] Adjust timeouts for specific operations (code generation vs quick queries)
- [ ] Add retry/backoff logic if not present
- [ ] Document the issue for future reference

---

**Last updated:** 2026-04-08 (Evolution Cycle #4 - Model SPOF Analysis)