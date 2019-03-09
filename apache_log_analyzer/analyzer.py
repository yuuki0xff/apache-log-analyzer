from typing import (
    NewType,
    Optional,
)
import dataclasses
import collections
from datetime import datetime

import apache_log_parser

LogRecord = NewType('LogRecord', dict)

DEFAULT_FORMAT = '%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"'


class Parser(apache_log_parser.Parser):
    """
    >>> log = '10.2.3.4 - - [18/Apr/2005:09:10:47 +0900] "GET / HTTP/1.1" 200 854 "-" "Mozilla/4.0 (compatible; MSIE 5.5; Windows 98)"'
    >>> result = Parser().parse(log)
    >>> result['remote_host']
    '10.2.3.4'
    >>> result['time_received_utc_datetimeobj']
    datetime.datetime(2005, 4, 18, 0, 10, 47, tzinfo='0000')
    """
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
        """
        >>> p = Period(datetime(2010, 1, 10), datetime(2010, 1, 20))
        >>> p.is_in_range(datetime(2010, 1, 9, 23, 59, 59))
        False
        >>> p.is_in_range(datetime(2010, 1, 10))
        True
        >>> p.is_in_range(datetime(2010, 1, 19, 23, 59, 59))
        True
        >>> p.is_in_range(datetime(2010, 1, 20))
        False

        >>> p = Period()
        >>> p.is_in_range(datetime(2010, 1, 1))
        True
        """
        if self.start and dt < self.start:
            return False
        if self.end and self.end <= dt:
            return False
        return True

    @classmethod
    def from_str(cls, s: str) -> 'Period':
        # TODO
        return Period()


class AccessCounter:
    def __init__(self, period: Period, time_unit='hour'):
        self._period = period
        self._time_unit = time_unit
        if time_unit == 'hour':
            self._convert_dt = lambda dt: dt.replace(minute=0, second=0, microsecond=0)
        else:
            raise ValueError('invalid time_unit')
        self._counter = collections.Counter()

    def __iter__(self):
        return iter(self._counter)

    def __getitem__(self, key: LogRecord) -> int:
        return self._counter[key]

    def add(self, rec: LogRecord):
        dt = rec['time_received_utc_datetimeobj']
        if not self._period.is_in_range(dt):
            # 集計期間外なので無視
            return

        key = self._convert_dt(dt)
        self._counter[key] += 1


class HostCounter:
    def __init__(self, period: Period):
        self._period = period
        self._counter = collections.Counter()

    def most_common(self, n: Optional[int] = None):
        return self._counter.most_common(n)

    def add(self, rec: LogRecord):
        dt = rec['time_received_utc_datetimeobj']
        if not self._period.is_in_range(dt):
            # 集計期間外なので無視
            return

        key = rec['remote_host']
        self._counter[key] += 1
