#!/bin/bash
#
#   What happens in the script:
#  trash ./*.bak* {output,input,docs,scripts,tests}/*.bak*. Bash brace-expands this to 7 separate glob patterns. Any directory that has no .bak* files (e.g. docs/, tests/,  passes the literal string docs/*.bak* as a filename argument to trash. Trash gets a non-existent path, returns a non-zero exit code, and set -e immediately aborts the script — before it even reaches the directories that  do have .bak* files.
#
#  The fix — use shopt -s nullglob so unmatched globs expand to nothing instead of a literal string, and guard against
#  the case where nothing matches at all:
#
#   The [[ ${#files[@]} -gt 0 ]] guard handles the remaining edge case: with nullglob, if nothing matches at all, the array is empty and trash would be called with no arguments (which also fails). The guard skips the call entirely in that case.
#

# prevents scripts from "marching forward" blindly after a critical failure
set -euo pipefail

# nullglob: unmatched globs expand to nothing instead of a literal string,
# preventing trash from receiving non-existent paths (which would abort via set -e)
shopt -s nullglob

# Trash all the generated output artifacts
files=(output/*.{html,j2,pdf,md,docx,xlsx})
[[ ${#files[@]} -gt 0 ]] && trash "${files[@]}"

# Trash all .bak* files in project directories
files=(./*.bak* {output,input,docs,scripts,tests}/*.bak*)
[[ ${#files[@]} -gt 0 ]] && trash "${files[@]}"
