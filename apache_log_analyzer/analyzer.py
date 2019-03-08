from typing import (
    Optional,
)
import apache_log_parser

DEFAULT_FORMAT = '%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"'


class Parser(apache_log_parser.Parser):
    def __init__(self, format_string: Optional[str] = None):
        if format_string is None:
            format_string = DEFAULT_FORMAT
        super().__init__(format_string)
