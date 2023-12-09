from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()

driver.get("https://casino.betfair.com/pt-br/c/roleta")

wait = WebDriverWait(driver, 20)  
while True:
    game_tile = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, 'div[data-gameuid="roleta-ao-vivo-cev"]')
    ))

    number_elements = wait.until(EC.visibility_of_any_elements_located(
        (By.CSS_SELECTOR, 'div[data-gameuid="roleta-ao-vivo-cev"] .results span.number')
    ))

    live_roulette_numbers = [element.text for element in number_elements]

    print("Live Roulette Numbers:", live_roulette_numbers)

    time.sleep(5)

