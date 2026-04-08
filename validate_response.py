#!/usr/bin/env python3

import sys
from pathlib import Path

from response_validation import validate_response_file_content


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: validate_response.py <response-file>")

    response_path = Path(sys.argv[1])

    if not response_path.exists():
        raise SystemExit(f"Response file not found: {response_path}")

    validate_response_file_content(response_path.read_text())
    print(f"Validated {response_path}")


if __name__ == "__main__":
    main()