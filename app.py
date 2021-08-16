# encoding: utf-8
from influxdb import InfluxDBClient
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns
import re
from dateutil import tz
from datetime import datetime
import codecs

from_zone = tz.gettz('UTC')
to_zone = tz.gettz('America/Sao_Paulo')

client = InfluxDBClient(host='localhost', port=8086, database='load_tests')
 
def getReqNames(begin_time, end_time):
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

def getIniEndTest(begin_time, end_time):
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

def getDataRPM(begin_time, end_time):

      query = ("SELECT sum(count) / 60 AS req_per_min " + 
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

def getDataRespTime(begin_time, end_time):

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

def getDataError(begin_time, end_time):

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

def plotCharts(testDateTime, arrayDataRPM, dictDataRespTime, dictDataError):
      ############################ PLOT CHART RPM ############################
      plt.rcParams.update({'figure.autolayout': True})

      # plt.plot(arrayDataRPM[0], arrayDataRPM[1])

      fig, ax = plt.subplots(figsize=(10, 5));

      ax.plot(arrayDataRPM[0], arrayDataRPM[1])
      labels = ax.get_xticklabels()
      plt.setp(labels, rotation=45, horizontalalignment='right', fontsize=12)
      ax.set(ylabel='Requisições por Minuto')
      plt.title('Total Throughput - Ini: {} / End: {}'.format(testDateTime[1], testDateTime[2]),
            fontsize=24,
            loc='center')

      sns.set_theme()
      sns.set_style("whitegrid")

      plt.savefig("./report/graph-rpm.png")

      ############################ PLOT CHART RespTime ############################
      plt.rcParams.update({'figure.autolayout': True})

      # plt.plot(arrayDataRPM[0], arrayDataRPM[1])

      fig, ax = plt.subplots(figsize=(10, 5));

      for transac_name in dictDataRespTime:
            ax.plot(dictDataRespTime[transac_name][0], dictDataRespTime[transac_name][1], label=transac_name)
      
      labels = ax.get_xticklabels()
      plt.setp(labels, rotation=45, horizontalalignment='right')
      ax.set(ylabel='Tempo de Resposta (p90 ms)')
      plt.title('Percentil 90 de Tempo de Resposta - Ini: {} / End: {}'.format(testDateTime[1], testDateTime[2]),
            pad=80.0, 
            fontsize=24,
            loc='Center'
      )
      # ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
      #     ncol=3, fancybox=True, shadow=True)
      plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), 
            loc='lower left',
            ncol=2, 
            borderaxespad=0.2,
            fontsize=14,
            framealpha=.0)
      
      sns.set_theme()
      sns.set_style("whitegrid")
      plt.savefig("./report/graph-respTime.png")

      ############################ PLOT CHART RespTime ############################
      plt.rcParams.update({'figure.autolayout': True})

      fig, ax = plt.subplots(figsize=(10, 5));

      for respCode in dictDataError:
            ax.plot(dictDataError[respCode][0], dictDataError[respCode][1], label=respCode)
      
      labels = ax.get_xticklabels()
      plt.setp(labels, rotation=45, horizontalalignment='right')
      ax.set(ylabel='Quantidade de Erros')
      
      plt.title('Ocorrência de Erros - Ini: {} / End: {}'.format(testDateTime[1], testDateTime[2]),
            pad=80.0, 
            fontsize=24,
            loc='Center'
      )
      plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), 
            loc='lower left',
            ncol=2, 
            borderaxespad=0.2,
            fontsize=14,
            framealpha=.0)

      sns.set_theme()
      sns.set_style("whitegrid")
      plt.savefig("./report/graph-errors.png")

def createReport(begin_time, end_time, reqNames, testDateTime):
      transacTable = """
| {:30}| Quantidade de Usuários  | Requisições por segundo  |
|-{:-<30}|-------------------------|--------------------------|""".format('Transação','-')

      for reqName in reqNames:
            transacTable = (transacTable + 
                  "\n| {:30}| XXX                     | XXXXX                    |".format(reqName))
            
      reportContent ="""
# Resultados do Teste de Carga

## 1. Objetivo do Teste

O teste tem como objetivo estressar o ambiente XPTO para validar a capacidade de processar XXX requisições por segundo com uma performance dentro dos parâmetros de negócio aceitáveis.

## 2. Volumetria Mapeada

{}

* Ambiente de teste X vezes menor que o ambiente de produção

## 3. Data de Execução

| Dados do Teste    |         |
|-------------------|---------|
| Data da Execução  | {:8}|
| Inicio do Teste   | {:8}|
| Fim do Teste      | {:8}|

## 4. Participação

* Pessoa 1
* Pessoa 2
* Pessoa 3

## 5. Configuração das Baterias

| Bateria | Users / Threads | Rampup Time (segs) | Steps | Duração | ThinkTime (ms) |
|---------|-----------------|--------------------|-------|---------|----------------|
| 1       | 300             | 150                | 10    | 300     | 200            |
| 2       | 900             | 450                | 10    | 300     | 200            |
| 3       | 1800            | 600                | 20    | 600     | 500            |

## 6. Conclusão do Teste

### **6.1 Requisições Por Minuto**

A aplicação se manteve em uma média de cerca de {} requisições por minuto alcançando picos de até {} requisições.

![Graf RPM](./graph-rpm.png)

### **6.2 Tempo de Resposta**

Observamos que o tempo de resposta geral em média se manteve em cerca de {} segundos alcançando picos de até {} segundos.

![Graf Tempo Resposta](./graph-respTime.png)

### **6.2 Erros**

Verificamos uma média de média {} erros sendo o mais frequente o código de erro {}.

![Graf Erros](./graph-errors.png)

## 7. Pipelines

* Link Pipeline Executada: https://<URL_DO_ORQUESTRADOR>/_build/results?buildId=934108&view=results
""".format(transacTable, testDateTime[0], testDateTime[1], testDateTime[2], 100, 150, 0.5, 2, 10, 500)

      f = codecs.open('./report/report.md', 'w', 'utf-8')
      f.write(reportContent)
      f.close()

def main():
      begin_time = "1628199538000";
      end_time = "1628200760000";

      reqNames = getReqNames(begin_time, end_time)
      # getReqNames(begin_time, end_time)
            
      datesTest = getIniEndTest(begin_time, end_time)
      # getIniEndTest(begin_time, end_time)

      dataRPM = getDataRPM(begin_time, end_time)
      # getDataRPM(begin_time, end_time)

      dataRespTime = getDataRespTime(begin_time, end_time)
      # getDataRespTime(begin_time, end_time)

      dataError = getDataError(begin_time, end_time)
      # getDataRespTime(begin_time, end_time)

      plotCharts(datesTest, dataRPM, dataRespTime, dataError)
      # createReport(begin_time, end_time, reqNames, datesTest)

main()
