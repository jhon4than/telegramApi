import requests
import telebot
from datetime import datetime
from time import sleep
from requests.exceptions import ConnectionError, Timeout
import asyncio
import random


class RouletteBot:
    def __init__(self, telegram_token, chat_id, api_url):
        self.bot = telebot.TeleBot(telegram_token)
        self.chat_id = chat_id
        self.api_url = api_url
        self.sinal = False
        self.indicacao1 = 0
        self.indicacao2 = 0
        self.entrada = 0
        self.todas_entradas = []
        self.operacoes = []
        self.quantidade_greens = 0
        self.quantidade_reds = 0
        self.horarios_envio = [9, 12, 18]
        self.contagem_sinais_enviados = 0
        self.martingale_steps = 2
        self.check_dados = []  # Inicializando check_dados
        self.ultimo_horario_envio = None  # Adiciona esta linha
        print("💰 BOT ROLETA BRASILEIRA - LIGADA! 💰")

    def obter_resultado(self, retries=5, backoff_factor=1.0):
        headers = {"cookie": "vid=1add2388-481c-49f1-b8ab-2bed487ed73c"}
        for attempt in range(retries):
            try:
                response = requests.get(self.api_url, headers=headers)
                response.raise_for_status()
                data = response.json()
                data = data["gameTables"]
                for x in data:
                    if x["gameTableId"] == "103910":
                        try:
                            return x["lastNumbers"]
                        except KeyError:
                            continue
                return []
            except (ConnectionError, Timeout) as e:
                print(f"Falha na conexão ({e}), tentativa {attempt + 1} de {retries}.")
                sleep(attempt * backoff_factor)
            except Exception as e:
                print(f"Erro inesperado: {e}")
                break
        return []

    def caracteristicas(self, data):
        if data is None:
            return []

        caracteristicas = []
        for numero in data:
            try:
                numero = int(numero)
                coluna = (
                    1
                    if numero in range(1, 13)
                    else 2
                    if numero in range(13, 25)
                    else 0
                    if numero == 0
                    else 3
                    if numero in range(25, 37)
                    else 4
                )
                caracteristicas.append({"numero": numero, "coluna": coluna})
            except ValueError:
                continue
        return caracteristicas

    def verificar_alerta(self, data):
        horario_atual = datetime.now().strftime("%H:%M")  # Obtém o horário atual

        data = self.caracteristicas(data)
        numeros = [numero["numero"] for numero in data]
        colunas = [coluna["coluna"] for coluna in data]

        if len(numeros) > 0:
            ultimo_numero = numeros[0]

            if self.sinal:
                self.correcao(numeros, colunas, self.indicacao1, self.indicacao2)
            else:
                if colunas[:2] == [3, 3]:
                    self.sinal = True
                    self.indicacao1 = 1
                    self.indicacao2 = 2
                    self.enviar_sinal(
                        self.indicacao1, self.indicacao2, ultimo_numero, horario_atual
                    )
                elif colunas[:2] == [2, 2]:
                    self.sinal = True
                    self.indicacao1 = 1
                    self.indicacao2 = 3
                    self.enviar_sinal(
                        self.indicacao1, self.indicacao2, ultimo_numero, horario_atual
                    )
                elif colunas[:2] == [1, 1]:
                    self.sinal = True
                    self.indicacao1 = 2
                    self.indicacao2 = 3
                    self.enviar_sinal(
                        self.indicacao1, self.indicacao2, ultimo_numero, horario_atual
                    )

    def correcao(self, numeros, colunas, indicacao1, indicacao2):
        if colunas[0] == indicacao1 or colunas[0] == indicacao2 or colunas[0] == 0:
            self.todas_entradas.append(numeros[0])
            self.green()
            self.reset()
        else:
            self.martingale()

    def enviar_sinal(self, indicacao1, indicacao2, ultimo_numero, horario):
        texto = f"""🎯 Entrada Confirmada 🎯

🖥️ Roleta: ROLETA BRAZA 🇧🇷
🔥 Entrar: {indicacao1}º e {indicacao2}º COLUNA
🛟 Até duas proteções - Cobrir o zero!

🧨 Último número: {ultimo_numero}
<a href="https://www.segurobet.com/slots/320/26560?accounts=*&register=*&btag=1504084_l254743&AFFAGG=&mode=fun&provider=all">💸 Clique aqui para abrir a corretora</a>"""
        retries = 3
        for attempt in range(retries):
          try:
              self.bot.send_message(
                  self.chat_id,
                  text=texto,
                  parse_mode="html",
                  disable_web_page_preview=True,
              )
              self.contagem_sinais_enviados += 1
              break  # Se a mensagem foi enviada com sucesso, sai do loop
          except ConnectionError as e:
              print(f"Erro de conexão ao enviar mensagem: {e}, tentativa {attempt + 1} de {retries}.")
              sleep(attempt + 1)  # Espera um pouco antes de tentar novamente
          except Exception as e:
              print(f"Erro inesperado ao enviar mensagem: {e}")
              break
    def enviar_mensagem_especifica(self):
        texto_mensagem = '''🚨 ATENÇÃO - Iniciando os sinais!
<a href="https://www.segurobet.com/slots/320/26560?accounts=*&register=*&btag=1504084_l254743&AFFAGG=&mode=fun&provider=all">💸 Clique aqui para se cadastrar e lucrar</a>'''
        self.bot.send_message(self.chat_id, texto_mensagem, parse_mode="html")
        
    def martingale(self):
        self.entrada += 1
        if self.entrada <= self.martingale_steps:
            texto = f"⌛️ <b>Vamos iniciar o {self.entrada}° Gale</b>"
            message = self.bot.send_message(self.chat_id, text=texto, parse_mode="html")
            sleep(15)
            self.bot.delete_message(self.chat_id, message_id=message.message_id)
        else:
            self.red()
            self.reset()

    def green(self):
        horario = datetime.now().strftime("%H:%M:%S")
        self.operacoes.append((horario, "GREEN"))
        self.quantidade_greens += 1
        texto = f"✅<b>GREEN! {self.todas_entradas}</b>"
        self.bot.send_message(self.chat_id, text=texto, parse_mode="html")

    def red(self):
        horario = datetime.now().strftime("%H:%M:%S")
        self.operacoes.append((horario, "RED"))
        self.quantidade_reds += 1
        texto = f"<b>❌ Loss...</b>"
        self.bot.send_message(self.chat_id, text=texto, parse_mode="html")

    def generate_report(self, final_report=False):
      data_atual = datetime.now().strftime("%d/%m/%y")
      texto_relatorio = f"📊HISTÓRICO DAS ENTRADAS ({data_atual})‍\n"
      for horario, resultado in self.operacoes:
          texto_relatorio += f"{horario} - {'GREEN ✅' if resultado == 'GREEN' else 'RED ❌'}\n"

      texto_relatorio += f"‍\n✅ GREEN {self.quantidade_greens} x  RED ❌ {self.quantidade_reds}"
      self.bot.send_message(self.chat_id, text=texto_relatorio, parse_mode="html")

      # Reset as variáveis se for o relatório final do dia
      if final_report:
          self.quantidade_greens = 0
          self.quantidade_reds = 0
          self.operacoes.clear()


    def reset(self):
        self.entrada = 0
        self.todas_entradas.clear()
        self.sinal = False

    async def main(self):
        horarios_enviados = {horario: False for horario in self.horarios_envio}
        mensagem_enviada = {horario: False for horario in self.horarios_envio}
        ultimo_horario_envio = None

        while True:
            now = datetime.now()
            hora_atual = now.hour

            # Processa os sinais para cada horário programado
            for horario in self.horarios_envio:
                if hora_atual == horario and not mensagem_enviada[horario]:
                    self.enviar_mensagem_especifica()
                    mensagem_enviada[horario] = True  # Marca que a mensagem foi enviada
                    
                if hora_atual == horario and not horarios_enviados[horario]:
                    data = self.obter_resultado()
                    if data != self.check_dados:
                        self.verificar_alerta(data)
                        self.check_dados = data

                    # Verifica se é necessário gerar o relatório parcial
                    if self.contagem_sinais_enviados >= 5:
                        # Certifique-se de que a última entrada tenha sido processada antes de enviar o relatório
                        if not self.sinal:
                            self.generate_report()
                            self.contagem_sinais_enviados = 0
                            horarios_enviados[horario] = True

            # Gera relatório final se necessário
            if hora_atual > max(self.horarios_envio) and (ultimo_horario_envio is None or ultimo_horario_envio != now.date()):
                # Certifique-se de que a última entrada tenha sido processada antes de enviar o relatório final
                if not self.sinal:
                    self.generate_report(final_report=True)
                    ultimo_horario_envio = now.date()

            # Reseta os horários para o próximo dia
            if now.hour == 0 and now.minute == 0:
                horarios_enviados = {horario: False for horario in self.horarios_envio}

            await asyncio.sleep(5)

# Inicialização e loop principal do bot
if __name__ == "__main__":
    telegram_token = "5666220091:AAGCEWvSx_Y-qfqBl9u8vB-cbMCi_xjjuTw"
    #chat_id = "-1001951559983"
    chat_id = "-1001601471922"
    api_url = "https://casino.betfair.com/api/tables-details"
    bot = RouletteBot(telegram_token, chat_id, api_url)
    asyncio.run(bot.main())
