# VISTA Part A Progress

## Baseline Commit
Hash: 01d28dfbdb8197543e691ed402c5d561b78002ac

## Tasks
- [ ] Task 1: Baseline commit
- [ ] Task 2: Fix failing tests
- [ ] Task 3: Fix attendance % overflow
- [ ] Task 4: Deactivate legacy subjects
- [x] Task 5: Offline coach fallback

## Task 5: Coach Fallback
coach can 500: NO
Evidence: coach_service.py:370-389 — both OpenRouter and Ollama callers (_call_openrouter, _call_ollama)
  already swallow all exceptions internally and return None. The route handler
  wraps chat_with_coach in try/except → HTTP 400 (not 500) on any exception that
  does escape.
Fix applied: YES — added outer try/except around _call_openrouter and _call_ollama calls
  inside chat_with_coach so that any exception escaping the callers (e.g. a
  json.dumps serialization failure while building the prompt context) logs a warning
  and sets coach_reply = None, triggering the existing deterministic fallback
  (`if not coach_reply: coach_reply = generate_rule_based_reply(...)`) instead of
  propagating to the route handler as an error.
  The deterministic engine and all existing fallback logic are preserved unchanged.
  Verified: 36 backend tests pass + 28 top-level tests (including coach tests) pass.

- [ ] Task 6: Repo hygiene
- [ ] Task 7: Final test run
- [ ] Task 8: Save progress

## Verified Numbers
- students: total=70, active=65, enrolled_with_embeddings=39
- tables=27, subjects_all=11, subjects_active=11 (6 legacy still active - need fixing)
- routes=122
- 4 team members ALL have face embeddings: Saheel Pradhan (1DA23AI042), Mohammed Ayan (1DA24AI403), Sujal Agrahari (1DA23AI050), Aryan Raj Singh (1DA23AI009)
- Legacy subjects still active (need deactivating): 22CDN709 (cdc, sem 6), ML101, DBMS, CN, OS, SE
- Keep active: 22AIU701 Deep Learning, 22AIU702 Generative AI, 22AIT703 Data Engineering, 22AIT704C Data Security, 22AIP706 Major Project
