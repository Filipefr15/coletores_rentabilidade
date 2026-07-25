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

#liga a instância do Chrome WebDriver, basicamente o driver É o google chrome.
driver = init.go_to_site(service, options, 'http://www.ipeadata.gov.br/ExibeSerie.aspx?serid=38391')

tab_ipca = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "grd_DXMainTable")))

tbody_tab_ipca = WebDriverWait(tab_ipca, 10).until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
#aqui eu pego apenas o cabeçalho
tr_excluido = WebDriverWait(tbody_tab_ipca, 10).until(EC.presence_of_element_located((By.ID, "grd_DXHeadersRow0")))
#aqui eu decido pegar todas as informações após o cabeçalho, para evitar perca de tempo com limpeza desnecessária
tr_tbody_tab_ipca = WebDriverWait(tr_excluido, 10).until(EC.presence_of_all_elements_located((By.XPATH, "following-sibling::tr")))

data, indice = [], []

for count, _ in enumerate(tr_tbody_tab_ipca):
    info_ipca = tr_tbody_tab_ipca[count].text.split()
    data.append(info_ipca[0])
    indice.append(info_ipca[1])

dict_ipca = {}

dict_ipca['data'] = data
dict_ipca['indice'] = indice

ipca = dict_ipca

def parse_float(value):
    try:
        return float(value.replace(',', '.'))
    except ValueError:
        return None
    except AttributeError:
        return None

def change_data_format(value):
    try:
        data = value.replace(".", '-')
        data = data + '-01'
        return data
    except AttributeError:
        return value
    except ValueError:
        return value
    
lista_to_insert = [
    [
    change_data_format(valores[0]),
    parse_float(valores[1]),
    ]
    for valores in zip(
        dict_ipca['data'],
        dict_ipca['indice']
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
    CREATE TABLE IF NOT EXISTS ipca (
        data DATE NOT NULL PRIMARY KEY,
        indice NUMERIC
    );
    """
    cursor.execute(create_table_query)

    # Inserir os dados na tabela
    insert_query = """
    INSERT INTO ipca (data, indice)
    VALUES (%s, %s)
    ON CONFLICT (data) DO UPDATE
    SET data = EXCLUDED.data,
    indice = EXCLUDED.indice;
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