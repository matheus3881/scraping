from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import os
import re

# CONFIGURAÇÕES
URL_LOGIN = ''
USERNAME = ''
PASSWORD = ''

# Setup do Selenium
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

# ==== LOGIN ====
driver.get(URL_LOGIN)

wait.until(EC.presence_of_element_located((By.ID, 'user_name'))).send_keys(USERNAME)
driver.find_element(By.ID, 'user_password').send_keys(PASSWORD)
driver.find_element(By.ID, 'sysverb_login').click()

# ==== PÓS LOGIN - AGUARDAR TÓPICOS ====
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li.sn-widget')))
topicos = driver.find_elements(By.CSS_SELECTOR, 'li.sn-widget')


def scroll_iframe_and_capture(driver, nome_arquivo_base, delay=1.5):
    driver.switch_to.frame("gsft_main")
    
    # Executa script para pegar altura total do conteúdo no iframe
    total_height = driver.execute_script("return document.body.scrollHeight")
    viewport_height = driver.execute_script("return window.innerHeight")

    print(f"Altura total do iframe: {total_height}px, viewport: {viewport_height}px")

    scroll_pos = 0
    count = 1
    os.makedirs("screenshots", exist_ok=True)

    while scroll_pos < total_height:
        # Scrolla para a posição atual
        driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
        time.sleep(delay)  # esperar o conteúdo renderizar

        # Salva screenshot
        filename = f"screenshots/{nome_arquivo_base}_part{count}.png"
        driver.save_screenshot(filename)
        print(f"Screenshot salvo: {filename}")

        scroll_pos += viewport_height
        count += 1

    driver.switch_to.default_content()


# ==== ITERAR TÓPICOS ====
for topico in topicos:
    try:
        nome_topico = topico.find_element(By.CSS_SELECTOR, 'a.nav-application-overwrite span').text.strip()
        print(f"Tópico: {nome_topico}")

        # Expandir o tópico
        botao_expandir = topico.find_element(By.CSS_SELECTOR, 'a.nav-application-overwrite')
        driver.execute_script("arguments[0].click();", botao_expandir)
        time.sleep(1)

        subtopicos = topico.find_elements(By.CSS_SELECTOR, 'a.module-node')
        for subt in subtopicos:
            try:
                nome_sub = subt.text.strip()
                print(f"  Subtópico: {nome_sub}")

                # Limpa nome para salvar arquivo
                nome_arquivo = re.sub(r'[\\/:"*?<>|]+', '-', f"{nome_topico}_{nome_sub}").replace(" ", "_")

                # Clica no subtópico
                driver.execute_script("arguments[0].click();", subt)
                time.sleep(2)

                # Troca para o iframe que sempre está presente
                try:
                    driver.switch_to.frame("gsft_main")
                except:
                    print("⚠️ Não foi possível entrar no iframe gsft_main")
                    continue

                # Aguarda o carregamento de conteúdo dentro do iframe
                try:
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                except TimeoutException:
                    print("⚠️ Conteúdo do iframe demorou para carregar")

                # Criar diretório e salvar print
                os.makedirs("screenshots", exist_ok=True)
                caminho = f"screenshots/{nome_arquivo}.png"
                scroll_iframe_and_capture(driver, nome_arquivo)
                print(f"  ✔️ Screenshot salvo: {caminho}")

            finally:
                # Voltar para fora do iframe e voltar à página anterior
                driver.switch_to.default_content()
                driver.back()
                time.sleep(2)
    except Exception as e:
        print(f"Erro ao processar tópico: {e}")

# ==== FINALIZA ====
driver.quit()
