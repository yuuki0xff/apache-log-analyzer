import dataclasses
from datetime import datetime
from typing import Optional
import json

from .analyzer import (
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
