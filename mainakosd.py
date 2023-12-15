import datetime
import requests
import telebot
import time
import json
import csv


class WebScraper:
    def __init__(self):
        # EDIT!
        self.game = "Football Studio"
        self.token = "5666220091:AAGCEWvSx_Y-qfqBl9u8vB-cbMCi_xjjuTw"
        self.chat_id = "-1001925542355"
        # self.chat_id = '-1001601471922' # TESTE
        self.url_API = "http://54.39.112.34:5000/api/football-studio"
        self.gales = 2
        self.protection = True
        self.link = "[Clique aqui!](https://go.flybet.com/C-BBSP6YOJA3)"
        self.plataforma = "Plataforma Correta"

        # MAYBE EDIT!
        self.win_results = 0
        self.empate_results = 0
        self.loss_results = 0
        self.max_hate = 0
        self.win_hate = 0

        # NO EDIT!
        self.count = 0
        self.analisar = True
        self.direction_color = "None"
        self.message_delete = False
        self.bot = telebot.TeleBot(token=self.token, parse_mode="MARKDOWN")
        self.check_date = None

    def restart(self):
        self.date_now = str(datetime.datetime.now().strftime("%d/%m/%Y"))
        if self.date_now != self.check_date:
            print("Reiniciando bot!")
            self.check_date = self.date_now

            self.bot.send_sticker(
                self.chat_id,
                sticker="CAACAgEAAxkBAAEBbJJjXNcB92-_4vp2v0B3Plp9FONrDwACvgEAAsFWwUVjxQN4wmmSBCoE",
            )
            self.results()

            # ZERA OS RESULTADOS
            self.win_results = 0
            self.loss_results = 0
            self.empate_results = 0
            self.max_hate = 0
            self.win_hate = 0
            time.sleep(10)

            self.bot.send_sticker(
                self.chat_id,
                sticker="CAACAgEAAxkBAAEBPQZi-ziImRgbjqbDkPduogMKzv0zFgACbAQAAl4ByUUIjW-sdJsr6CkE",
            )
            self.results()
            return True
        else:
            return False

    def results(self):
        if self.win_results + self.empate_results + self.loss_results != 0:
            a = (
                100
                / (self.win_results + self.empate_results + self.loss_results)
                * (self.win_results + self.empate_results)
            )
        else:
            a = 0
        self.win_hate = f"{a:,.2f}%"

        self.bot.send_message(
            chat_id=self.chat_id,
            text=(
                f"""
► PLACAR GERAL = ✅{self.win_results} | 🟡{self.empate_results} | 🚫{self.loss_results} 
► Assertividade = {self.win_hate}
► Quem fizer GREEN ✅ Manda um print para @Mestresuporte01
"""
            ),
        )
        return

    def alert_sinal(self):
        message_id = self.bot.send_message(
            self.chat_id,
            text="""
⚠️ ANALISANDO, FIQUE ATENTO!!!
""",
        ).message_id
        self.message_ids = message_id
        self.message_delete = True
        return

    def alert_gale(self):
        self.message_ids = self.bot.send_message(
            self.chat_id, text=f"""⚠️ Vamos para o {self.count}ª GALE"""
        ).message_id
        self.message_delete = True
        return

    def delete(self):
        if self.message_delete:
            self.bot.delete_message(chat_id=self.chat_id, message_id=self.message_ids)
            self.message_delete = False

    def send_sinal(self):
        self.analisar = False
        self.bot.send_message(
            chat_id=self.chat_id,
            text=(
                f"""
🎲 *ENTRADA CONFIRMADA!*
🎰 Apostar no {self.direction_color}
🟡 Proteger o empate (Meio) 
🔁 Fazer até {self.gales} gales
📲 *{self.plataforma}*: {self.link}
📱 *{self.game}* {self.link}
"""
            ),
            disable_web_page_preview=True,
        )
        return

    def martingale(self, result):
        if result == "WIN":
            print(f"WIN")
            self.win_results += 1
            self.max_hate += 1
            self.bot.send_message(chat_id=self.chat_id, text="✅✅✅ GREEN ✅✅✅")

        elif result == "LOSS":
            self.count += 1

            if self.count > self.gales:
                print(f"LOSS")
                self.loss_results += 1
                self.max_hate = 0
                self.bot.send_message(chat_id=self.chat_id, text="🚫🚫🚫 LOSS 🚫🚫🚫")
            else:
                print(f"Vamos para o {self.count}ª gale!")
                self.alert_gale()
                return

        elif result == "EMPATE":
            print(f"EMPATE")
            self.empate_results += 1
            self.max_hate += 1
            self.bot.send_message(chat_id=self.chat_id, text="✅✅✅ EMPATE ✅✅✅")

        self.count = 0
        self.analisar = True
        self.results()
        self.restart()
        return

    def check_results(self, results):
        if results == "V" and self.direction_color == "🔴":
            self.martingale("WIN")
            return
        elif results == "V" and self.direction_color == "🔵":
            self.martingale("LOSS")
            return

        if results == "A" and self.direction_color == "🔵":
            self.martingale("WIN")
            return
        elif results == "A" and self.direction_color == "🔴":
            self.martingale("LOSS")
            return

        if results == "E" and self.protection:
            self.martingale("EMPATE")
            return
        elif results == "E" and not self.protection:
            self.martingale("LOSS")
            return

    def start(self):
        check = []
        self.check_date = str(datetime.datetime.now().strftime("%d/%m/%Y"))
        while True:
            self.date_now = str(datetime.datetime.now().strftime("%d/%m/%Y"))

            results = []
            time.sleep(1)
            print("Iniciando requisição...")

            try:
                response = requests.get(self.url_API)
                response.raise_for_status()
            except requests.exceptions.RequestException as err:
                print("Error:", err)
                time.sleep(10)
                continue

            try:
                json_data = json.loads(response.text)
                for i in json_data["results"]:
                    results.append(i)
            except json.JSONDecodeError as e:
                print("Error decoding JSON", e)
                continue

            if check != results:
                check = results
                self.delete()
                self.estrategy(results)
        print("Requisição realizada com sucesso!")

    def estrategy(self, results):
        print("Entrou na estratégia!")
        print(results[0:10])

        if not self.analisar:
            self.check_results(results[0])
            return
        elif self.analisar:
            try:
                with open("estrategy.csv", newline="") as f:
                    reader = csv.reader(f)
                    ESTRATEGIAS = []

                    for row in reader:
                        string = str(row[0])

                        split_string = string.split("=")
                        values = list(split_string[0])
                        values.reverse()
                        dictionary = {"PADRAO": values, "ENTRADA": split_string[1]}
                        ESTRATEGIAS.append(dictionary)

                for i in ESTRATEGIAS:
                    if results[0 : len(i["PADRAO"])] == i["PADRAO"]:
                        print(f"\nRESULTADOS: {results[0:len(i['PADRAO'])]}")
                        print(
                            f"SINAL ENCONTRADO\nPADRÃO:{i['PADRAO']}\nENTRADA:{i['ENTRADA']}\n"
                        )

                        if i["ENTRADA"] == "A":
                            self.direction_color = "🔵"
                        elif i["ENTRADA"] == "V":
                            self.direction_color = "🔴"
                        elif i["ENTRADA"] == "E":
                            self.direction_color = "🟡"

                        self.send_sinal()
                        return

                for i in ESTRATEGIAS:
                    if (
                        results[0 : (len(i["PADRAO"]) - 1)]
                        == i["PADRAO"][1 : len(i["PADRAO"])]
                    ):
                        print("ALERTA DE POSSÍVEL SINAL")
                        self.alert_sinal()
                        return
            except FileNotFoundError as e:
                print("Error opening CSV file", e)
                return


scraper = WebScraper()
scraper.start()
