import codecs
from datetime import datetime
from time import timezone

def createReport(reqNames, testDateTime):
    transacTable = """
| {:30}| Quantidade de Usuários  | Requisições por segundo  |
|-{:-<30}|-------------------------|--------------------------|""".format('Transação','-')

    for reqName in reqNames:
        transacTable = (transacTable + 
                "\n| {:30}| XXX                     | XXXXX                    |".format(reqName))
        
    reportContent ="""
# Resultados do Teste de Carga - {}

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
""".format(datetime.now().strftime('%H:%M:%S'), transacTable, testDateTime[0], testDateTime[1], testDateTime[2], 100, 150, 0.5, 2, 10, 500)

    f = codecs.open('./report/report.md', 'w', 'utf-8')
    f.write(reportContent)
    f.close()