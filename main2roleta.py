import telebot
import threading
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

TELEGRAM_TOKEN = "5666220091:AAGCEWvSx_Y-qfqBl9u8vB-cbMCi_xjjuTw"
bot = telebot.TeleBot(TELEGRAM_TOKEN)
CHAT_ID = "-1001601471922"
results = []
live_roulette_numbers = []
sinal_enviado = False
ultimo_tempo_sinal = None
contador_rodadas = 0  # Adicionar um contador de rodadas
gale_atual = 0
max_gales = 2  # Defina o número máximo de gales aqui


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


def enviar_sinais():
    global live_roulette_numbers, sinal_enviado, ultimo_tempo_sinal, contador_rodadas, gale_atual
    ultimo_numero = None
    while True:
        time.sleep(3)
        if live_roulette_numbers and (live_roulette_numbers[0] != ultimo_numero):
            numero_atual = live_roulette_numbers[0]
            if numero_atual == "0":  # Se o número atual for 0, apenas aguarde o próximo número
                print("Número 0 detectado, aguardando o próximo número.")
                ultimo_numero = numero_atual  # Atualiza o último número para o número atual que é 0
                continue  # Pula para a próxima iteração do loop

            if not sinal_enviado or (ultimo_tempo_sinal is None or time.time() - ultimo_tempo_sinal > 60):  # Pausa de 60 segundos entre sinais
                bet_columns = determine_bet_columns(numero_atual)
                if bet_columns:
                    message = f"🎯 Entrada Confirmada 🎯\n\n🖥️ Roleta: ROLETA BRAZA 🇧🇷\n🔥 Entrar: Entrar na {bet_columns[0]} e {bet_columns[1]} COLUNA\n🛟 Até duas proteções - Cobrir o zero!\n\n🧨 Último número: {numero_atual}\n\n💸 Clique aqui para abrir a corretora -> [LINK DA PLATAFORMA]"
                    bot.send_message(chat_id=CHAT_ID, text=message)
                    print("Mensagem de entrada confirmada enviada.")
                    sinal_enviado = True
                    ultimo_tempo_sinal = time.time()

            # Aguarda a atualização do número para verificar o resultado
            while True:
                time.sleep(2)
                if live_roulette_numbers[0] != numero_atual:  # Aqui mudamos para verificar contra numero_atual em vez de ultimo_numero
                    numero_novo = live_roulette_numbers[0]
                    break

            if numero_novo != "0":  # Verifica se o novo número não é 0 antes de enviar o resultado
              resultado_coluna = determinar_coluna(numero_novo)
              if resultado_coluna in bet_columns:
                  result_message = f"🟢 GREEN ✅ Número: {numero_novo}"
                  gale_atual = 0  # Reseta o gale se ganhar
              else:
                  result_message = "🔴 LOSS ❌"
                  if gale_atual < max_gales:
                      gale_atual += 1
                      # Envie uma mensagem para o gale aqui
                      bot.send_message(chat_id=CHAT_ID, text=f"Vamos para o Gale {gale_atual}")
                  else:
                      gale_atual = 0  # Reseta o gale se atingir o máximo permitido

              bot.send_message(chat_id=CHAT_ID, text=result_message)
              print(f"Mensagem de resultado enviada: {result_message}")
              results.append(
                  f"{datetime.now().strftime('%H:%M')} - {resultado_coluna} {'✅' if resultado_coluna in bet_columns else '❌'}"
              )
              sinal_enviado = False

              ultimo_numero = numero_novo  # Atualiza o último número para o novo número

              # Aguarda o próximo número diferente do último para começar um novo sinal
              while True:
                  time.sleep(2)
                  if live_roulette_numbers[0] != ultimo_numero:
                      break

              contador_rodadas += 1  # Incrementa o contador de rodadas após cada sinal

              if contador_rodadas >= 5:
                  enviar_relatorio()  # Envia o relatório após 5 rodadas
                  contador_rodadas = 0  # Reseta o contador de rodadas



def resetar_relatorio_a_meianoite():
    global results
    while True:
        # Aguarde até meia-noite para resetar
        agora = datetime.now()
        meianoite = (agora + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        tempo_para_meianoite = (meianoite - agora).total_seconds()
        time.sleep(tempo_para_meianoite)
        results = []  # Resetar os resultados à meia-noite
        contador_rodadas = 0  # Reseta também o contador de rodadas
        salvar_resultados()  # Salvar os resultados vazios para resetar o arquivo
        print("Relatório resetado à meia-noite.")


def salvar_resultados():
    global results
    with open("resultados_roleta.txt", "w") as file:
        for result in results:
            file.write(result + "\n")


def carregar_resultados():
    global results
    try:
        with open("resultados_roleta.txt", "r") as file:
            results = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        results = []


def enviar_relatorio():
    global results
    carregar_resultados()  # Carregar os resultados salvos

    # Verifica se há resultados para incluir no relatório.
    if not results:
        print("Não há resultados para incluir no relatório.")
        return  # Não envia o relatório se não houver resultados

    green_count = sum("✅" in result for result in results)
    loss_count = sum("❌" in result for result in results)
    data_atual = datetime.now().strftime("%d/%m/%Y")
    # Limita os resultados exibidos no relatório aos últimos 5
    resultados_exibidos = results[-5:] if len(results) >= 5 else results
    report_message = (f"📔 RELATÓRIO DE OPERAÇÕES {data_atual}\n\n" + "\n".join(resultados_exibidos) + f"\n\nPlacar: ✅ {green_count} x {loss_count} ❌")
    bot.send_message(chat_id=CHAT_ID, text=report_message)
    salvar_resultados()  # Salvar os resultados após enviar o relatório


def determine_bet_columns(last_number):
    try:
        last_number = int(last_number)
        if last_number == 0:  # Se o último número for 0, é sempre GREEN.
            return ("GREEN", "GREEN")
        elif 1 <= last_number <= 12:
            return (
                "2ª",
                "3ª",
            )  # Apostar nas colunas 2 e 3 se o último número estiver na coluna 1.
        elif 13 <= last_number <= 24:
            return (
                "1ª",
                "3ª",
            )  # Apostar nas colunas 1 e 3 se o último número estiver na coluna 2.
        elif 25 <= last_number <= 36:
            return (
                "1ª",
                "2ª",
            )  # Apostar nas colunas 1 e 2 se o último número estiver na coluna 3.
    except ValueError:
        return None, None


def determinar_coluna(numero):
    try:
        numero = int(numero)
        if numero == 0:
            return "GREEN"  # GREEN é uma condição especial para o número 0.
        elif 1 <= numero <= 12:
            return "1ª"
        elif 13 <= numero <= 24:
            return "2ª"
        elif 25 <= numero <= 36:
            return "3ª"
    except ValueError:
        return None


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "I'm your Roulette Strategy Bot.")


@bot.message_handler(commands=["report"])
def report(message):
    report_message = "📔 RELATÓRIO DE OPERAÇÕES\n\n" + "\n".join(results)
    bot.send_message(message.chat.id, report_message)


if __name__ == "__main__":
    carregar_resultados()  # Carregar os resultados ao iniciar o script
    threading.Thread(target=monitor_roleta, daemon=True).start()
    threading.Thread(target=enviar_sinais, daemon=True).start()
    threading.Thread(target=resetar_relatorio_a_meianoite, daemon=True).start()
    bot.polling(none_stop=True)
