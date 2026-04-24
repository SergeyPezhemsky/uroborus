"""
Ouroboros — LLM tool loop.

Core loop: send messages to LLM, execute tool calls, repeat until final response.
Extracted from agent.py to keep agent.py as thin orchestrator (Principle 5: Minimalism).
"""

import asyncio
import json
import logging
import os
import sys
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, TypedDict, Union

from pydantic import BaseModel, ValidationError

# Internal imports
from ouroboros.llm import get_llm
from ouroboros.context import Context


# ============================================================================
# CONSTANTS
# ============================================================================

logger = logging.getLogger(__name__)


# Conservative pricing estimates for Cloud.ru Foundation Models
# NOTE: These are CONSERVATIVE ESTIMATES pending official Cloud.ru pricing docs
# Sources checked: https://cloud.ru/docs/foundation-models/ug/topics/pricing (2026-12-07)
# Last verified: Pricing not publicly documented in accessible static docs
#
# These estimates are set HIGH to avoid surprise budget depletion. 
# Actual cost is likely lower. Update when official pricing is confirmed.
_MODEL_PRICING_STATIC = {
    # zai-org/GLM-4.7 - Main production model
    # Format: (input_rub_per_1M_tokens, cached_rub_per_1M_tokens, output_rub_per_1M_tokens)
    # Conservative estimate based on comparable Chinese production LLMs (GLM-4, Qwen, etc.)
    "zai-org/GLM-4.7": (25.0, 8.0, 75.0),  # Estimated: ₽25/1M in, ₽8/1M cached, ₽75/1M out (3:1 ratio typical)
    
    # ai-sage/GigaChat3-10B-A1.8B - Smaller model
    "ai-sage/GigaChat3-10B-A1.8B": (15.0, 5.0, 45.0),  # Estimated: ₽15/1M in, ₽5/1M cached, ₽45/1M out (3:1 ratio)
    
    # Default pricing for unknown models (conservative)
    "default": (30.0, 10.0, 90.0),
}


# ============================================================================