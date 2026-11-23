#!/usr/bin/env python3
"""Backward-compatible Windows tool artwork entrypoint.

Previously generated placeholder illustrations are retired. The vendor logos
live in assets/tools/vendor and are validated by build_real_tool_art.py.
"""
from build_real_tool_art import main
if __name__ == "__main__":
    main()
