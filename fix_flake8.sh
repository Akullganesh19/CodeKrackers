#!/bin/bash
# Re-run flake8 but focus on critical syntax and undefined errors first
flake8 backend/ --count --select=E9,F63,F7,F82 --show-source --statistics
