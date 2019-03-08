import apache_log_parser

format = '%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\"'
line_parser = apache_log_parser.make_parser(format)
