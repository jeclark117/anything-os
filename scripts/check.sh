#!/bin/bash
# Checks this folder against the rules in conventions.md, which follow OKF v0.2.
# Optional. The agent can check by reading, and "Check my OS" does that.
# This catches the mechanical problems faster: missing headers, broken links,
# footnotes with no source. It can't tell a guess from a decision.
#
# Exits 1 on any ERROR. WARN does not fail.
#
# Usage:  ./scripts/check.sh                       this OS
#         ./scripts/check.sh examples/personal     one of the examples

set -euo pipefail
exec python3 "$(dirname "$0")/okf_check.py" "$@"
