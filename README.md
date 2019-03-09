# apache-log-analyzer
Apache HTTP サーバのアクセスログを集計し、下記のデータを表示する。

- 各時間帯毎のアクセス件数
- リモートホスト別のアクセス件数:
  アクセスの多いリモートホストの順にアクセス件数の一覧を表示する。
  
## Requirements
* Python 3.7 or later

## Installation
```bash
$ python3 -m pip install -U git+https://url/to/this/repository
```

## Usage
```bash
$ apache-log-analyzer /path/to/log/files
Requests per hour:
[DateTime]: [Requests]
2019-01-01 12:00: 100
2019-01-01 13:00: 100
2019-01-01 14:00: 200

Requests per IP address:
[IP Address]: [Requests]
10.0.0.3: 255
10.0.0.2: 75
10.0.0.4: 40
10.0.0.5: 30
...
```

## Arguments
```
apache-log-analyzer [--time-range RANGE] [--hosts N] [--format FORMAT] /path/to/log/files ...

--time-range <START>/<END>
    集計対象の期間を指定する。
    期間は、開始日時と終了日時を"/"で繋げた文字列で表現する
    例: 2019-01-01/2019-05-01 (2019年01月01日から4月末まで)
    例: 2019-04-01 10:00/2019-04-01 20:00 (2019年04月01日の10時から20時まで)
    例: 2019-04-01 10:00+00:00/2019-04-01 20:00+00:00 (2019年04月01日の10時から20時まで。タイムゾーンはUTC)

--hosts <N>
    アクセスが多いホストの上位N件を表示する。
    N<=0のときは、全てのホストを表示する。

--format <FORMAT>
    出力フォーマットを指定する。
    指定可能な値は、textまたはjson。
    デフォルト値はtext。
```
