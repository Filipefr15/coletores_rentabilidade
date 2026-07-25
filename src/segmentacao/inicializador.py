from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def start_driver():
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

    return service, options

def go_to_site(service, options, url):
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    return driver

def max_window_click_cookies(driver, element):
    driver.maximize_window()
    cookies = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, element)))
    cookies.click()