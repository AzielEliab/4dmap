#!/usr/bin/env python3
"""Shim so `python3 4dmap.py doctor` works from a source checkout."""

from fourdmap.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
