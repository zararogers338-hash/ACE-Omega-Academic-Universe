#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
echo "Starting ACE-Omega Academic Universe..."
python -m streamlit run app.py
