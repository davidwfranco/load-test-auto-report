# load-test-auto-report
A automated load test report using (at first) jmeter, influxdb, python and publishing it in markdown

```
usage: load-test-auto-report.py [-h] --host HOSTNAME --port PORT --db DATABASE --begin 'BEGIN_TIME' --end 'END_TIME'

A load test report creator

optional arguments:
  -h, --help            show this help message and exit
  --host HOSTNAME       hostname of InfluxDB http API
  --port PORT           port of InfluxDB http API
  --db DATABASE         InfluxDB database to be queried
  --begin 'BEGIN_TIME'  begin of the test (yyyy-mm-dd hh24:mi:ss)
  --end 'END_TIME'      end of the test (yyyy-mm-dd hh24:mi:ss)
```