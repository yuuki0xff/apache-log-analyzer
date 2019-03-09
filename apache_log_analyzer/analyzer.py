from typing import (
    NewType,
    Optional,
)
import dataclasses
import collections
from datetime import datetime

import apache_log_parser
import pytz

LogRecord = NewType('LogRecord', dict)

DEFAULT_FORMAT = '%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"'


class Parser(apache_log_parser.Parser):
    """ Apacheのログをパースする

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
        """
        # Set timezone to UTC.
        # https://stackoverflow.com/a/1301528
        >>> import os, time
        >>> previous_tz = os.environ.get('TZ')
        >>> os.environ['TZ'] = 'UTC'
        >>> time.tzset()

        >>> Period.from_str('2010-04-01/2015-03-31')
        Period(start=datetime.datetime(2010, 4, 1, 0, 0, tzinfo=<UTC>), end=datetime.datetime(2015, 3, 31, 0, 0, tzinfo=<UTC>))
        >>> Period.from_str('2010-04-01 10/2010-04-01 19:59')
        Period(start=datetime.datetime(2010, 4, 1, 10, 0, tzinfo=<UTC>), end=datetime.datetime(2010, 4, 1, 19, 59, tzinfo=<UTC>))
        >>> Period.from_str('2010-04-01 10:00+09:00/2010-04-01')
        Period(start=datetime.datetime(2010, 4, 1, 1, 0, tzinfo=<UTC>), end=datetime.datetime(2010, 4, 1, 0, 0, tzinfo=<UTC>))
        >>> Period.from_str('foo')
        Traceback (most recent call last):
        ...
        ValueError: invalid syntax
        >>> Period.from_str('foo/bar')
        Traceback (most recent call last):
        ...
        ValueError: invalid syntax

        # Restore the timezone
        >>> if previous_tz:
        ...     os.environ['TZ'] = previous_tz
        ... else:
        ...     del os.environ['TZ']
        """
        try:
            start, end = s.split('/', maxsplit=2)
            return Period(
                # 1. astimezone()でタイムゾーンを付与
                # 2. UTCに戻す
                start=datetime.fromisoformat(start).astimezone().astimezone(pytz.UTC),
                end=datetime.fromisoformat(end).astimezone().astimezone(pytz.UTC),
            )
        except ValueError:
            raise ValueError('invalid syntax')


class AccessCounter:
    """ 時間帯ごとのアクセス数を数える。

    Arguments:
        period - 集計期間
        time_unit - 時間帯の長さを指定する。指定できる値は'hour'のみ。

    >>> AccessCounter(period=Period(), time_unit='hour')._convert_dt(
    ...     datetime(1, 2, 3, 4, 5, 6, 7))
    datetime.datetime(1, 2, 3, 4, 0)
    >>> AccessCounter(period=Period(), time_unit='invalid')
    Traceback (most recent call last):
    ...
    ValueError: invalid time_unit
    """
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

    def __getitem__(self, key: datetime) -> int:
        return self._counter[key]

    def add(self, rec: LogRecord):
        dt = rec['time_received_utc_datetimeobj']
        if not self._period.is_in_range(dt):
            # 集計期間外なので無視
            return

        key = self._convert_dt(dt)
        self._counter[key] += 1


class HostCounter:
    """ 集計期間内のホスト別のアクセス数を数える """
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
