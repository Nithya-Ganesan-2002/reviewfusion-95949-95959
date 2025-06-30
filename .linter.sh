#!/bin/bash
cd /home/kavia/workspace/code-generation/reviewfusion-95949-95959/review_radar_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

