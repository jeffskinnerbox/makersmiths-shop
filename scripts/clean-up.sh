#!/bin/bash

# prevents scripts from "marching forward" blindly after a critical failure
set -euo pipefail

# Run these command to re-initialized everything
trash output/*.{html,j2,pdf,md,docx,xlsx}
trash *.bak* output/*.bak* input/*.bak* docs/*.bak* requirments/*.bak* scripts/*.bak* tests/*.bak*
