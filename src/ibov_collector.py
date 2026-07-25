import psycopg2, os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("HOST")
database = os.getenv("DATABASE")
user= os.getenv("USER")
password= os.getenv("PASSWORD")

# A classe Service é usada para iniciar uma instância do Chrome WebDriver
service = Service()

# webdriver.ChromeOptions é usado para definir a preferência para o browser do Chrome
options = webdriver.ChromeOptions()

options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-images")
options.add_argument("--disable-javascript")

# Inicia-se a instância do Chrome WebDriver com as definidas 'options' e 'service'
# basicamente o driver É o google chrome.
driver = webdriver.Chrome(service=service, options=options)

url = 'https://br.investing.com/indices/bovespa-historical-data'

driver.get(url)

#fechar anúncio que aparece na página
div_id_fechar_anuncio = driver.find_element(By.ID , ":rl:")

fechar_anuncio = div_id_fechar_anuncio.find_elements(By.TAG_NAME , "svg")

for count, _ in enumerate(fechar_anuncio):
    try:
        fechar_anuncio[count].click()
    except:
        continue
    break

#pegar tabela de dados
tabela_ibovespa = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.TAG_NAME, "table")))

tbody_tabela_ibovespa = WebDriverWait(tabela_ibovespa[0], 20).until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))

tr_tabela_ibovespa = WebDriverWait(tbody_tabela_ibovespa, 20).until(EC.presence_of_all_elements_located((By.TAG_NAME, "tr")))

data, fechamento, abertura, minimo, maximo, volume, variacao = [], [], [], [], [], [], []

for count, _ in enumerate(tr_tabela_ibovespa):

    info_ibovespa = tr_tabela_ibovespa[count].text.split()

    data.append(info_ibovespa[0])
    fechamento.append(info_ibovespa[1])
    abertura.append(info_ibovespa[2])
    maximo.append(info_ibovespa[3])
    minimo.append(info_ibovespa[4])
    volume.append(info_ibovespa[5])
    variacao.append(info_ibovespa[6])

dict_ibovespa = {}

dict_ibovespa['data'] = data
dict_ibovespa['fechamento'] = fechamento
dict_ibovespa['abertura'] = abertura
dict_ibovespa['minimo'] = minimo
dict_ibovespa['maximo'] = maximo
dict_ibovespa['volume'] = volume
dict_ibovespa['variacao'] = variacao

selic = dict_ibovespa

def change_to_numeric(value):
    try:
        if 'B' in value:
            return float(value.replace('B', '').replace(',', '.')) * 1000000000
        elif 'M' in value:
            return float(value.replace('M', '').replace(',', '.')) * 1000000
    except ValueError:
        return None
    except AttributeError:
        return None
    
def clean_percent(value):
    try:
        return value.replace('%', '').replace('+', '')
    except ValueError:
        return None
    except AttributeError:
        return None
    
def uniform_data(data):
    return data.replace('.', '-')

lista_to_insert = [
    [
    uniform_data(valores[0]),
    valores[1],
    valores[2],
    valores[3],
    valores[4],
    str(change_to_numeric(valores[5])),
    clean_percent(valores[6])
    ]
    for valores in zip(
        dict_ibovespa['data'],
        dict_ibovespa['fechamento'],
        dict_ibovespa['abertura'],
        dict_ibovespa['maximo'],
        dict_ibovespa['minimo'],
        dict_ibovespa['volume'],
        dict_ibovespa['variacao']
    )
]

print(lista_to_insert)

try:
    # Conectar ao banco de dados
    conn = psycopg2.connect(host=host, database=database, user=user, password=password)
    cursor = conn.cursor()

    # Criar o banco de dados, caso não exista
    #cursor.execute("CREATE DATABASE IF NOT EXISTS indices_financeiros;")

    # Criar tabela para armazenar os índices
    create_table_query = """
    CREATE TABLE IF NOT EXISTS ibovespa (
        data DATE NOT NULL PRIMARY KEY,
        fechamento NUMERIC NOT NULL,
        abertura NUMERIC NOT NULL,
        minimo NUMERIC NOT NULL,
        maximo NUMERIC NOT NULL,
        volume NUMERIC NOT NULL,
        variacao NUMERIC NOT NULL
    );
    """
    cursor.execute(create_table_query)

    # Inserir os dados na tabela
    insert_query = """
    INSERT INTO ibovespa (data, fechamento, abertura, minimo, maximo, volume, variacao)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (data) DO UPDATE
    SET fechamento = EXCLUDED.fechamento,
    abertura = EXCLUDED.abertura,
    minimo = EXCLUDED.minimo,
    maximo = EXCLUDED.maximo,
    volume = EXCLUDED.volume,
    variacao = EXCLUDED.variacao;
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