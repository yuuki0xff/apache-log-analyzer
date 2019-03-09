import sys
import argparse
import dataclasses
from typing import (
    Optional,
    List,
    Iterator,
)

from apache_log_analyzer import (
    analyzer,
    renderer,
)


@dataclasses.dataclass
class Arguments:
    time_range: analyzer.Period
    hosts: Optional[int]
    format: str
    files: List[str]

    @staticmethod
    def parser(prog: str):
        p = argparse.ArgumentParser(prog=prog)
        p.add_argument('--time-range', default=analyzer.Period(), type=analyzer.Period.from_str)
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
            hosts=None if ns.hosts <= 0 else ns.hosts,
            format=ns.format,
            files=ns.files,
        )


def iter_lines(files: List[str]) -> Iterator[str]:
    if files:
        for fname in files:
            with open(fname) as f:
                yield from f
    else:
        yield from sys.stdin


def _main(args: List[str]) -> int:
    a = Arguments.from_args(args)
    print(a)
    lines = iter_lines(a.files)
    parser = analyzer.Parser()
    req_per_hour = analyzer.AccessCounter(time_unit='hour', period=a.time_range)
    req_per_host = analyzer.HostCounter(period=a.time_range)
    for line in lines:
        result = parser.parse(line)
        print(result['remote_host'], result['time_received_utc_datetimeobj'])
        req_per_hour.add(result)
        req_per_host.add(result)

    params = renderer.Params(
        req_per_hour=req_per_hour,
        req_per_host=req_per_host,
        hosts=a.hosts,
    )
    if a.format == 'text':
        renderer.TextRenderer().render(params)
    elif a.format == 'json':
        renderer.JsonRenderer().render(params)
    else:
        # argparseで採りうる値を制限しているので、ここには到達しないはず
        raise ValueError(f'invalid format: {a.format}')
    return 0


def main():
    exit(_main(sys.argv))
