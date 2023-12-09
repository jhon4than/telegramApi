import requests
import telebot
import pytz
import time
from datetime import datetime, timedelta
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

brasilia_timezone = pytz.timezone("America/Sao_Paulo")
hora_inicio = (datetime.now() + timedelta(minutes=1)).astimezone(brasilia_timezone).strftime("%H:%M")

# Configurações do bot
telegram_token = "5666220091:AAGCEWvSx_Y-qfqBl9u8vB-cbMCi_xjjuTw"
chat_id = "-1001601471922"

# Configurações do jogo
API_URL = "https://casino.betfair.com/api/tables-details"
MARTINGALE_STEPS = 1

# Inicialização do bot
bot = telebot.TeleBot(telegram_token)
# Envia mensagem de início do robô
msg = f'''<b>JÁ ESTOU ANALISANDO POSSÍVEIS ENTRADAS</b> 🔥
Às {hora_inicio} começaremos com as nossas operações'''
bot.send_message(chat_id=chat_id, text=msg, parse_mode="html")

# Variáveis de controle
check_resultado = []
sinal = False
indicacao1 = 0
indicacao2 = 0
entrada = 0
todas_entradas = []
operacoes = []
quantidade_operacoes = 0
quatidade_greens = 0
quatidade_reds = 0
live_roulette_numbers = []
check_dados = []

# Função para obter o resultado atual do jogo
def obter_resultado():
    headers = {"cookie": "vid=210bec56-62f7-4616-939d-077cf4ff0f25"}
    response = requests.get(API_URL, headers=headers)
    if response.status_code != 200:
        return []

    data = response.json()
    data = data['gameTables']
    for x in data:
        if x['gameTableId'] == '103910':
            try:
                data = x['lastNumbers']
                return data
            except KeyError:
                continue

def monitor_roleta():
    global live_roulette_numbers
    driver = webdriver.Chrome()
    driver.get("https://casino.betfair.com/pt-br/c/roleta")
    wait = WebDriverWait(driver, 20)
    while True:
        game_tile = wait.until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 'div[data-gameuid="roleta-ao-vivo-cev"]')
            )
        )
        number_elements = wait.until(
            EC.visibility_of_any_elements_located(
                (
                    By.CSS_SELECTOR,
                    'div[data-gameuid="roleta-ao-vivo-cev"] .results span.number',
                )
            )
        )
        live_roulette_numbers = [element.text for element in number_elements]
        print("Novos números detectados:", live_roulette_numbers)
        time.sleep(5)

def caracteristicas(data):
    if data is None:
        return []

    caracteristicas = []
    for numero in data:
        try:
            numero = int(numero)
            coluna = 1 if numero in [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34] else 2 if numero in [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35] else 0 if numero in [0] else 3
            caracteristicas.append({'numero': numero, 'coluna': coluna})
        except ValueError:
            continue
    return caracteristicas

def verificar_alerta(data):
    global sinal
    global indicacao1
    global indicacao2
    global ultimo_numero 

    data = caracteristicas(data)
    numeros = [numero['numero'] for numero in data]
    colunas = [coluna['coluna'] for coluna in data]
    if len(numeros) > 0:
        ultimo_numero = numeros[0]

        if sinal == True:
            correcao(numeros, colunas, indicacao1, indicacao2)
        else:
            if colunas[:2] == [1,1]:
                sinal = True
                indicacao1 = 1
                indicacao2 = 2
                padrao = 'Padrão Earth'
                enviar_sinal(indicacao1, indicacao2, ultimo_numero, padrao)
            if colunas[:3] == [3,3]:
                sinal = True
                indicacao1 = 1
                indicacao2 = 3
                padrao = 'Padrão Fire'
                enviar_sinal(indicacao1, indicacao2, ultimo_numero, padrao)
            if colunas[:3] == [2,2]:
                sinal = True
                indicacao1 = 2
                indicacao2 = 3
                padrao = 'Padrão Air'
                enviar_sinal(indicacao1, indicacao2, ultimo_numero, padrao)
				
    return

def correcao(numeros, colunas, indicacao1, indicacao2):
    global todas_entradas
    if colunas[0] == indicacao1 or colunas[0] == indicacao2 or colunas[0] == 0:
        todas_entradas.append(numeros[0])
        green(numeros[0])
        reset()
    else:
        martingale()
    return

def enviar_sinal(indicacao1, indicacao2, ultimo_numero, padrao):
    brasilia_timezone = pytz.timezone("America/Sao_Paulo")
    hora_inicio = datetime.now().astimezone(brasilia_timezone).strftime("%H:%M")
    hora_final = (datetime.now() + timedelta(minutes=8)).astimezone(brasilia_timezone).strftime("%H:%M")

    texto = f'''🎯 Entrada Confirmada 🎯

🖥️ Roleta: ROLETA BRAZA 🇧🇷
🔥 Entrar: {indicacao1}º e {indicacao2}º COLUNA
🛟 Até duas proteções - Cobrir o zero!

🧨 Último número: {ultimo_numero}

💸 Clique aqui para abrir a corretora [ <a href="https://google.com">Aperte aqui</a>]'''
    bot.send_message(chat_id=chat_id, text=texto, parse_mode="html", disable_web_page_preview=True)
    return

def martingale():
    global entrada
    global MARTINGALE_STEPS
    entrada += 1

    if entrada <= MARTINGALE_STEPS:
        texto = f"🔁 <b>Estamos no {entrada}° gale</b>"
        message = bot.send_message(chat_id=chat_id, text=texto, parse_mode="html")
        time.sleep(15)
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
    else:
        red()
        reset()
    return

def green(numero):
    global quatidade_greens
    global todas_entradas
    global operacoes
    global quantidade_operacoes
    quantidade_operacoes += 1
    quatidade_greens += 1

    texto = f"{numero} ✅ GREEN"
    bot.send_message(chat_id=chat_id, text=texto, parse_mode="html")

    # Adicionar mensagem de "Vamos para a próxima!"
    mensagem_proxima = "Vamos para a próxima!"
    bot.send_message(chat_id=chat_id, text=mensagem_proxima, parse_mode="html")

    brasilia_timezone = pytz.timezone("America/Sao_Paulo")
    hora_green = datetime.now().astimezone(brasilia_timezone).strftime("%H:%M")

    msg = f'''{hora_green}  >  {numero} GREEN ✅'''
    operacoes.append(msg)
    return

def red():
    global quatidade_reds
    global todas_entradas
    global operacoes
    global quantidade_operacoes
    quantidade_operacoes += 1
    quatidade_reds += 1

    texto = f"<b>❌ {ultimo_numero} RED</b>"
    bot.send_message(chat_id=chat_id, text=texto, parse_mode="html")

    brasilia_timezone = pytz.timezone("America/Sao_Paulo")
    hora_red = datetime.now().astimezone(brasilia_timezone).strftime("%H:%M:%S")

    msg = f'''{hora_red}  >  RED ❌'''
    operacoes.append(msg)
    return

def generate_report():
    global quatidade_greens
    global quatidade_reds
    global operacoes
    global quantidade_operacoes
    result = '\n'.join(str(item) for item in operacoes)
    total = quatidade_greens + quatidade_reds
    porcentagem = (quatidade_greens / total) * 100
    porcentagen = format(porcentagem, '.2f')
    data = datetime.today().strftime('%d/%m/%y')

    texto = f'''📊 HISTÓRICO DAS ENTRADAS ({data})

{result}

🎯 Todas as Entradas: {total}
✅ Green: <b>{quatidade_greens}</b>
❌ Red: <b>{quatidade_reds}</b>
🚀 Assertividade: <b>{porcentagen}%</b>'''
    bot.send_message(chat_id=chat_id, text=texto, parse_mode="html")
    quantidade_operacoes = 0
    return
def reset():
    global sinal
    global entrada
    global todas_entradas

    entrada = 0
    todas_entradas.clear()
    sinal = False
    return
	
def reset():
    global sinal
    global entrada
    global todas_entradas

    entrada = 0
    todas_entradas.clear()
    sinal = False
    return
	
def main():
    # Inicia a thread de monitoramento uma única vez
    threading.Thread(target=monitor_roleta, daemon=True).start()
    time.sleep(30)
    while True:
        # Use live_roulette_numbers para a lógica do jogo
        global check_dados
        data = live_roulette_numbers
        if data != check_dados:
            verificar_alerta(data)
            check_dados = data.copy()  # Faz uma cópia dos dados para evitar conflitos
            if quantidade_operacoes >= 10:
                generate_report()

        time.sleep(5)
# while True:
#     data = obter_resultado()

#     if data != check_dados:
#         verificar_alerta(data)
#         check_dados = data
#         if quantidade_operacoes >= 10:
#             generate_report()
#     time.sleep(5) 
if __name__ == "__main__":
    main()