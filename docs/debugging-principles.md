# Debugging Principles

- **Diagnose before fixing**: Run the thing first, check logs, identify the actual error before changing code
- **Understand the system before changing it**: Read docs/check how images/frameworks work (entrypoint vs CMD, init systems, etc.) before rewriting configs
- **Change one thing at a time**: Isolate variables, test after each change
- **Preserve what works**: When editing a line, diff against the original to avoid dropping intentional details (e.g., `cd /openvpn` was there for a reason)
- **Fix the first error first**: Don't chase secondary symptoms — fix the root cause and re-test
