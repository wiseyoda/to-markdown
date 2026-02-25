# SpecFlow Usage Reference

This document provides the CLI and slash command reference for SpecFlow v3.0.

## Quick Start

```bash
# In terminal
specflow status              # Show project status
specflow next                # Get next actionable task

# In Claude Code
/flow.orchestrate            # Full automated workflow
```

## CLI Commands

### Smart Commands

```bash
specflow status              # Complete project status
specflow next                # Next actionable task with context
specflow mark T007           # Mark task complete
specflow mark T007..T010     # Mark range of tasks
specflow mark V-001          # Mark verification item
specflow check               # Deep validation
specflow check --fix         # Auto-fix issues
specflow check --gate design # Check specific gate
```

### State Management

```bash
specflow state get <key>                    # Get state value
specflow state set key=value                # Set state value
specflow state get orchestration.phase      # Dot notation supported
```

### Phase Management

```bash
specflow phase                              # Show current phase
specflow phase open 0010                    # Start a specific phase
specflow phase open --hotfix                # Create hotfix phase
specflow phase close                        # Close current phase
specflow phase close --dry-run              # Preview close
specflow phase archive 0042                 # Archive completed phase
specflow phase add 0010 "name"              # Add phase to ROADMAP
specflow phase defer "item"                 # Add to BACKLOG.md
specflow phase scan                         # Scan for incomplete tasks
```

## Slash Commands

### Primary Workflows

```
/flow.orchestrate            # Full automated workflow (design → implement → verify)
/flow.design                 # Create spec, plan, tasks, checklists
/flow.implement              # Execute tasks with TDD
/flow.verify                 # Verify completion, update ROADMAP
/flow.merge                  # Close phase, push, merge to main
```

### Setup & Maintenance

```
/flow.init                   # Project initialization interview
/flow.memory                 # Verify and optimize memory documents
/flow.roadmap                # Create/update ROADMAP.md
/flow.doctor                 # Diagnose and migrate projects
```

### Quality & Review

```
/flow.analyze                # Cross-artifact consistency analysis
/flow.review                 # Systematic code review
```

## Common Patterns

### Starting a New Phase

```bash
# Option 1: Full automation (recommended)
/flow.orchestrate

# Option 2: Just design
/flow.design "Add user authentication"
```

### Completing a Phase

```bash
# Check status
specflow status

# Verify completion
/flow.verify

# Complete and merge
/flow.merge
```

### Resuming Work

```bash
# Check current state
specflow status

# Get next task
specflow next

# Resume workflow
/flow.orchestrate
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Missing templates | `specflow check --fix` |
| State file corrupt | `specflow check --fix` |
| Missing artifacts | Re-run `/flow.design` |

## More Information

- Project instructions: See `CLAUDE.md`
- Memory documents: `.specify/memory/`
- Templates: `.specify/templates/`
