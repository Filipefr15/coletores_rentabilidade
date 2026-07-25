from ima_idka_collector import procurar_ima_idka
from rv_index_collector import procurar_indices_rv
from sEp_500_collector import procurar_sEp500
from tx_cambio_collector import procurar_tx_cambio
import datetime

data = ['18/03/2025']

#data = '13022025'
try:
    #adequando a data para o formato correto para essa função
    formatted_data = [date.replace('/', '') for date in data]
    print("Iniciando busca IMA's, IDKA's, IRF's")
    procurar_ima_idka(formatted_data)
except Exception as e:
    print(e)
    print('Erro ao procurar IMA IDKA')
    raise e
print("Procura finalizada com sucesso!")

#data = '17/03/2025'
# Verificar motivo dos erros frequentes e corrigir antes de descomentar.
#Data sempre não encontrada? Mas a data está lá...
try:
    print("Iniciando busca de índices de Renda Variável")
    procurar_indices_rv(data)
except Exception as e:
    print(e)
    print('Erro ao procurar índices de Renda Variável')
    raise e
print("Procura finalizada com sucesso!")

#data = 'Mar 10, 2025'
try:
    #adequando a data para o formato correto para essa função
    formatted_data = [datetime.datetime.strptime(date, '%d/%m/%Y').strftime('%b %d, %Y') for date in data]
    print("Iniciando busca S&P500")
    procurar_sEp500(formatted_data)
except Exception as e:
    print(e)
    print('Erro ao procurar S&P500')
    raise e
print("Procura finalizada com sucesso!")

#data = '17/03/2025'
try:
    print("Iniciando busca Taxa de Câmbio")
    procurar_tx_cambio(data)
except Exception as e:
    print(e)
    print('Erro ao procurar Taxa de Câmbio')
    raise e
print("Procura finalizada com sucesso!")
