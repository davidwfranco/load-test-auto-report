from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sns

def plot(testDateTime, arrayDataRPM, dictDataRespTime, dictDataError):
    ############################ PLOT CHART RPM ############################
    plt.rcParams.update({'figure.autolayout': True})

    sns.set_theme()
    sns.set_style("whitegrid")

    fig, ax = plt.subplots(figsize=(10, 5));

    ax.plot(arrayDataRPM[0], arrayDataRPM[1])
    
    labels = ax.get_xticklabels()
    plt.setp(labels, rotation=45, horizontalalignment='right', fontsize=12)
    
    ax.set(ylabel='Requisições por Minuto')

    
    
    plt.title('Total Throughput - Ini: {} / End: {}'.format(testDateTime[1], testDateTime[2]),
        pad=20,
        fontsize=24,
        loc='center'
    )

    plt.savefig("./report/graph-rpm.png")

    ############################ PLOT CHART RespTime ############################
    plt.rcParams.update({'figure.autolayout': True})

    sns.set_theme()
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(10, 5));

    for transac_name in dictDataRespTime:
        ax.plot(dictDataRespTime[transac_name][0], dictDataRespTime[transac_name][1], label=transac_name)
    
    labels = ax.get_xticklabels()
    plt.setp(labels, rotation=45, horizontalalignment='right', fontsize=12)
    
    ax.set(ylabel='Tempo de Resposta (p90 ms)')
    
    plt.title('Percentil 90 de Tempo de Resposta - Ini: {} / End: {}'.format(testDateTime[1], testDateTime[2]),
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
    

    plt.savefig("./report/graph-respTime.png")

    ############################ PLOT CHART RespTime ############################
    plt.rcParams.update({'figure.autolayout': True})

    sns.set_theme()
    sns.set_style("whitegrid")

    fig, ax = plt.subplots(figsize=(10, 5));

    for respCode in dictDataError:
        ax.plot(dictDataError[respCode][0], dictDataError[respCode][1], label=respCode)
    
    labels = ax.get_xticklabels()
    plt.setp(labels, rotation=45, horizontalalignment='right', fontsize=12)
    
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

    plt.savefig("./report/graph-errors.png")
