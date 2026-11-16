"""
VISTA — Resilient LLM Client with Model Fallback & Circuit Breaker
====================================================================
Replaces the naive 2-attempt urllib loop in coach_service._call_openrouter().

Features:
- Configurable model priority chain (env: LLM_MODEL_CHAIN)
- Transient-error detection (HTTP 429, 502, 503, 504)
- Google MODEL_CAPACITY_EXHAUSTED (error 2010) → immediate model switch
- Exponential backoff with random jitter, respecting Retry-After
- Per-model circuit breaker (5-min cooldown after consecutive failures)
- Sanitized structured logging (no API keys, no PII)
- Returns None when all models are exhausted → deterministic fallback
"""
from __future__ import annotations

import json
import logging
import os
import random
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

logger = logging.getLogger("vista.llm_resilience")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_DEFAULT_MODEL_CHAIN = (
    "nvidia/nemotron-3.5-super-vl:free,"
    "google/gemini-2.5-flash,"
    "google/gemini-2.0-flash-001,"
    "google/gemini-1.5-flash,"
    "meta-llama/llama-3.3-70b-instruct:free"
)

_TRANSIENT_STATUS_CODES = frozenset({429, 502, 503, 504})

_MAX_RETRIES_PER_MODEL = 2
_BASE_BACKOFF_SECS = 1.0
_MAX_BACKOFF_SECS = 16.0
_JITTER_RANGE_SECS = 1.0
_REQUEST_TIMEOUT_SECS = 30
_CIRCUIT_BREAKER_COOLDOWN_SECS = 300  # 5 minutes


# ---------------------------------------------------------------------------
# Circuit Breaker (per-model)
# ---------------------------------------------------------------------------
@dataclass
class _ModelCircuit:
    """Tracks consecutive failures for a single model."""
    consecutive_failures: int = 0
    tripped_at: float = 0.0              # time.monotonic() when breaker opened
    capacity_exhausted: bool = False      # Google error 2010 flag

    @property
    def is_open(self) -> bool:
        if self.consecutive_failures < _MAX_RETRIES_PER_MODEL and not self.capacity_exhausted:
            return False
        elapsed = time.monotonic() - self.tripped_at
        if elapsed >= _CIRCUIT_BREAKER_COOLDOWN_SECS:
            # Half-open: allow a probe
            return False
        return True

    def record_failure(self, *, capacity_exhausted: bool = False) -> None:
        self.consecutive_failures += 1
        self.capacity_exhausted = capacity_exhausted
        self.tripped_at = time.monotonic()

    def record_success(self) -> None:
        self.consecutive_failures = 0
        self.capacity_exhausted = False
        self.tripped_at = 0.0


# Module-level breaker state (process-lifetime; acceptable for single-process
# FastAPI + uvicorn deployment used by VISTA).
_circuits: dict[str, _ModelCircuit] = {}


def _get_circuit(model: str) -> _ModelCircuit:
    if model not in _circuits:
        _circuits[model] = _ModelCircuit()
    return _circuits[model]


# ---------------------------------------------------------------------------
# Response helpers
# ---------------------------------------------------------------------------
@dataclass
class LLMResult:
    """Structured result from a resilient LLM call."""
    text: str | None
    model_used: str | None
    provider: str                      # "openrouter" | "fallback"
    attempts: int = 0
    fallback_chain: list[str] = field(default_factory=list)
    error_summary: str | None = None


def _safe_model_name(model: str) -> str:
    """Return the model identifier safe for logging (no secrets)."""
    return model


def _extract_retry_after(response: httpx.Response) -> float | None:
    """Parse Retry-After header or Google retryDelay from JSON body."""
    # Standard header
    ra = response.headers.get("retry-after")
    if ra:
        try:
            return float(ra)
        except ValueError:
            pass

    # Google-style JSON body with retryDelay
    try:
        body = response.json()
        for detail in body.get("error", {}).get("details", []):
            delay_str = detail.get("retryDelay", "")
            if delay_str.endswith("s"):
                return float(delay_str[:-1])
    except Exception:
        pass

    return None


def _is_capacity_exhausted(response: httpx.Response) -> bool:
    """Detect Google MODEL_CAPACITY_EXHAUSTED (error 2010)."""
    if response.status_code != 503:
        return False
    try:
        body = response.json()
        err = body.get("error", {})
        if err.get("code") == 2010:
            return True
        if "MODEL_CAPACITY_EXHAUSTED" in err.get("message", ""):
            return True
        # OpenRouter wraps Google errors in its own JSON
        if "capacity" in json.dumps(body).lower():
            return True
    except Exception:
        pass
    return False


def _compute_backoff(attempt: int, retry_after: float | None) -> float:
    """Exponential backoff with jitter, capped, respecting Retry-After."""
    exp_delay = min(_MAX_BACKOFF_SECS, _BASE_BACKOFF_SECS * (2 ** attempt))
    jitter = random.uniform(0, _JITTER_RANGE_SECS)
    delay = exp_delay + jitter
    if retry_after is not None:
        # If the server suggests a long delay (e.g. 58 s) we do NOT wait that
        # long; instead we switch models immediately.  But for short delays
        # (≤ max_backoff) we honour them.
        if retry_after <= _MAX_BACKOFF_SECS:
            delay = max(delay, retry_after + jitter)
    return delay


# ---------------------------------------------------------------------------
# Core: single-model attempt
# ---------------------------------------------------------------------------
def _try_model(
    *,
    model: str,
    messages: list[dict],
    api_key: str,
    base_url: str,
    temperature: float,
    max_tokens: int,
    extra_body: dict | None = None,
) -> tuple[str | None, int]:
    """
    Try a single model up to _MAX_RETRIES_PER_MODEL times.
    Returns (text | None, attempts_used).
    Raises nothing — all errors are caught and logged.
    """
    circuit = _get_circuit(model)
    if circuit.is_open:
        logger.info(
            "Circuit breaker OPEN for model=%s (consecutive_failures=%d, "
            "capacity_exhausted=%s). Skipping.",
            _safe_model_name(model),
            circuit.consecutive_failures,
            circuit.capacity_exhausted,
        )
        return None, 0

    url = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://vista.academic",
        "X-Title": "VISTA Study Coach",
    }

    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if extra_body:
        payload.update(extra_body)

    attempts = 0
    for attempt in range(_MAX_RETRIES_PER_MODEL):
        attempts += 1
        try:
            with httpx.Client(timeout=_REQUEST_TIMEOUT_SECS) as client:
                resp = client.post(url, json=payload, headers=headers)

            # ---- Success ----
            if resp.status_code == 200:
                try:
                    result = resp.json()
                    choice = result.get("choices", [{}])[0]
                    msg_obj = choice.get("message") or {}
                    text = (msg_obj.get("content") or "").strip()
                    if not text and msg_obj.get("reasoning"):
                        text = msg_obj["reasoning"].strip()
                    if text:
                        circuit.record_success()
                        logger.info(
                            "LLM success: model=%s attempt=%d",
                            _safe_model_name(model), attempt + 1,
                        )
                        return text, attempts
                except Exception as parse_exc:
                    logger.warning(
                        "LLM response parse error: model=%s error=%s",
                        _safe_model_name(model), parse_exc,
                    )

            # ---- Capacity Exhausted → skip remaining retries ----
            if _is_capacity_exhausted(resp):
                logger.warning(
                    "MODEL_CAPACITY_EXHAUSTED: model=%s status=%d. "
                    "Opening circuit breaker, switching model.",
                    _safe_model_name(model), resp.status_code,
                )
                circuit.record_failure(capacity_exhausted=True)
                return None, attempts

            # ---- Other transient errors → backoff & retry ----
            if resp.status_code in _TRANSIENT_STATUS_CODES:
                retry_after = _extract_retry_after(resp)
                delay = _compute_backoff(attempt, retry_after)
                logger.warning(
                    "Transient error: model=%s status=%d attempt=%d/%d "
                    "retry_after=%.1f backoff=%.1f",
                    _safe_model_name(model), resp.status_code,
                    attempt + 1, _MAX_RETRIES_PER_MODEL,
                    retry_after or -1, delay,
                )
                circuit.record_failure()
                if attempt < _MAX_RETRIES_PER_MODEL - 1:
                    time.sleep(delay)
                continue

            # ---- Permanent errors (401, 403, 404, 422…) → no retry ----
            logger.error(
                "Permanent error: model=%s status=%d body=%s",
                _safe_model_name(model), resp.status_code,
                resp.text[:300],
            )
            circuit.record_failure()
            return None, attempts

        except httpx.TimeoutException:
            logger.warning(
                "Timeout: model=%s attempt=%d/%d",
                _safe_model_name(model), attempt + 1, _MAX_RETRIES_PER_MODEL,
            )
            circuit.record_failure()
        except httpx.RequestError as net_exc:
            logger.warning(
                "Network error: model=%s attempt=%d/%d error=%s",
                _safe_model_name(model), attempt + 1, _MAX_RETRIES_PER_MODEL,
                net_exc,
            )
            circuit.record_failure()

    return None, attempts


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def get_model_chain() -> list[str]:
    """
    Return the ordered model priority chain from environment or defaults.
    The first model in the list is the primary.
    """
    raw = os.environ.get("LLM_MODEL_CHAIN", "").strip()
    if not raw:
        # Honour the legacy OPENROUTER_MODEL env var as primary
        primary = os.environ.get("OPENROUTER_MODEL", "").strip()
        chain = [m.strip() for m in _DEFAULT_MODEL_CHAIN.split(",") if m.strip()]
        if primary and primary not in chain:
            chain.insert(0, primary)
        elif primary and primary in chain:
            # Move to front
            chain.remove(primary)
            chain.insert(0, primary)
        return chain
    return [m.strip() for m in raw.split(",") if m.strip()]


def resilient_chat_completion(
    *,
    messages: list[dict],
    api_key: str | None = None,
    base_url: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 500,
    extra_body: dict | None = None,
    model_chain: list[str] | None = None,
) -> LLMResult:
    """
    Call the OpenRouter chat-completions endpoint with automatic model
    fallback, circuit breaking, and structured observability.

    Returns an LLMResult.  If .text is None every model in the chain failed
    and the caller should use the deterministic rule engine.
    """
    if api_key is None:
        api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if base_url is None:
        base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")

    if not api_key or api_key == "your_openrouter_api_key_here":
        logger.info("OpenRouter API key not configured. Returning None for deterministic fallback.")
        return LLMResult(
            text=None, model_used=None, provider="fallback",
            error_summary="API key not configured",
        )

    chain = model_chain or get_model_chain()
    total_attempts = 0
    tried_models: list[str] = []

    for model in chain:
        tried_models.append(model)
        text, attempts = _try_model(
            model=model,
            messages=messages,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_body=extra_body,
        )
        total_attempts += attempts

        if text:
            if model != chain[0]:
                logger.info(
                    "Fallback succeeded: primary=%s used=%s after %d total attempts",
                    _safe_model_name(chain[0]), _safe_model_name(model),
                    total_attempts,
                )
            return LLMResult(
                text=text,
                model_used=model,
                provider="openrouter",
                attempts=total_attempts,
                fallback_chain=tried_models,
            )

        logger.info(
            "Model %s exhausted. Trying next in chain (%d/%d).",
            _safe_model_name(model),
            tried_models.index(model) + 1,
            len(chain),
        )

    # All models failed
    logger.error(
        "All %d models in chain exhausted after %d total attempts. "
        "Falling back to deterministic rule engine. chain=%s",
        len(chain), total_attempts,
        [_safe_model_name(m) for m in chain],
    )
    return LLMResult(
        text=None,
        model_used=None,
        provider="fallback",
        attempts=total_attempts,
        fallback_chain=tried_models,
        error_summary=f"All {len(chain)} models exhausted",
    )


# ---------------------------------------------------------------------------
# Testing helpers
# ---------------------------------------------------------------------------
def reset_all_circuits() -> None:
    """Clear all circuit breaker state. For tests only."""
    _circuits.clear()


def get_circuit_status(model: str) -> dict[str, Any]:
    """Return circuit breaker state for a model. For diagnostics/tests."""
    c = _get_circuit(model)
    return {
        "model": model,
        "consecutive_failures": c.consecutive_failures,
        "is_open": c.is_open,
        "capacity_exhausted": c.capacity_exhausted,
    }
