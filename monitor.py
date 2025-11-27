#!/usr/bin/env python3
"""
Wrapper to run monitor/monitor.py from repository root so commands like
`python monitor.py` keep working whether the script is in the `monitor/` folder
or the repo root.
"""
import runpy
import sys


def main():
    # Run the monitor script from the monitor/ path, and return success
    runpy.run_path('monitor/monitor.py', run_name='__main__')
    return 0


if __name__ == '__main__':
    sys.exit(main())
