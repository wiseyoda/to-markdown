---
version: '1.0'
description: 'Requirements checklist for production readiness verification'
---

# Requirements Checklist: Production Readiness & Documentation

**Purpose**: Track completion of all Phase 0130 requirements
**Created**: 2026-02-27
**Feature**: [spec.md](spec.md)

## README & Documentation

- [ ] CHK001 README.md rewritten with public-facing content (FR-001)
- [ ] CHK002 Badges added: Python version, license, CI status (FR-002)
- [ ] CHK003 CHANGELOG.md created covering phases 0010-0130 (FR-007)
- [ ] CHK004 LICENSE file created with MIT text (FR-008)

## CI/CD

- [ ] CHK005 GitHub Actions workflow created in `.github/workflows/` (FR-003)
- [ ] CHK006 CI tests Python 3.14 only (FR-004)
- [ ] CHK007 Coverage threshold set to 80% (FR-005)
- [ ] CHK008 Coverage configuration in pyproject.toml (FR-006)
- [ ] CHK009 CI completes in under 5 minutes (NFR-001)

## Governance Updates

- [ ] CHK010 constitution.md: Fix "Gemini 3.0 Flash" -> "Gemini 2.5 Flash (GA)" (FR-009)
- [ ] CHK011 testing-strategy.md: Update to v1.2.0 with current test count (FR-010)
- [ ] CHK012 glossary.md: Update to v2.1.0 with new terms (FR-011)
- [ ] CHK013 All memory docs have accurate versions and dates (NFR-003)

## Release

- [ ] CHK014 pyproject.toml version set to "1.0.0" (FR-012)
- [ ] CHK015 Git tag v1.0.0 created (FR-013)

## Notes

- Check items off as completed: `[x]`
- FR-013 (git tag) is done during `/flow.merge`, not during implementation
- Coverage measurement should happen early to identify if tests need to be added
