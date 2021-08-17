# encoding: utf-8
from influxdb import InfluxDBClient
import re
from dateutil import tz
from datetime import datetime
import argparse
import reportGenerator as rg
import plotCharts

from_zone = tz.gettz('UTC')
to_zone = tz.gettz('America/Sao_Paulo')

def getReqNames(client, begin_time, end_time):
      query = ("SELECT distinct(transaction) as transac_name" +
            " FROM (SELECT * FROM jmeter " +
                  " WHERE application='jmeter_mock_test' " +
                  # " AND transaction !='all' " + 
                  " AND transaction =~ /^TC/ " + 
                  # " AND transaction != 'internal' " + 
                  # " AND transaction != 'Think_Time' " +
                  " AND time >= " + begin_time + "ms AND time <= " + end_time + "ms)")
      results = client.query(query)
      points  = results.get_points()

      arrayReqNames = [];
      for point in points:
            arrayReqNames.append(point['transac_name'])

      return arrayReqNames

def getIniEndTest(client, begin_time, end_time):
      def getTime(points):
            for point in points:
                  time = point['time']
                  time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ')
                  time = time.replace(tzinfo=from_zone)
                  time = time.astimezone(to_zone)
                  date = re.sub('([0-9]{4})-([0-9]{2})-([0-9]{2}).*', '\\3/\\2', str(time))
                  time = re.sub('^.+ ([0-9]{2}):([0-9]{2}):.*', '\\1:\\2', str(time))
                  return time, date

      query_first = ("SELECT first(count) as transac_name" +
            " FROM jmeter " +
            " WHERE application='jmeter_mock_test' " +
            " AND time >= " + begin_time + "ms AND time <= " + end_time + "ms")
      
      query_last = ("SELECT last(count) as transac_name" +
            " FROM jmeter " +
            " WHERE application='jmeter_mock_test' " +
            " AND time >= " + begin_time + "ms AND time <= " + end_time + "ms")
      
      results_first = client.query(query_first)
      results_last = client.query(query_last)

      testIniTime, testIniDate = getTime(results_first.get_points())
      testEndTime, testEndDate = getTime(results_last.get_points())

      arrayTimeInitEnd = [testIniDate, testIniTime, testEndTime]
      return arrayTimeInitEnd

def getDataRPM(client, begin_time, end_time):

      query = ("SELECT sum(count) AS req_per_min " + 
            " FROM jmeter " + 
            " WHERE (statut = 'ok' AND transaction !~ /^TC/ AND transaction != 'all')  " + 
            " AND time >= " + begin_time + "ms and time <= " + end_time + "ms" + 
            " GROUP BY time(60s) fill(0)")
      
      results = client.query(query)

      points = results.get_points()

      arrayDataRPM = [[],[]]

      for point in points:
            time = point['time']

            time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ')
            time = time.replace(tzinfo=from_zone)
            time = time.astimezone(to_zone)
            time = re.sub('([0-9]{4})-([0-9]{2})-([0-9]{2}).+([0-9]{2}):([0-9]{2}):([0-9]{2})-.*', '\\3/\\2 \\4:\\5', str(time))

            arrayDataRPM[0].append(time)
            arrayDataRPM[1].append(point['req_per_min'])
      # print(arrayDataRPM)
      return arrayDataRPM

def getDataRespTime(client, begin_time, end_time):

      query = ("SELECT mean(\"pct90.0\") AS resp_time " + 
            " FROM jmeter " + 
            " WHERE statut = 'ok' AND transaction !~ /^TC/ AND transaction != 'all' and transaction != 'Think_Time' " + 
            " AND time >= " + begin_time + "ms and time <= " + end_time + "ms" + 
            " GROUP BY transaction, time(60s) fill(0)")

      results = client.query(query)

      itens = results.items()

      dictRespTimePerTransac = {}

      for item in itens:
            transac_name = item[0][1]['transaction']
            dictRespTimePerTransac[transac_name] = [[],[]]
            points = results.get_points(tags={'transaction':transac_name})
            for point in points:
                  time = point['time']
                  time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ')
                  time = time.replace(tzinfo=from_zone)
                  time = time.astimezone(to_zone)
                  time = re.sub('([0-9]{4})-([0-9]{2})-([0-9]{2}).+([0-9]{2}):([0-9]{2}):([0-9]{2})-.*', '\\3/\\2 \\4:\\5', str(time))

                  dictRespTimePerTransac[transac_name][0].append(time)
                  dictRespTimePerTransac[transac_name][1].append(point["resp_time"])

      return dictRespTimePerTransac

def getDataError(client, begin_time, end_time):

      query = ("SELECT sum(count) AS countError " + 
            " FROM jmeter " + 
            " WHERE transaction !~ /^TC/ AND transaction != 'all' and transaction != 'Think_Time' " + 
            " AND responseCode !~ /^$/ " +
            " AND time >= " + begin_time + "ms and time <= " + end_time + "ms" + 
            " GROUP BY responseCode, time(60s) fill(0)")

      results = client.query(query)

      itens = results.items()

      dictError = {}

      for item in itens:
            resp_code = item[0][1]['responseCode']
            dictError[resp_code] = [[],[]]
            points = results.get_points(tags={'responseCode':resp_code})
            for point in points:
                  time = point['time']
                  time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ')
                  time = time.replace(tzinfo=from_zone)
                  time = time.astimezone(to_zone)
                  time = re.sub('([0-9]{4})-([0-9]{2})-([0-9]{2}).+([0-9]{2}):([0-9]{2}):([0-9]{2})-.*', '\\3/\\2 \\4:\\5', str(time))

                  dictError[resp_code][0].append(time)
                  dictError[resp_code][1].append(point["countError"])

      return dictError

def main(host='localhost', port=8086, database='load_tests'):
      begin_time = "1628199538000";
      end_time = "1628200760000";

      client = InfluxDBClient(host=host, port=port, database=database)

      reqNames = getReqNames(client, begin_time, end_time)
      # getReqNames(begin_time, end_time)
            
      datesTest = getIniEndTest(client, begin_time, end_time)
      # getIniEndTest(begin_time, end_time)

      dataRPM = getDataRPM(client, begin_time, end_time)
      # getDataRPM(begin_time, end_time)

      dataRespTime = getDataRespTime(client, begin_time, end_time)
      # getDataRespTime(begin_time, end_time)

      dataError = getDataError(client, begin_time, end_time)
      # getDataRespTime(begin_time, end_time)

      plotCharts.plot(datesTest, dataRPM, dataRespTime, dataError)
      
      rg.createReport(reqNames, datesTest)


def parse_args():
      """Parse the args."""
      parser = argparse.ArgumentParser(
            description='A load test report creator')
      parser.add_argument('--host', type=str, required=False,
                        default='localhost',
                        help='hostname of InfluxDB http API', dest='host')
      parser.add_argument('--port', type=int, required=False, default=8086,
                        help='port of InfluxDB http API')
      parser.add_argument('--db', type=str, required=False, 
                        default='load_tests',
                        help='InfluxDB database to be queried')
      return parser.parse_args()


if __name__ == '__main__':
      args = parse_args()
      main(host=args.host, port=args.port, database=args.db)
