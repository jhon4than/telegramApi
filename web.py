from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

app = Flask(__name__)

@app.route('/get-roulette-numbers', methods=['GET'])
def get_roulette_numbers():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run headless Chrome
    options.add_argument('--no-sandbox')  # Bypass OS security model
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

    try:
        driver.get("https://casino.betfair.com/pt-br/c/roleta")
        wait = WebDriverWait(driver, 20)
        
        game_tile = wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'div[data-gameuid="roleta-ao-vivo-cev"]')
        ))

        number_elements = game_tile.find_elements(By.CSS_SELECTOR, '.results span.number')
        numbers = [elem.text for elem in number_elements]

    finally:
        driver.quit()

    return jsonify({'numbers': numbers})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
