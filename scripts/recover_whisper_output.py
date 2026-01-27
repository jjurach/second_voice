#!/usr/bin/env python3
"""
Recover whisper output from temporary files.

Usage:
    python scripts/recover_whisper_output.py [--tmp-dir /path/to/tmp]
"""

import os
import sys
import glob
import argparse
from pathlib import Path
from datetime import datetime, timedelta


def find_orphaned_whisper_files(tmp_dir: str, age_hours: int = 24) -> list:
    """Find whisper output files without matching recording.

    Args:
        tmp_dir: Temporary directory to scan
        age_hours: Only find files older than this many hours

    Returns:
        list: Paths to orphaned whisper files
    """
    whisper_files = glob.glob(os.path.join(tmp_dir, "whisper-*.txt"))
    cutoff_time = datetime.now() - timedelta(hours=age_hours)

    orphaned = []
    for whisper_path in whisper_files:
        mtime = datetime.fromtimestamp(os.path.getmtime(whisper_path))
        if mtime < cutoff_time:
            orphaned.append(whisper_path)

    return orphaned


def main():
    parser = argparse.ArgumentParser(description="Recover whisper output from temp files")
    parser.add_argument("--tmp-dir", default="./tmp", help="Temporary directory (default: ./tmp)")
    parser.add_argument("--age-hours", type=int, default=24, help="Age threshold in hours (default: 24)")
    parser.add_argument("--recover", action="store_true", help="Copy orphaned files to recovery directory")
    parser.add_argument("--recovery-dir", default="./recovery", help="Recovery directory (default: ./recovery)")

    args = parser.parse_args()

    orphaned = find_orphaned_whisper_files(args.tmp_dir, args.age_hours)

    if not orphaned:
        print(f"✓ No orphaned whisper files in {args.tmp_dir}")
        return 0

    print(f"Found {len(orphaned)} orphaned whisper file(s):\n")
    for path in orphaned:
        size = os.path.getsize(path)
        mtime = datetime.fromtimestamp(os.path.getmtime(path))
        print(f"  {path} ({size} bytes, modified {mtime})")

    if args.recover:
        os.makedirs(args.recovery_dir, exist_ok=True)
        for path in orphaned:
            dest = os.path.join(args.recovery_dir, os.path.basename(path))
            import shutil
            shutil.copy2(path, dest)
            print(f"✓ Recovered: {dest}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
