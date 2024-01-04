from datetime import datetime, timedelta  # Import timedelta here
from telebot.apihelper import ApiException
import requests
import telebot
from time import sleep
from requests.exceptions import ConnectionError, Timeout
from requests.exceptions import HTTPError
import asyncio
import random
import json

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
        self.horarios_envio = [9, 12, 19]
        self.contagem_sinais_enviados = 0
        self.martingale_steps = 2
        self.check_dados = []  # Inicializando check_dados
        self.ultimo_horario_envio = None  # Adiciona esta linha
        self.report_file = "daily_report.json"
        self.load_report()

        print("💰 BOT ROLETA BRASILEIRA - LIGADA! 💰")
    
    def horario_ajustado(self):
        return (datetime.now() - timedelta(hours=3)).strftime('%d-%m-%Y %H:%M')

    def load_report(self):
        try:
            with open(self.report_file, 'r') as file:
                # Verifica se o arquivo está vazio
                if file.read(1):
                    file.seek(0)  # Retorna para o início do arquivo após verificar
                    data = json.load(file)
                    self.operacoes = data.get("operacoes", [])
                    self.quantidade_greens = data.get("quantidade_greens", 0)
                    self.quantidade_reds = data.get("quantidade_reds", 0)
                else:
                    # Se o arquivo estiver vazio, inicializa com valores padrão
                    self.operacoes = []
                    self.quantidade_greens = 0
                    self.quantidade_reds = 0
                print("Relatório carregado com sucesso.")
        except FileNotFoundError:
            print("Arquivo de relatório não encontrado. Iniciando com dados vazios.")
            self.operacoes = []
            self.quantidade_greens = 0
            self.quantidade_reds = 0
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON. Iniciando com dados vazios.")
            self.operacoes = []
            self.quantidade_greens = 0
            self.quantidade_reds = 0

    def save_report(self):
        data = {
            "operacoes": self.operacoes,
            "quantidade_greens": self.quantidade_greens,
            "quantidade_reds": self.quantidade_reds
        }
        try:
            with open(self.report_file, 'w') as file:
                json.dump(data, file)
        except IOError as e:
            print(f"Erro ao salvar o relatório: {e}")
        except Exception as e:
            print(f"Erro desconhecido ao salvar o relatório: {e}")


    def clear_report_file(self):
        try:
            with open(self.report_file, 'w') as file:
                json.dump({}, file)
        except IOError as e:
            print(f"Erro em limpar relatório: {e}")
        except Exception as e:
            print(f"Erro desconhecido ao limpar relatório: {e}")

        

    def obter_resultado(self, retries=5, backoff_factor=1.0):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "cookie": "vid=1add2388-481c-49f1-b8ab-2bed487ed73c"
        }
        for attempt in range(retries):
            try:
                response = requests.get(self.api_url, headers=headers)
                response.raise_for_status()
                data = response.json()
                # Validação de dados adicionada
                if 'gameTables' in data:
                    for x in data['gameTables']:
                        if x['gameTableId'] == '103910' and 'lastNumbers' in x:
                            return x['lastNumbers']
                return []
            except (ConnectionError, Timeout, HTTPError) as e:
                print(f"Erro de rede ({e}), tentativa {attempt + 1} de {retries}.")
                sleep(attempt * backoff_factor)
            except Exception as e:
                print(f"Erro inesperado: {e}")
                break  # Em caso de erro desconhecido, sai do loop

        return []

    def caracteristicas(self, data):
        if data is None:
            return []

        caracteristicas = []
        for numero in data:
            try:
                numero = int(numero)
                coluna = 1 if numero in [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34] else 2 if numero in [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35] else 0 if numero in [0] else 3 if numero in [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36] else 4
                caracteristicas.append({"numero": numero, "coluna": coluna})
            except ValueError:
                continue
        return caracteristicas

    def verificar_alerta(self, data):
        horario_atual = self.horario_ajustado()  # Alterado para usar o horário ajustado

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

🖥️ Roleta: ROLETA BRAZILEIRA 🇧🇷
🔥 Entrar: {indicacao1}º e {indicacao2}º COLUNA
🛟 Até duas proteções - Cobrir o zero!

🧨 Último número: {ultimo_numero}
<a href="https://www.segurobet.com/slots/320/26560?accounts=*&register=*&btag=1504084_l254743&AFFAGG=&mode=fun&provider=all">💸 Clique aqui para abrir a corretora</a>"""
        print(f"Enviando sinal para as colunas {indicacao1} e {indicacao2}, último número: {ultimo_numero}. Horário: {horario}")
        retries = 3
        backoff_factor = 1
        for attempt in range(retries):
            try:
                self.bot.send_message(
                    self.chat_id,
                    text=texto,
                    parse_mode="html",
                    disable_web_page_preview=True,
                )
                self.contagem_sinais_enviados += 1
                print("Sinal enviado com sucesso.")
                break
            except ConnectionError as e:
                print(f"Erro de conexão ao enviar mensagem: {e}, tentativa {attempt + 1} de {retries}.")
                sleep(attempt * backoff_factor)
            except Exception as e:
                print(f"Erro desconhecido ao enviar mensagem: {e}")
                sleep(attempt * backoff_factor)
        
    def enviar_mensagem_especifica(self):
        mensageminiciando = '''⏳ 5 minutos para iniciar os sinais!'''
        max_retries = 3
        backoff_factor = 1
        for attempt in range(max_retries):
            try:
                self.bot.send_message(self.chat_id, mensageminiciando, parse_mode="html")
                break
            except requests.exceptions.ConnectionError:
                sleep(attempt * backoff_factor)
            except Exception as e:
                print(f"Erro inesperado: {e}")
                break
        print(f"Esperando tempo de 5 minutos para começar enviar sinais!")
        sleep(360)
        texto_mensagem = '''🚨 ATENÇÃO - Iniciando os sinais!
<a href="https://www.segurobet.com/slots/320/26560?accounts=*&register=*&btag=1504084_l254743&AFFAGG=&mode=fun&provider=all">💸 Clique aqui para se cadastrar e lucrar</a>'''
        max_retries = 3  # Número máximo de tentativas
        backoff_factor = 1  # Fator de atraso

        for attempt in range(max_retries):
            try:
                self.bot.send_message(self.chat_id, texto_mensagem, parse_mode="html")
                break  # Se a mensagem foi enviada com sucesso, sai do loop
            except requests.exceptions.ConnectionError:
                sleep(attempt * backoff_factor)  # Espera um pouco antes de tentar novamente
            except Exception as e:
                print(f"Erro inesperado: {e}")
                break
        print(f"Iniciando...")

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
        horario = self.horario_ajustado() 
        self.operacoes.append((horario, "GREEN"))
        self.quantidade_greens += 1
        texto = f"✅<b>GREEN! {self.todas_entradas}</b>"
        self.bot.send_message(self.chat_id, text=texto, parse_mode="html")
        print(f"Entrada GREEN no horário {horario}. Total de GREENs: {self.quantidade_greens} Numero :{self.todas_entradas}")

    def red(self):
        horario = self.horario_ajustado() 
        self.operacoes.append((horario, "RED"))
        self.quantidade_reds += 1
        texto = f"<b>❌ Loss...</b>"
        self.bot.send_message(self.chat_id, text=texto, parse_mode="html")
        print(f"Entrada RED no horário {horario}. Total de REDs: {self.quantidade_reds} Numero :{self.todas_entradas}")

    def data_atual(self):
        return datetime.now().strftime('%d/%m/%Y')

    def generate_report(self, final_report=False):
        data_atual = self.data_atual()
        texto_relatorio = f"📊HISTÓRICO DAS ENTRADAS - {data_atual}\n\n"

        for horario, resultado in self.operacoes:
            if horario:
                # Extrai apenas a parte do horário da string
                horario_formatado = horario.split(' ')[1]
            else:
                horario_formatado = "Horário Desconhecido"

            texto_relatorio += f"{horario_formatado} - {'GREEN ✅' if resultado == 'GREEN' else 'RED ❌'}\n"

        texto_relatorio += f"\n✅ GREEN {self.quantidade_greens} x  RED ❌ {self.quantidade_reds}"
        self.bot.send_message(self.chat_id, text=texto_relatorio, parse_mode="html")

        print("Gerando relatório...")
        self.save_report()
        print("Esperando Próximo horário...")

        if final_report:
            self.clear_report_file()
            print("Relatório final do dia gerado e resetado.")

    def reset(self):
        self.entrada = 0
        self.todas_entradas.clear()
        self.sinal = False

    async def main(self):
        horarios_enviados = {horario: False for horario in self.horarios_envio}
        mensagem_enviada = {horario: False for horario in self.horarios_envio}
        ultimo_horario_envio = None

        while True:
            now = datetime.now() - timedelta(hours=3)
            hora_atual = now.hour

            # Processa os sinais para cada horário programado
            for horario in self.horarios_envio:
                if hora_atual == horario and not mensagem_enviada[horario]:
                    self.enviar_mensagem_especifica()
                    mensagem_enviada[horario] = True  # Marca que a mensagem foi enviada
                    
                if hora_atual == horario and not horarios_enviados[horario]:
                    data = self.obter_resultado()
                    print("Recebendo dados da API...")
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
                if not self.sinal:
                    self.generate_report(final_report=True)
                    ultimo_horario_envio = now.date()

            # Reseta os horários para o próximo dia
            if (now - timedelta(hours=3)).hour == 0 and (now - timedelta(hours=3)).minute == 0:
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
