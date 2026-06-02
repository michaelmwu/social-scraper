#!/usr/bin/env sh
set -eu

required_major=0
required_minor=11

version_output=$(uv --version)
version=$(printf '%s\n' "$version_output" | awk '{print $2}')
major=${version%%.*}
minor_patch=${version#*.}
minor=${minor_patch%%.*}

if [ "$major" -lt "$required_major" ] || {
  [ "$major" -eq "$required_major" ] && [ "$minor" -lt "$required_minor" ]
}; then
  printf '%s\n' "uv >=0.11.0 is required; found $version_output." >&2
  printf '%s\n' "Upgrade uv with Homebrew: brew upgrade uv" >&2
  exit 1
fi
