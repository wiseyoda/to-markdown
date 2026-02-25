---
phase: 0080
name: smart-features
status: not_started
created: 2026-02-25
updated: 2026-02-25
---

# Phase 0080: Smart Features (LLM Integration)

**Goal**: Implement LLM-powered enhancement flags that add intelligence to the conversion
output using Google Gemini 3.0 Flash.

**Scope**:
- Set up Gemini API client with .env-based API key management
- Implement --summary flag: generates a concise document summary prepended to output
- Implement --images flag: describes images/charts using Gemini vision
- Implement --toc flag: auto-generates table of contents from headings
- Graceful degradation: clear error if API key missing, suggest setup
- Rate limiting / cost awareness (log token usage)
- Mock LLM responses in tests

**Deliverables**:
- [ ] Gemini API client wrapper (google-genai SDK)
- [ ] --summary flag implementation
- [ ] --images flag implementation (vision API for image description)
- [ ] --toc flag implementation
- [ ] .env.example updated with GEMINI_API_KEY
- [ ] Integration tests with mocked LLM responses
- [ ] Documentation of smart features in README

**Verification Gate**: **USER GATE**: LLM-powered --summary and --images flags work correctly

**Estimated Complexity**: Medium
