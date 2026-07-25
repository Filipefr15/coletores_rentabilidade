import re, os, psycopg2, datetime,importlib
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import segmentacao.inicializador as init

importlib.reload(init)

load_dotenv()

host = os.getenv("HOST")
database = os.getenv("DATABASE")
user= os.getenv("USER")
password= os.getenv("PASSWORD")

service, options = init.start_driver()

# Inicia-se a instância do Chrome WebDriver com as definidas 'options' e 'service', basicamente o driver É o google chrome.
driver = init.go_to_site(service, options, 'https://www.bcb.gov.br/controleinflacao/historicotaxasjuros')

tab_txa_selic = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "historicotaxasjuros")))

tbody_tab_txa_selic = WebDriverWait(tab_txa_selic, 10).until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))

tr_tab_txa_selic = WebDriverWait(tbody_tab_txa_selic, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "tr")))

reuniao, data_reuniao, extraordinaria, vies, inicio_vigencia, fim_vigencia, taxa_selic, selic_acumulada_periodo, selic_media_anual = [], [], [], [], [], [], [], [], []

for count, _ in enumerate(tr_tab_txa_selic):

    info_selic = tr_tab_txa_selic[count].text.split()
        
    try:
        info_selic.remove("-")
    except ValueError:
        pass
    x, y = re.findall(r"\(\d+\)", info_selic[1]), re.findall(r"\(\d+\)", info_selic[2]) 
    if x != []:
        info_selic.remove(x[0])
    elif y != []:
        info_selic.remove(y[0])
    
    is_ex = False
    if info_selic[1] == 'ex.':
        is_ex = True
        info_selic.remove('ex.')

    if info_selic[2] == 'sem':
        info_selic[2] = info_selic[2] + ' ' + info_selic[3]
        info_selic.remove(info_selic[3])

    if len(info_selic) <= 6:
        reuniao.append(info_selic[0])
        data_reuniao.append(info_selic[1])
        extraordinaria.append(is_ex)
        vies.append(info_selic[2])
        inicio_vigencia.append(info_selic[3])
        fim_vigencia.append(None)
        taxa_selic.append(info_selic[4])
        #tban.append(info_selic[5])
        selic_acumulada_periodo.append(None)
        selic_media_anual.append(None)
    else:
        reuniao.append(info_selic[0])
        data_reuniao.append(info_selic[1])
        extraordinaria.append(is_ex)
        vies.append(info_selic[2])
        inicio_vigencia.append(info_selic[3])
        fim_vigencia.append(info_selic[4])
        taxa_selic.append(info_selic[5])
        #tban.append(info_selic[6])
        selic_acumulada_periodo.append(info_selic[7])
        selic_media_anual.append(info_selic[8])

dict_selic = {}

dict_selic['reuniao'] = reuniao
dict_selic['data_reuniao'] = data_reuniao
dict_selic['extraordinaria'] = extraordinaria
dict_selic['vies'] = vies
dict_selic['inicio_vigencia'] = inicio_vigencia
dict_selic['fim_vigencia'] = fim_vigencia
dict_selic['taxa_selic'] = taxa_selic
dict_selic['selic_acumulada_periodo'] = selic_acumulada_periodo
dict_selic['selic_media_anual'] = selic_media_anual

selic = dict_selic

def parse_float(value):
    try:
        return float(value.replace(',', '.'))
    except ValueError:
        return None
    except AttributeError:
        return None

def change_data_format(value):
    try:
        data = value.replace("/", '-')
        data = datetime.datetime.strptime(data, "%d-%m-%Y").strftime("%Y-%m-%d")
        return data
    except AttributeError:
        return value
    except ValueError:
        return value

def clear_na(value):
    try:
        return value.replace('n/a', 'não aplicável')
    except AttributeError:
        return value
    
lista_to_insert = [
    [
    valores[0],
    change_data_format(valores[1]),
    valores[2],
    clear_na(valores[3]),
    change_data_format(valores[4]),
    change_data_format(valores[5]),
    parse_float(valores[6]),
    parse_float(valores[7]),
    parse_float(valores[8])
    ]
    for valores in zip(
        dict_selic['reuniao'],
        dict_selic['data_reuniao'],
        dict_selic['extraordinaria'],
        dict_selic['vies'],
        dict_selic['inicio_vigencia'],
        dict_selic['fim_vigencia'],
        dict_selic['taxa_selic'],
        dict_selic['selic_acumulada_periodo'],
        dict_selic['selic_media_anual']
    )
]

try:
    # Conectar ao banco de dados
    conn = psycopg2.connect(host=host, database=database, user=user, password=password, sslmode='require')
    cursor = conn.cursor()

    # Criar o banco de dados, caso não exista
    #cursor.execute("CREATE DATABASE IF NOT EXISTS indices_financeiros;")

    # Criar tabela para armazenar os índices
    create_table_query = """
    CREATE TABLE IF NOT EXISTS selic (
        reuniao VARCHAR(10) NOT NULL,
        data_reuniao DATE NOT NULL PRIMARY KEY,
        extraordinaria BOOLEAN NOT NULL,
        vies VARCHAR(20) NOT NULL,
        inicio_vigencia DATE NOT NULL,
        fim_vigencia DATE,
        taxa_selic NUMERIC NOT NULL,
        selic_acumulada_periodo NUMERIC,
        selic_media_anual NUMERIC
    );
    """
    cursor.execute(create_table_query)

    # Inserir os dados na tabela
    insert_query = """
    INSERT INTO selic (reuniao, data_reuniao, extraordinaria, vies, inicio_vigencia, fim_vigencia, taxa_selic, selic_acumulada_periodo, selic_media_anual)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (data_reuniao) DO UPDATE
    SET reuniao = EXCLUDED.reuniao,
    data_reuniao = EXCLUDED.data_reuniao,
    extraordinaria = EXCLUDED.extraordinaria,
    vies = EXCLUDED.vies,
    inicio_vigencia = EXCLUDED.inicio_vigencia,
    fim_vigencia = EXCLUDED.fim_vigencia,
    taxa_selic = EXCLUDED.taxa_selic,
    selic_acumulada_periodo = EXCLUDED.selic_acumulada_periodo,
    selic_media_anual = EXCLUDED.selic_media_anual;
    """
    cursor.executemany(insert_query, lista_to_insert)

    # Confirmar as alterações no banco de dados
    conn.commit()
    print("Dados inseridos com sucesso!")

except psycopg2.Error as e:
    print(f"Erro ao conectar ou manipular o banco de dados: {e}")
finally:
    if conn:
        cursor.close()
        conn.close()

driver.quit()