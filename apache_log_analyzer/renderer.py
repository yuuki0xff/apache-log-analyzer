import dataclasses
from datetime import datetime
from typing import Optional
import json
import collections
from datetime import datetime

from apache_log_analyzer.analyzer import (
    AccessCounter,
    HostCounter,
)


@dataclasses.dataclass
class Params:
    req_per_hour: AccessCounter
    req_per_host: HostCounter
    hosts: Optional[int]


class TextRenderer:
    def render(self, params: Params):
        """
        >>> params = Params(
        ...     req_per_hour=collections.Counter({
        ...         datetime(2019, 1, 1, 12, 0): 100,
        ...         datetime(2019, 1, 1, 13, 0): 100,
        ...         datetime(2019, 1, 1, 14, 0): 200,
        ...     }),
        ...     req_per_host=collections.Counter({
        ...         '10.0.0.1': 20,
        ...         '10.0.0.2': 75,
        ...         '10.0.0.3': 255,
        ...         '10.0.0.4': 40,
        ...         '10.0.0.5': 10,
        ...     }),
        ...     hosts=3,
        ... )
        >>> TextRenderer().render(params)
        Requests per hour:
        [DateTime]: [Requests]
        2019-01-01 12:00: 100
        2019-01-01 13:00: 100
        2019-01-01 14:00: 200
        <BLANKLINE>
        Requests per IP address:
        [IP Address]: [Requests]
        10.0.0.3: 255
        10.0.0.2: 75
        10.0.0.4: 40
        """
        print('Requests per hour:')
        print('[DateTime]: [Requests]')
        for dt in sorted(params.req_per_hour):  # 時刻でソート。
            count = params.req_per_hour[dt]
            print(f'{dt:%04y-%02m-%02d %02H-%02M-%02S}: {count}')
        print()
        print('Requests per IP address:')
        print('[IP Address]: [Requests]')
        for host, count in params.req_per_host.most_common(params.hosts):  # アクセス数でソート
            print(f'{host}: {count}')


class JsonRenderer:
    def render(self, params: Params):
        js = {
            'request_per_hour': {
                dt.isoformat(): params.req_per_hour[dt]
                for dt in params.req_per_hour  # type: datetime
            },
            'request_per_host': {
                host: count
                for host, count in params.req_per_host.most_common(params.hosts)
            },
        }
        print(json.dumps(js))
