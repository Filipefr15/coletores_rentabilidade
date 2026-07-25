import psycopg2, os, time, importlib
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
import pandas as pd

import segmentacao.inicializador as init

importlib.reload(init)

def procurar_sEp500(data):

    load_dotenv()

    host = os.getenv("HOST")
    database = os.getenv("DATABASE")
    user= os.getenv("USER")
    password= os.getenv("PASSWORD")

    service, options = init.start_driver()

    # Inicia-se a instância do Chrome WebDriver com as definidas 'options' e 'service'
    # basicamente o driver É o google chrome.


    lista_indices = []

    urls = [
        'https://finance.yahoo.com/quote/%5EGSPC/history/',
    ]

    lista_indices = ['S&P 500']

    data_desejada = data

    lista_indices_retorno, lista_fechamento, lista_variacao, lista_datas = [], [], [], []

    driver = init.go_to_site(service, options, 'https://finance.yahoo.com/quote/%5EGSPC/history/')
    for url in urls:
        driver.get(url)
        for data in data_desejada:
            try:
                verifica_dia = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//table[@class='table yf-1jecxey noDl hideOnPrint']/tbody/tr/td[text()='"+ data +"']")))
                tr_pai = verifica_dia.find_element(By.XPATH, "..")
                tr_proximo = tr_pai.find_element(By.XPATH, "following-sibling::tr")
            except TimeoutException:
                print("Data não encontrada")
                lista_indices_retorno.append(lista_indices[urls.index(url)])
                lista_fechamento.append('-')
                lista_variacao.append('-')
                lista_datas.append(data)
                continue
            
            lista_indices_retorno.append(lista_indices[urls.index(url)])
            lista_fechamento.append(tr_pai.find_element(By.XPATH, "./td[5]").text.replace(',', ''))
            #para encontrar a variaao, preciso procurar o dia anterior e realizar os calculos.
            valor_anterior = tr_proximo.find_element(By.XPATH, "./td[5]").text.replace(',', '')
            valor_atual = tr_pai.find_element(By.XPATH, "./td[5]").text.replace(',', '')

            variacao_formatada = round((((((float(valor_atual) * 100)/float(valor_anterior))/100)-1)*100), 4)


            lista_variacao.append(variacao_formatada)
            lista_datas.append(data)

    driver.close()

    lista_datas = pd.to_datetime(lista_datas, format='%b %d, %Y').strftime('%Y-%m-%d').tolist()

    dict_index_rv = {'Índice': lista_indices_retorno, 'Data': lista_datas, 'Fechamento': lista_fechamento, 'Variação': lista_variacao}

    lista_to_insert = [
        [
        valores[0],
        valores[1],
        str(valores[2]),
        valores[3],
        ]
        for valores in zip(
            dict_index_rv['Índice'],
            dict_index_rv['Fechamento'],
            dict_index_rv['Variação'],
            dict_index_rv['Data'],
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
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS indices_rv (
            nome VARCHAR(20) NOT NULL,
            valor_indice NUMERIC NOT NULL,
            var_diaria NUMERIC,
            data_consulta DATE NOT NULL,
            CONSTRAINT unique_data_nome_index_rv UNIQUE (data_consulta, nome)
        );
        """
        cursor.execute(create_table_query)

        # Inserir os dados na tabela
        insert_query = """
        INSERT INTO indices_rv (nome, valor_indice, var_diaria, data_consulta)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (data_consulta, nome) DO UPDATE SET
        valor_indice = EXCLUDED.valor_indice,
        var_diaria = EXCLUDED.var_diaria;
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

    #pd = pd.DataFrame({'Índice': lista_indices_retorno, 'Data': lista_datas, 'Fechamento': lista_fechamento, 'Variação': lista_variacao})