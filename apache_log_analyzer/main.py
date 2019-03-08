import sys
import argparse
import dataclasses
from typing import (
    Optional,
    List
)


@dataclasses.dataclass
class Arguments:
    time_range: Optional[str]
    hosts: int
    format: str
    files: List[str]

    @staticmethod
    def parser(prog: str):
        p = argparse.ArgumentParser(prog=prog)
        p.add_argument('--time-range', default=None)
        p.add_argument('--hosts', type=int, default=0)
        p.add_argument('--format', choices=['text', 'json'], default='text')
        p.add_argument('files', nargs='*')
        return p

    @classmethod
    def from_args(cls, args: List[str]):
        prog = args[0]
        ns = cls.parser(prog).parse_args(args[1:])
        return cls(
            time_range=ns.time_range or None,
            hosts=ns.hosts,
            format=ns.format,
            files=ns.files,
        )


def _main(args: List[str]) -> int:
    a = Arguments.from_args(args)
    print(a)
    return 0


def main():
    exit(_main(sys.argv))
