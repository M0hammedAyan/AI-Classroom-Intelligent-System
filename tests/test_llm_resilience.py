"""
VISTA — Tests for Resilient LLM Client (llm_resilience.py)
============================================================
Covers:
  1. Successful primary model request.
  2. HTTP 503 MODEL_CAPACITY_EXHAUSTED → immediate fallback to next model.
  3. HTTP 429 rate-limit → retry with backoff, then fallback.
  4. HTTP 401 permanent error → no infinite loop, immediate stop.
  5. All models exhausted → graceful None return.
  6. Circuit breaker opens after consecutive failures.
  7. Circuit breaker half-open probe after cooldown.
  8. Retry-After header is respected.
  9. Google retryDelay JSON body is parsed.
  10. Model chain configuration from environment.
  11. Primary model recovery after circuit breaker cooldown.
"""
from __future__ import annotations

import json
import os
import time
from unittest.mock import patch, MagicMock

import httpx
import pytest

# Ensure llm_resilience can be imported standalone
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))
from vista.backend.app.services.llm_resilience import (
    resilient_chat_completion,
    reset_all_circuits,
    get_circuit_status,
    get_model_chain,
    _extract_retry_after,
    _is_capacity_exhausted,
    _compute_backoff,
    _get_circuit,
    _CIRCUIT_BREAKER_COOLDOWN_SECS,
    _MAX_RETRIES_PER_MODEL,
    LLMResult,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def clean_circuits():
    """Reset circuit breaker state before each test."""
    reset_all_circuits()
    yield
    reset_all_circuits()


@pytest.fixture
def api_key():
    return "sk-test-key-not-real"


@pytest.fixture
def test_messages():
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello"},
    ]


@pytest.fixture
def simple_chain():
    return ["model-a", "model-b", "model-c"]


def _success_response(content: str = "Test reply") -> httpx.Response:
    """Build a mock 200 response with a valid chat completion body."""
    body = json.dumps({
        "choices": [{"message": {"content": content}}],
    })
    resp = httpx.Response(200, text=body, headers={"content-type": "application/json"})
    return resp


def _error_response(status: int, body: dict | None = None, headers: dict | None = None) -> httpx.Response:
    """Build a mock error response."""
    body_text = json.dumps(body or {})
    h = {"content-type": "application/json"}
    if headers:
        h.update(headers)
    return httpx.Response(status, text=body_text, headers=h)


def _capacity_exhausted_response() -> httpx.Response:
    """Google MODEL_CAPACITY_EXHAUSTED 503 response."""
    body = {
        "error": {
            "code": 2010,
            "message": "MODEL_CAPACITY_EXHAUSTED",
            "status": "UNAVAILABLE",
            "details": [{"retryDelay": "58s"}],
        }
    }
    return _error_response(503, body)


# ===========================================================================
# Test 1: Successful primary model request
# ===========================================================================
class TestSuccessfulRequest:
    def test_primary_model_success(self, api_key, test_messages, simple_chain):
        with patch("vista.backend.app.services.llm_resilience.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = _success_response("Hello student!")

            result = resilient_chat_completion(
                messages=test_messages,
                api_key=api_key,
                model_chain=simple_chain,
            )

        assert result.text == "Hello student!"
        assert result.model_used == "model-a"
        assert result.provider == "openrouter"
        assert result.attempts == 1
        assert result.error_summary is None

    def test_reasoning_field_fallback(self, api_key, test_messages, simple_chain):
        """If content is empty but reasoning exists, use reasoning."""
        body = json.dumps({
            "choices": [{"message": {"content": "", "reasoning": "Thought process"}}],
        })
        resp = httpx.Response(200, text=body, headers={"content-type": "application/json"})

        with patch("vista.backend.app.services.llm_resilience.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = resp

            result = resilient_chat_completion(
                messages=test_messages,
                api_key=api_key,
                model_chain=simple_chain,
            )

        assert result.text == "Thought process"


# ===========================================================================
# Test 2: HTTP 503 MODEL_CAPACITY_EXHAUSTED → immediate model switch
# ===========================================================================
class TestCapacityExhausted:
    def test_503_triggers_immediate_fallback(self, api_key, test_messages, simple_chain):
        """First model returns 503 capacity exhausted, second model succeeds."""
        responses = [
            _capacity_exhausted_response(),  # model-a
            _success_response("Fallback reply"),  # model-b
        ]

        with patch("vista.backend.app.services.llm_resilience.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.post.side_effect = responses

            result = resilient_chat_completion(
                messages=test_messages,
                api_key=api_key,
                model_chain=simple_chain,
            )

        assert result.text == "Fallback reply"
        assert result.model_used == "model-b"
        assert result.provider == "openrouter"
        assert len(result.fallback_chain) == 2
        assert result.fallback_chain == ["model-a", "model-b"]

    def test_503_opens_circuit_breaker(self, api_key, test_messages, simple_chain):
        """After 503, the circuit breaker for model-a should be open."""
        with patch("vista.backend.app.services.llm_resilience.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.post.side_effect = [
                _capacity_exhausted_response(),
                _success_response("OK"),
            ]

            resilient_chat_completion(
                messages=test_messages,
                api_key=api_key,
                model_chain=simple_chain,
            )

        status = get_circuit_status("model-a")
        assert status["is_open"] is True
        assert status["capacity_exhausted"] is True


# ===========================================================================
# Test 3: HTTP 429 rate-limit → retry then fallback
# ===========================================================================
class TestRateLimiting:
    def test_429_retries_then_falls_back(self, api_key, test_messages, simple_chain):
        """429 on model-a retries then falls back to model-b."""
        responses = [
            _error_response(429, {"error": "rate limited"}, {"retry-after": "1"}),  # model-a attempt 1
            _error_response(429, {"error": "rate limited"}),  # model-a attempt 2
            _success_response("After rate limit"),  # model-b
        ]

        with patch("vista.backend.app.services.llm_resilience.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.post.side_effect = responses

            with patch("vista.backend.app.services.llm_resilience.time.sleep") as mock_sleep:
                result = resilient_chat_completion(
                    messages=test_messages,
                    api_key=api_key,
                    model_chain=simple_chain,
                )

        assert result.text == "After rate limit"
        assert result.model_used == "model-b"
        assert result.attempts >= 3
        # Verify backoff sleep was called
        assert mock_sleep.call_count >= 1


# ===========================================================================
# Test 4: HTTP 401 permanent error → no retry, no infinite loop
# ===========================================================================
class TestPermanentError:
    def test_401_stops_immediately(self, api_key, test_messages):
        """401 on all models → returns None, no retry loops."""
        chain = ["model-a", "model-b"]
        responses = [
            _error_response(401, {"error": "unauthorized"}),
            _error_response(401, {"error": "unauthorized"}),
        ]

        with patch("vista.backend.app.services.llm_resilience.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.post.side_effect = responses

            result = resilient_chat_completion(
                messages=test_messages,
                api_key=api_key,
                model_chain=chain,
            )

        assert result.text is None
        assert result.provider == "fallback"
        # Each model should be tried exactly once (no retry for 401)
        assert result.attempts == 2
        assert "exhausted" in result.error_summary.lower()


# ===========================================================================
# Test 5: All models exhausted → graceful None
# ===========================================================================
class TestAllModelsExhausted:
    def test_all_fail_returns_none(self, api_key, test_messages, simple_chain):
        """Every model in the chain fails → deterministic fallback."""
        with patch("vista.backend.app.services.llm_resilience.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.post.side_effect = [
                _capacity_exhausted_response(),  # model-a
                _capacity_exhausted_response(),  # model-b
                _capacity_exhausted_response(),  # model-c
            ]

            result = resilient_chat_completion(
                messages=test_messages,
                api_key=api_key,
                model_chain=simple_chain,
            )

        assert result.text is None
        assert result.model_used is None
        assert result.provider == "fallback"
        assert len(result.fallback_chain) == 3


# ===========================================================================
# Test 6: Circuit breaker skips tripped models
# ===========================================================================
class TestCircuitBreaker:
    def test_skips_open_circuit(self, api_key, test_messages, simple_chain):
        """If model-a's circuit is already open, it's skipped immediately."""
        circuit = _get_circuit("model-a")
        circuit.record_failure(capacity_exhausted=True)

        with patch("vista.backend.app.services.llm_resilience.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = _success_response("Skipped model-a")

            result = resilient_chat_completion(
                messages=test_messages,
                api_key=api_key,
                model_chain=simple_chain,
            )

        # model-a is skipped, model-b answers
        assert result.model_used == "model-b"
        assert result.text == "Skipped model-a"

    def test_circuit_half_open_after_cooldown(self, api_key, test_messages, simple_chain):
        """After cooldown, circuit becomes half-open and allows a probe."""
        circuit = _get_circuit("model-a")
        circuit.record_failure(capacity_exhausted=True)
        # Simulate cooldown expiry by setting tripped_at far in the past
        circuit.tripped_at = time.monotonic() - _CIRCUIT_BREAKER_COOLDOWN_SECS - 1

        with patch("vista.backend.app.services.llm_resilience.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.post.return_value = _success_response("Recovered!")

            result = resilient_chat_completion(
                messages=test_messages,
                api_key=api_key,
                model_chain=simple_chain,
            )

        # model-a should be probed and succeed (half-open → closed)
        assert result.model_used == "model-a"
        assert result.text == "Recovered!"
        status = get_circuit_status("model-a")
        assert status["is_open"] is False
        assert status["consecutive_failures"] == 0


# ===========================================================================
# Test 7: Retry-After header parsing
# ===========================================================================
class TestRetryAfterParsing:
    def test_retry_after_header(self):
        resp = _error_response(429, {}, {"retry-after": "3"})
        assert _extract_retry_after(resp) == 3.0

    def test_google_retry_delay_json(self):
        resp = _error_response(503, {
            "error": {"details": [{"retryDelay": "58s"}]}
        })
        assert _extract_retry_after(resp) == 58.0

    def test_no_retry_after(self):
        resp = _error_response(500, {})
        assert _extract_retry_after(resp) is None


# ===========================================================================
# Test 8: Capacity exhaustion detection
# ===========================================================================
class TestCapacityDetection:
    def test_detects_error_code_2010(self):
        resp = _error_response(503, {"error": {"code": 2010, "message": "err"}})
        assert _is_capacity_exhausted(resp) is True

    def test_detects_message_string(self):
        resp = _error_response(503, {"error": {"message": "MODEL_CAPACITY_EXHAUSTED"}})
        assert _is_capacity_exhausted(resp) is True

    def test_non_503_is_not_capacity(self):
        resp = _error_response(429, {"error": {"code": 2010}})
        assert _is_capacity_exhausted(resp) is False


# ===========================================================================
# Test 9: Backoff computation
# ===========================================================================
class TestBackoffComputation:
    def test_exponential_growth(self):
        d0 = _compute_backoff(0, None)
        d1 = _compute_backoff(1, None)
        d2 = _compute_backoff(2, None)
        # Each should be roughly double the base (within jitter)
        assert d1 > d0 * 0.8
        assert d2 > d1 * 0.8

    def test_respects_short_retry_after(self):
        delay = _compute_backoff(0, 5.0)
        assert delay >= 5.0

    def test_ignores_long_retry_after(self):
        """58-second retry-after should NOT block; we switch models instead."""
        delay = _compute_backoff(0, 58.0)
        assert delay < 20.0  # Should not be 58+


# ===========================================================================
# Test 10: Model chain configuration
# ===========================================================================
class TestModelChainConfig:
    def test_default_chain(self):
        with patch.dict(os.environ, {"OPENROUTER_MODEL": "nvidia/nemotron-3.5-super-vl:free"}, clear=False):
            chain = get_model_chain()
        assert chain[0] == "nvidia/nemotron-3.5-super-vl:free"
        assert len(chain) >= 3

    def test_custom_chain_from_env(self):
        with patch.dict(os.environ, {"LLM_MODEL_CHAIN": "alpha,beta,gamma"}, clear=False):
            chain = get_model_chain()
        assert chain == ["alpha", "beta", "gamma"]


# ===========================================================================
# Test 11: No API key → immediate fallback
# ===========================================================================
class TestMissingApiKey:
    def test_no_key_returns_fallback(self, test_messages):
        result = resilient_chat_completion(
            messages=test_messages,
            api_key="",
            model_chain=["model-a"],
        )
        assert result.text is None
        assert result.provider == "fallback"
        assert "not configured" in result.error_summary.lower()

    def test_placeholder_key_returns_fallback(self, test_messages):
        result = resilient_chat_completion(
            messages=test_messages,
            api_key="your_openrouter_api_key_here",
            model_chain=["model-a"],
        )
        assert result.text is None
        assert result.provider == "fallback"


# ===========================================================================
# Test 12: Timeout handling
# ===========================================================================
class TestTimeoutHandling:
    def test_timeout_retries_then_falls_back(self, api_key, test_messages, simple_chain):
        with patch("vista.backend.app.services.llm_resilience.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.post.side_effect = [
                httpx.ReadTimeout("timed out"),  # model-a attempt 1
                httpx.ReadTimeout("timed out"),  # model-a attempt 2
                _success_response("After timeout"),  # model-b
            ]

            result = resilient_chat_completion(
                messages=test_messages,
                api_key=api_key,
                model_chain=simple_chain,
            )

        assert result.text == "After timeout"
        assert result.model_used == "model-b"


# ===========================================================================
# Test 13: Network error handling
# ===========================================================================
class TestNetworkError:
    def test_connection_error_falls_back(self, api_key, test_messages, simple_chain):
        with patch("vista.backend.app.services.llm_resilience.httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client_cls.return_value.__enter__ = MagicMock(return_value=mock_client)
            mock_client_cls.return_value.__exit__ = MagicMock(return_value=False)
            mock_client.post.side_effect = [
                httpx.ConnectError("connection refused"),
                httpx.ConnectError("connection refused"),
                _success_response("After network fix"),
            ]

            result = resilient_chat_completion(
                messages=test_messages,
                api_key=api_key,
                model_chain=simple_chain,
            )

        assert result.text == "After network fix"
        assert result.model_used == "model-b"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
