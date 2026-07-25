import psycopg2, os, time, importlib
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import pandas as pd
import segmentacao.inicializador as init

importlib.reload(init)

##data aqui: modelo '13022025'
def procurar_ima_idka(data):

    load_dotenv()

    host = os.getenv("HOST")
    database = os.getenv("DATABASE")
    user= os.getenv("USER")
    password= os.getenv("PASSWORD")

    service, options = init.start_driver()

    # Inicia-se a instância do Chrome WebDriver com as definidas 'options' e 'service'
    # basicamente o driver É o google chrome.

    driver = init.go_to_site(service, options, 'https://www.anbima.com.br/pt_br/informar/consulta-idka.htm')
    driver2 = init.go_to_site(service, options, 'https://www.anbima.com.br/pt_br/informar/ima-resultados-diarios.htm')

    init.max_window_click_cookies(driver, 'LGPD_ANBIMA_global_sites__text__btn')
    init.max_window_click_cookies(driver2, 'LGPD_ANBIMA_global_sites__text__btn')

    lista_datas = data

    def parse_float(value):
        try:
            return float(value.replace('.', '').replace(',', '.'))
        except ValueError:
            return None
        except AttributeError:
            return None

    def clicar_botao_enviar(driver, path):
        iframe_button_enviar = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, path)))
        driver.switch_to.frame(iframe_button_enviar[0])
        
    def inserir_data(driver, path, datas):
        data_pesquisa = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, path)))
        data_pesquisa.click()
        data_pesquisa.send_keys(Keys.SHIFT, Keys.ARROW_UP)
        data_pesquisa.send_keys(Keys.DELETE)  
        data_pesquisa.send_keys(datas)

    def envia_abre_aba(driver, path):
        valueElements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, path)))
        valueElements[3].click()

    def inserir_info_listas(driver, path):
        lista = []
        values_list = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.ID, path)))
        for values in values_list:
            lista.append(values.text)
        return lista

    def inserir_info_lista_data(driver, path):
        lista = []
        values_list = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.ID, path)))
        for values in values_list:
            lista.append(values.text.replace("/", "-"))
        return lista

    def value_elements_preventing_stale_element_exception(driver, path):
        lista = []
        try:
            valueElements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, path)))
        except StaleElementReferenceException:
            valueElements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, path)))
        for count, _ in enumerate(valueElements):
            lista.append(valueElements[count].text)
        return lista

    time.sleep(2)
    #aguardando 2 segundos antes de procurar os iframes e "mudar" para dentro dele.
    for count, _ in enumerate(lista_datas):
        if count == 0:
            clicar_botao_enviar(driver, "full")
        clicar_botao_enviar(driver2, "full")
        try:
            inserir_data(driver, "/html/body/table/tbody/tr[1]/td/div/table/tbody/tr[2]/td/form/div/div/fieldset[2]/table/tbody/tr/td[1]/input[2]", lista_datas[count])
            inserir_data(driver2, "/html/body/table/tbody/tr/td/div/table/tbody/tr[2]/td/div[3]/form/div/fieldset[3]/table/tbody/tr/td/input[2]", lista_datas[count])
        except IndexError:
            print("Programa finalizado.")
            break

        #agora dentro dos iframes, procuro todas as tags "img" e clico na [3] (é a que "envia" ou "abre" a aba de rentabilidades ima e idka2)
        envia_abre_aba(driver, "img")
        envia_abre_aba(driver2, "img")

        #sai do iframe para a pagina default e em seguida troca de aba (apenas no driver2, que é o único que abre outra aba)
        driver2.switch_to.default_content()
        driver2.switch_to.window(driver2.window_handles[1])

        try:
            lista_tudo = value_elements_preventing_stale_element_exception(driver, "td")
        except StaleElementReferenceException:
            lista_tudo = value_elements_preventing_stale_element_exception(driver, "td")
            
        data_dia = ""
        dataPesquisa = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "b")))
        for count, _ in enumerate(dataPesquisa):
            if len(dataPesquisa[count].text) > 10:
                data_dia = dataPesquisa[count].text
        data_dia = data_dia.replace("Resultado Diário - ", "")

        lista_refinada, lista_nomes, lista_data_dia_consulta, lista_num_indices, lista_var_diaria, lista_var_mes, lista_var_ano, lista_var_ult_12meses, lista_var_ult_24meses = lista_tudo[20:129], [], [], [], [], [], [], [], []

        lista_nomes = inserir_info_listas(driver2, 'Dat1')
        lista_data_dia_consulta = inserir_info_listas(driver2, 'Dat2')
        lista_num_indices = inserir_info_listas(driver2, 'Dat3')
        lista_var_diaria = inserir_info_listas(driver2, 'Dat4')
        lista_var_mes = inserir_info_listas(driver2, 'Dat5')
        lista_var_ano = inserir_info_listas(driver2, 'Dat6')
        lista_var_ult_12meses = inserir_info_listas(driver2, 'Dat7')
        lista_var_ult_24meses = inserir_info_listas(driver2, 'Dat8')

        for count, _ in enumerate(lista_refinada):
            if 'IDkA' in lista_refinada[count]:
                lista_nomes.append(lista_refinada[count])
                lista_num_indices.append(lista_refinada[count+1])
                lista_var_diaria.append(lista_refinada[count+2])
                lista_var_mes.append(lista_refinada[count+3])
                lista_var_ano.append(lista_refinada[count+4])
                lista_var_ult_12meses.append(lista_refinada[count+5])
                lista_var_ult_24meses.append(None)
                lista_data_dia_consulta.append(data_dia)

        dict_titulos_publicos = {}

        #convertendo as datas de DD/MM/YYYY para YYYY-MM-DD
        lista_data_dia_consulta = pd.to_datetime(lista_data_dia_consulta, format='%d/%m/%Y').strftime('%Y-%m-%d').tolist()

        dict_titulos_publicos['Índices'] = lista_nomes
        dict_titulos_publicos['Valor Índices'] = lista_num_indices
        dict_titulos_publicos['Var Diária (%)'] = lista_var_diaria
        dict_titulos_publicos['Var Mês (%)'] = lista_var_mes
        dict_titulos_publicos['Var Ano (%)'] = lista_var_ano
        dict_titulos_publicos['Var 12 Meses (%)'] = lista_var_ult_12meses
        dict_titulos_publicos['Var 24 Meses (%)'] = lista_var_ult_24meses
        dict_titulos_publicos['Data Consulta'] = lista_data_dia_consulta

        lista_to_insert = [
            [
            valores[0],
            str(parse_float(valores[1])),
            str(parse_float(valores[2])),
            str(parse_float(valores[3])),
            str(parse_float(valores[4])),
            str(parse_float(valores[5])),
            str(parse_float(valores[6])) if valores[6] is not None else parse_float(valores[6]),
            valores[7]
            ]
            for valores in zip(
                dict_titulos_publicos['Índices'],
                dict_titulos_publicos['Valor Índices'],
                dict_titulos_publicos['Var Diária (%)'],
                dict_titulos_publicos['Var Mês (%)'],
                dict_titulos_publicos['Var Ano (%)'],
                dict_titulos_publicos['Var 12 Meses (%)'],
                dict_titulos_publicos['Var 24 Meses (%)'],
                dict_titulos_publicos['Data Consulta']
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
            CREATE TABLE IF NOT EXISTS indices (
                nome VARCHAR(20) NOT NULL,
                valor_indice NUMERIC NOT NULL,
                var_diaria NUMERIC,
                var_mes NUMERIC,
                var_ano NUMERIC,
                var_12_meses NUMERIC,
                var_24_meses NUMERIC,
                data_consulta DATE NOT NULL,
                CONSTRAINT unique_data_nome UNIQUE (data_consulta, nome)
            );
            """
            cursor.execute(create_table_query)

            # Inserir os dados na tabela
            insert_query = """
            INSERT INTO indices (nome, valor_indice, var_diaria, var_mes, var_ano, var_12_meses, var_24_meses, data_consulta)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (data_consulta, nome) DO UPDATE SET
            valor_indice = EXCLUDED.valor_indice,
            var_diaria = EXCLUDED.var_diaria,
            var_mes = EXCLUDED.var_mes,
            var_ano = EXCLUDED.var_ano,
            var_12_meses = EXCLUDED.var_12_meses,
            var_24_meses = EXCLUDED.var_24_meses;
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

        #volta para pagina inicial.
        driver.execute_script("window.history.go(-1)")
        driver2.close()
        driver2.switch_to.window(driver2.window_handles[0])