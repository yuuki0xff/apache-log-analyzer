import sys
from typing import (
    List
)


def _main(args: List[str]) -> int:
    print('args', args)
    return 0


def main():
    exit(_main(sys.argv))
