# Requirements Checklist: Easy Install

**Phase**: `0120-easy-install`

## Functional Requirements

- [ ] FR-001: macOS install script (install.sh)
- [ ] FR-002: Windows install script (install.ps1)
- [ ] FR-003: Configuration wizard (--setup flag)
- [ ] FR-004: Installation documentation (INSTALL.md)
- [ ] FR-005: Uninstall scripts (uninstall.sh / uninstall.ps1)
- [ ] FR-006: README update with install reference

## Non-Functional Requirements

- [ ] NFR-001: Install scripts require no Python
- [ ] NFR-002: Idempotent installation
- [ ] NFR-003: Graceful degradation (Tesseract optional)
- [ ] NFR-004: Clear, actionable error messages

## Success Criteria

- [ ] SC-001: Fresh macOS install works end-to-end
- [ ] SC-002: Fresh Windows install works end-to-end
- [ ] SC-003: Setup wizard configures API key successfully

## Wiring Requirements

- [ ] WR-001: --setup flag wired in cli.py
- [ ] WR-002: Setup constants in constants.py
