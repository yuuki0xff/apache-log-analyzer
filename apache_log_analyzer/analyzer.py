from typing import (
    NewType,
    Optional,
)
import dataclasses
from datetime import datetime

import apache_log_parser

LogRecord = NewType('LogRecord', dict)

DEFAULT_FORMAT = '%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"'


class Parser(apache_log_parser.Parser):
    def __init__(self, format_string: Optional[str] = None):
        if format_string is None:
            format_string = DEFAULT_FORMAT
        super().__init__(format_string)

    def parse(self, log_line: str) -> LogRecord:
        return super().parse(log_line)


@dataclasses.dataclass
class Period:
    """ 集計期間

    Attributes:
        start - 集計期間の開始日時。未指定の場合はNone
        end - 集計期間の終了日時。endは集計期間に含まれない。未指定の場合はNone
    """
    start: Optional[datetime] = dataclasses.field(default=None)
    end: Optional[datetime] = dataclasses.field(default=None)

    def is_in_range(self, dt: datetime) -> bool:
        # TODO
        raise NotImplementedError()


class AccessCounter:
    def __init__(self, period: Period, time_unit='hour'):
        # TODO
        pass

    def __iter__(self):
        # TODO
        return iter([
            datetime(2010, 1, 2),
            datetime(2010, 1, 1),
            datetime(2010, 1, 3),
        ])

    def __getitem__(self, key: LogRecord) -> int:
        # TODO
        return 0


class HostCounter:
    def __init__(self, period: Period): pass
    def most_common(self, n: Optional[int] = None):
        # TODO
        return [
            ('host2', 20),
            ('host0', 10),
            ('host1', 5),
        ]
