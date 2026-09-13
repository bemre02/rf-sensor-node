#!/usr/bin/env bash
# Idempotent Cloud Agent bootstrap for rf-sensor-node.
# Prepares the Python simulation environment under sim/ (scikit-rf, numpy, matplotlib).
# The firmware/ and hardware/ trees are currently plan-only (no buildable sources yet),
# so this only sets up what can actually run today: the sim/ toolchain.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
sim_dir="$repo_root/sim"

# python venv needs ensurepip, which lives in the python3-venv system package on
# Debian/Ubuntu and is missing from the default image. Install it only when absent.
if ! python3 -c "import ensurepip" >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y --no-install-recommends python3-venv
fi

cd "$sim_dir"
python3 -m venv .venv
# shellcheck disable=SC1091
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "sim/ environment ready. Activate with: source sim/.venv/bin/activate"
