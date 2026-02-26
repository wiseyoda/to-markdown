# Smoke Test: Easy Install (Phase 0120)

## Prerequisites

These tests verify the install experience. You need a clean terminal session.

## Test 1: macOS Install Script

```bash
# In the project directory
./install.sh
# Expected: 7-step output, all steps OK, ends with success message
# Expected: "to-markdown is ready to use!"
```

## Test 2: Verify Global Alias (macOS)

```bash
# Open a NEW terminal window (to pick up the alias)
to-markdown --version
# Expected: to-markdown 0.1.0

# Convert a file
echo "Hello install test" > /tmp/install-test.txt
to-markdown /tmp/install-test.txt
# Expected: "Converted /tmp/install-test.txt → /tmp/install-test.md"
cat /tmp/install-test.md
# Expected: YAML frontmatter + "Hello install test"
```

## Test 3: Idempotent Install

```bash
# Run install again (should not duplicate alias)
./install.sh
# Expected: Step 6 says "Shell alias already configured"
grep -c "alias to-markdown" ~/.zshrc
# Expected: 1 (not 2)
```

## Test 4: Configuration Wizard

```bash
# Run setup wizard
to-markdown --setup
# Expected: Blue panel with feature explanation
# Expected: Prompt for API key
# Type: (your actual API key or press Enter to skip)

# If you entered a key:
cat .env
# Expected: GEMINI_API_KEY=your-key

# Test smart features
to-markdown /tmp/install-test.txt --summary
# Expected: markdown with ## Summary section
```

## Test 5: Setup Quiet Mode

```bash
to-markdown --setup --quiet
# Expected: "API key not configured. Smart features disabled." (if no .env)
# OR: "Validating existing API key... Valid." (if .env exists)
```

## Test 6: Uninstall

```bash
./uninstall.sh
# Expected: 4 prompts (alias, .venv, data dir, .env)
# Answer y to all

# Verify alias removed
source ~/.zshrc
to-markdown --version
# Expected: "command not found"
```

## Test 7: Reinstall After Uninstall

```bash
./install.sh
# Expected: Full install succeeds again
# Open new terminal, verify to-markdown works
```

## Test 8: Windows Install Script

```powershell
# In PowerShell
.\install.ps1
# Expected: 7-step output, all steps OK
# Expected: "to-markdown is ready to use!"

# Open NEW PowerShell window
to-markdown --version
# Expected: to-markdown 0.1.0
```

## Cleanup

```bash
rm -f /tmp/install-test.txt /tmp/install-test.md
```
